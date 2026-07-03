# ──────────────────────────────────────────────────────────────────────────
#  ReelDossier · Structured Film Intelligence
#  A dark, editorial-magazine front end for the LangChain movie extractor.
#
#  Core logic is unchanged from 4_prompt_template.py:
#    • ChatMistralAI (mistral-small-2506)
#    • A ChatPromptTemplate turns a raw paragraph into structured fields
#  The only upgrade: we ask the model for JSON so the result can be rendered
#  as a clean "dossier" instead of a wall of text.
# ──────────────────────────────────────────────────────────────────────────
import json
import re
import html as _html

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate

st.set_page_config(page_title="ReelDossier · Film Intelligence", page_icon="🎞", layout="wide")

# ──────────────────────────────────────────────────────────────────────────
#  MODEL + PROMPT  (same task as the original, now returning JSON)
# ──────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_model():
    return ChatMistralAI(model="mistral-small-2506", temperature=0.15)


PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     """You are an expert film data-extraction assistant. Read the paragraph and \
extract key information. Return ONLY a single valid minified JSON object — no \
markdown fences, no commentary, no intro or outro text.

Use EXACTLY these keys:
"movie_name"     : string
"release_year"   : string
"director"       : string
"cast"           : array of strings
"genre"          : array of strings
"key_themes"     : array of strings
"imdb_rating"    : string   (e.g. "8.6/10" or "Not mentioned")
"quick_summary"  : string   (a concise 1-2 sentence summary of plot and reception)

Only use what is present in the text. If a scalar value is missing write \
"Not mentioned"; if a list value is missing use an empty array [].

### Example ###
Paragraph: "The Matrix is a 1999 science fiction action film written and directed \
by the Wachowskis. It stars Keanu Reeves, Laurence Fishburne, and Carrie-Anne Moss. \
It depicts a dystopian future in which humanity is unknowingly trapped inside a \
simulated reality."
JSON: {{"movie_name":"The Matrix","release_year":"1999","director":"The Wachowskis",\
"cast":["Keanu Reeves","Laurence Fishburne","Carrie-Anne Moss"],\
"genre":["Science Fiction","Action"],\
"key_themes":["Dystopian future","Simulated reality","AI control"],\
"imdb_rating":"Not mentioned",\
"quick_summary":"A 1999 sci-fi action film by the Wachowskis starring Keanu Reeves, \
where humanity is trapped inside a simulated reality."}}"""),
    ("human",
     """### Task ###
Paragraph: {paragraph}
JSON:"""),
])


def _coerce_json(raw: str) -> dict:
    """Pull a JSON object out of the model output, tolerating stray fences/text."""
    text = raw.strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.MULTILINE).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    # Last resort: parse "Field: value" lines from a plain-text response.
    fields = {}
    keymap = {
        "movie name": "movie_name", "release year": "release_year",
        "director": "director", "cast": "cast", "genre": "genre",
        "key themes": "key_themes", "imdb rating": "imdb_rating",
        "quick summary": "quick_summary",
    }
    for line in text.splitlines():
        if ":" in line:
            label, _, value = line.partition(":")
            key = keymap.get(label.strip().lower())
            if key:
                fields[key] = value.strip()
    return fields


def extract(paragraph: str) -> dict:
    final_prompt = PROMPT.invoke({"paragraph": paragraph})
    response = get_model().invoke(final_prompt)
    return _coerce_json(response.content)


# ──────────────────────────────────────────────────────────────────────────
#  STYLE  (four typefaces, cinema-noir dark palette)
#    Playfair Display  → big Didone display + film title
#    Cormorant Garamond → italic accents + the summary blockquote
#    Inter             → body copy, sub-text, buttons
#    DM Mono           → eyebrows, field labels, the technical detailing
# ──────────────────────────────────────────────────────────────────────────
st.html("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,700;0,800;0,900;1,500;1,600;1,700&family=Cormorant+Garamond:ital,wght@0,500;0,600;1,400;1,500;1,600&family=Inter:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  #MainMenu, header[data-testid="stHeader"], footer {visibility:hidden;}
  [data-testid="stToolbar"], [data-testid="stDecoration"] {display:none;}

  :root{
    --bg:#0c0a0e;
    --bg2:#120e16;
    --ink:#f2eadf;          /* warm cream */
    --muted:#9a8f99;        /* dusty mauve-grey */
    --faint:#6a6270;
    --line:rgba(242,234,223,.12);
    --coral:#e08763;        /* terracotta — the lead accent (NOT the ref's gold) */
    --coral-soft:#f0b89a;
    --rose:#d98c86;         /* dusty rose */
    --jade:#8fbfa9;         /* soft sage/jade — the cool counterpoint */
    --panel:rgba(242,234,223,.035);
  }

  html, body, [data-testid="stAppViewContainer"]{
    font-family:'Inter',sans-serif;
    color:var(--ink);
    background:
      radial-gradient(1100px 620px at 88% -8%, rgba(224,135,99,.16), transparent 58%),
      radial-gradient(900px 680px at -8% 108%, rgba(143,191,169,.12), transparent 55%),
      var(--bg);
  }
  [data-testid="stAppViewContainer"] .block-container{
    max-width:1140px;
    padding-top:1.4rem;
    padding-bottom:7rem;
  }

  /* ── top bar ─────────────────────────────────────────────── */
  .topbar{
    display:flex; align-items:center; justify-content:space-between;
    padding:.2rem .1rem 1.4rem;
    border-bottom:1px solid var(--line);
    margin-bottom:2.6rem;
  }
  .brand{
    font-family:'Playfair Display',serif; font-weight:800;
    font-size:1.45rem; letter-spacing:.01em; color:var(--ink);
  }
  .brand b{ color:var(--coral); }
  .topmeta{
    font-family:'DM Mono',monospace; font-size:.72rem; letter-spacing:.18em;
    text-transform:uppercase; color:var(--faint);
  }

  /* ── hero ────────────────────────────────────────────────── */
  .hero{
    display:grid; grid-template-columns:1.15fr .85fr; gap:2.4rem;
    align-items:center; margin-bottom:2.2rem;
  }
  .eyebrow{
    font-family:'DM Mono',monospace; font-size:.74rem; letter-spacing:.32em;
    text-transform:uppercase; color:var(--coral); margin-bottom:1.5rem;
    display:flex; align-items:center; gap:.8rem;
  }
  .eyebrow::before{ content:""; width:34px; height:1px; background:var(--coral); display:inline-block; }
  .display{
    font-family:'Playfair Display',serif; font-weight:800;
    font-size:clamp(2.9rem,6vw,4.9rem); line-height:.98; letter-spacing:-.02em;
    margin:0; color:var(--ink);
  }
  .display .it{
    font-style:italic; font-weight:600;
    background:linear-gradient(96deg,var(--coral-soft),var(--coral) 45%,var(--rose));
    -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent;
  }
  .lede{
    font-family:'Inter',sans-serif; font-size:1.04rem; line-height:1.65;
    color:var(--muted); max-width:30rem; margin:1.7rem 0 0; font-weight:400;
  }
  .lede em{ color:var(--ink); font-style:normal; font-weight:600; }

  /* right-hand "film still" art panel */
  .still{
    position:relative; border:1px solid var(--line); border-radius:14px;
    background:
      radial-gradient(120% 80% at 70% 0%, rgba(224,135,99,.18), transparent 60%),
      linear-gradient(160deg,#181019,#0e0b12);
    aspect-ratio:4/5; overflow:hidden; padding:1.4rem;
    display:flex; flex-direction:column; justify-content:space-between;
  }
  .still .perf{
    position:absolute; top:0; bottom:0; width:18px;
    background-image:repeating-linear-gradient(to bottom,transparent 0 14px,rgba(242,234,223,.14) 14px 24px);
  }
  .still .perf.l{ left:9px; } .still .perf.r{ right:9px; }
  .still .ghost{
    position:absolute; right:-2.4rem; bottom:-3.6rem;
    font-family:'Playfair Display',serif; font-weight:900; font-style:italic;
    font-size:13rem; line-height:.8; color:rgba(242,234,223,.05); pointer-events:none;
  }
  .still .tag{
    font-family:'DM Mono',monospace; font-size:.68rem; letter-spacing:.22em;
    text-transform:uppercase; color:var(--jade); position:relative;
  }
  .still .pull{
    position:relative; font-family:'Cormorant Garamond',serif; font-style:italic;
    font-weight:500; font-size:1.75rem; line-height:1.25; color:var(--ink);
  }
  .still .pull span{ color:var(--coral-soft); }

  /* ── working console ─────────────────────────────────────── */
  .section-label{
    font-family:'DM Mono',monospace; font-size:.74rem; letter-spacing:.26em;
    text-transform:uppercase; color:var(--faint);
    display:flex; align-items:center; gap:1rem; margin:.4rem 0 1rem;
  }
  .section-label::after{ content:""; flex:1; height:1px; background:var(--line); }

  /* text area */
  [data-testid="stTextArea"] label{ display:none; }
  [data-testid="stTextArea"] textarea{
    background:var(--panel) !important;
    color:var(--ink) !important;
    border:1px solid var(--line) !important;
    border-radius:13px !important;
    font-family:'Cormorant Garamond',serif !important;
    font-size:1.32rem !important; line-height:1.5 !important;
    padding:1.15rem 1.3rem !important;
    transition:border-color .2s ease, box-shadow .2s ease;
  }
  [data-testid="stTextArea"] textarea:focus{
    border-color:rgba(224,135,99,.6) !important;
    box-shadow:0 0 0 3px rgba(224,135,99,.12) !important;
  }
  [data-testid="stTextArea"] textarea::placeholder{ color:var(--faint) !important; font-style:italic; }

  /* buttons — default = editorial ghost */
  .stButton > button{
    width:100%;
    background:transparent; color:var(--ink);
    border:1px solid var(--line); border-radius:11px;
    font-family:'DM Mono',monospace; font-size:.76rem; font-weight:500;
    letter-spacing:.14em; text-transform:uppercase;
    padding:.62rem .8rem; transition:all .18s ease;
  }
  .stButton > button:hover{
    border-color:var(--coral); color:var(--coral-soft);
    background:rgba(224,135,99,.06);
  }
  /* primary CTA */
  .stButton > button[kind="primary"],
  [data-testid="stBaseButton-primary"]{
    background:linear-gradient(100deg,var(--coral),var(--rose));
    color:#1a0f0b !important; border:none; font-weight:500;
    box-shadow:0 10px 30px -10px rgba(224,135,99,.55);
  }
  .stButton > button[kind="primary"]:hover,
  [data-testid="stBaseButton-primary"]:hover{
    filter:brightness(1.07); transform:translateY(-1px);
  }

  /* ── dossier (results) ───────────────────────────────────── */
  .dossier{
    border:1px solid var(--line); border-radius:16px;
    background:linear-gradient(168deg,rgba(242,234,223,.05),rgba(242,234,223,.015));
    padding:2.2rem 2.3rem; margin-top:.4rem; position:relative; overflow:hidden;
  }
  .dossier::before{
    content:""; position:absolute; left:0; top:0; bottom:0; width:3px;
    background:linear-gradient(var(--coral),var(--jade));
  }
  .dossier .kicker{
    font-family:'DM Mono',monospace; font-size:.7rem; letter-spacing:.28em;
    text-transform:uppercase; color:var(--jade); margin-bottom:.7rem;
  }
  .dossier .title-row{
    display:flex; align-items:baseline; gap:1rem; flex-wrap:wrap;
    border-bottom:1px solid var(--line); padding-bottom:1.3rem; margin-bottom:1.4rem;
  }
  .dossier h2{
    font-family:'Playfair Display',serif; font-weight:800;
    font-size:clamp(2rem,4vw,3rem); line-height:1.02; letter-spacing:-.02em;
    margin:0; color:var(--ink);
  }
  .dossier .year{
    font-family:'Cormorant Garamond',serif; font-style:italic; font-size:1.6rem;
    color:var(--muted);
  }
  .chips{ display:flex; flex-wrap:wrap; gap:.5rem; margin-left:auto; }
  .chip{
    font-family:'DM Mono',monospace; font-size:.68rem; letter-spacing:.1em;
    text-transform:uppercase; color:var(--coral-soft);
    border:1px solid rgba(224,135,99,.35); border-radius:999px;
    padding:.34rem .8rem; background:rgba(224,135,99,.06);
  }
  .rating{
    display:flex; align-items:baseline; gap:.35rem;
    font-family:'DM Mono',monospace; color:var(--jade);
    border:1px solid rgba(143,191,169,.35); background:rgba(143,191,169,.07);
    border-radius:999px; padding:.3rem .85rem;
  }
  .rating b{ font-size:1rem; letter-spacing:.02em; }
  .rating span{ font-size:.66rem; letter-spacing:.12em; text-transform:uppercase; color:var(--muted); }

  .grid{ display:grid; grid-template-columns:1fr 1fr; gap:1.4rem 2.4rem; margin-bottom:1.6rem; }
  .field .lab{
    font-family:'DM Mono',monospace; font-size:.68rem; letter-spacing:.22em;
    text-transform:uppercase; color:var(--faint); margin-bottom:.45rem;
  }
  .field .val{
    font-family:'Playfair Display',serif; font-size:1.18rem; line-height:1.4; color:var(--ink);
  }
  .field .val.muted{ font-family:'Inter'; font-size:.95rem; color:var(--faint); font-style:italic; }
  .tags{ display:flex; flex-wrap:wrap; gap:.45rem; }
  .tag{
    font-family:'Inter',sans-serif; font-size:.82rem; color:var(--ink);
    border:1px solid var(--line); border-radius:8px; padding:.28rem .7rem;
    background:var(--panel);
  }
  .tag::before{ content:"# "; color:var(--jade); }

  .summary{
    border-top:1px solid var(--line); padding-top:1.5rem; margin-top:.4rem;
    position:relative; padding-left:1.4rem;
  }
  .summary::before{
    content:"“"; position:absolute; left:-.2rem; top:.3rem;
    font-family:'Playfair Display',serif; font-size:3.4rem; line-height:1;
    color:rgba(224,135,99,.35);
  }
  .summary .lab{
    font-family:'DM Mono',monospace; font-size:.68rem; letter-spacing:.22em;
    text-transform:uppercase; color:var(--faint); margin-bottom:.5rem;
  }
  .summary p{
    font-family:'Cormorant Garamond',serif; font-style:italic; font-weight:500;
    font-size:1.5rem; line-height:1.5; color:var(--ink); margin:0;
  }

  /* empty state */
  .empty{
    border:1px dashed var(--line); border-radius:16px;
    padding:2.6rem 2rem; text-align:center; color:var(--muted);
  }
  .empty h3{
    font-family:'Cormorant Garamond',serif; font-style:italic; font-weight:500;
    font-size:1.7rem; color:var(--ink); margin:0 0 .4rem;
  }
  .empty p{ font-family:'Inter'; font-size:.95rem; margin:0; color:var(--faint); }

  /* spacing tweaks for streamlit blocks */
  [data-testid="stExpander"]{ border:none !important; background:transparent !important; }
  [data-testid="stExpander"] summary{
    font-family:'DM Mono',monospace !important; font-size:.72rem !important;
    letter-spacing:.2em; text-transform:uppercase; color:var(--faint) !important;
  }
  @media (max-width:820px){
    .hero{ grid-template-columns:1fr; } .still{ display:none; }
    .grid{ grid-template-columns:1fr; }
  }
</style>
""")

# ──────────────────────────────────────────────────────────────────────────
#  TOP BAR + HERO
# ──────────────────────────────────────────────────────────────────────────
st.html("""
<div class="topbar">
  <div class="brand">Reel<b>Dossier</b></div>
  <div class="topmeta">Structured Film Intelligence · v1.0</div>
</div>

<div class="hero">
  <div>
    <div class="eyebrow">Paragraph in · Dossier out</div>
    <h1 class="display">We Read<br>The <span class="it">Reels</span><br>For You.</h1>
    <p class="lede">Hand over a messy paragraph about any film. ReelDossier reads it like a
       critic and returns <em>clean, structured intelligence</em> — cast, crew, themes,
       rating and a sharp little summary.</p>
  </div>
  <div class="still">
    <div class="perf l"></div><div class="perf r"></div>
    <div class="ghost">36</div>
    <div class="tag">Reel · 36 · take 01</div>
    <div class="pull">From a paragraph<br>to a <span>proper file.</span></div>
    <div class="tag" style="text-align:right;color:var(--coral-soft)">↳ powered by langchain × mistral</div>
  </div>
</div>
""")

# ──────────────────────────────────────────────────────────────────────────
#  STATE + EXAMPLES
# ──────────────────────────────────────────────────────────────────────────
EXAMPLES = {
    "Interstellar": (
        "Interstellar is a visually stunning science fiction epic directed by Christopher "
        "Nolan. Released in 2014, the film stars Matthew McConaughey, Anne Hathaway, Jessica "
        "Chastain, and Michael Caine. The story revolves around a group of astronauts who "
        "travel through a wormhole near Saturn in search of a new home for humanity as Earth "
        "faces environmental collapse. The movie was widely appreciated for its emotional "
        "depth, scientific accuracy, and Hans Zimmer's powerful soundtrack. It holds a rating "
        "of 8.6 on IMDb and is often considered one of the greatest sci-fi films of the 21st century."
    ),
    "Parasite": (
        "Parasite is a 2019 South Korean dark comedy thriller directed by Bong Joon-ho, "
        "starring Song Kang-ho, Lee Sun-kyun and Cho Yeo-jeong. It follows the impoverished "
        "Kim family as they scheme their way into the household of the wealthy Park family, "
        "exposing the brutal gap between rich and poor. The film won the Academy Award for "
        "Best Picture and carries an IMDb rating of 8.5."
    ),
    "Spirited Away": (
        "Spirited Away is a 2001 Japanese animated fantasy film written and directed by Hayao "
        "Miyazaki. It tells the story of Chihiro, a young girl who wanders into a spirit world "
        "and must work in a bathhouse to free her parents and find her way home. Praised for "
        "its imaginative world-building and themes of courage and identity, it holds an IMDb "
        "rating of 8.6."
    ),
}

if "paragraph" not in st.session_state:
    st.session_state.paragraph = ""
if "result" not in st.session_state:
    st.session_state.result = None
if "error" not in st.session_state:
    st.session_state.error = None


def _load_example(name: str):
    st.session_state.paragraph = EXAMPLES[name]
    st.session_state.result = None
    st.session_state.error = None


def _clear():
    st.session_state.paragraph = ""
    st.session_state.result = None
    st.session_state.error = None


# ──────────────────────────────────────────────────────────────────────────
#  CONSOLE  (real Streamlit widgets, styled above)
# ──────────────────────────────────────────────────────────────────────────
st.html('<div class="section-label">01 · Paste the paragraph</div>')

st.text_area(
    "paragraph", key="paragraph", height=170, label_visibility="collapsed",
    placeholder="Paste a raw paragraph about a movie — the messier the better…",
)

# example chips
st.html('<div class="section-label" style="margin-top:.2rem">Or try a sample reel</div>')
ex_cols = st.columns(len(EXAMPLES) + 1)
for col, name in zip(ex_cols, EXAMPLES):
    col.button(name, key=f"ex_{name}", on_click=_load_example, args=(name,))
ex_cols[-1].button("Clear", key="clear", on_click=_clear)

# action row
act1, act2 = st.columns([3, 1])
run = act1.button("Extract the dossier  ⟶", type="primary", key="run")
act2.button("Reset", key="reset", on_click=_clear)

if run:
    text = st.session_state.paragraph.strip()
    if not text:
        st.session_state.error = "Add a paragraph first — even a few sentences will do."
        st.session_state.result = None
    else:
        st.session_state.error = None
        with st.spinner("Reading the reel — extracting structured intelligence…"):
            try:
                st.session_state.result = extract(text)
            except Exception as exc:  # surface API / parsing issues plainly
                st.session_state.error = f"Extraction failed: {exc}"
                st.session_state.result = None

# ──────────────────────────────────────────────────────────────────────────
#  RESULTS
# ──────────────────────────────────────────────────────────────────────────
st.html('<div class="section-label" style="margin-top:2.4rem">02 · The dossier</div>')


def _as_list(value):
    """Normalise cast/genre/theme fields to a clean list, dropping 'Not mentioned'."""
    if value is None:
        return []
    if isinstance(value, list):
        items = [str(v).strip() for v in value]
    else:
        s = str(value).strip()
        if not s:
            return []
        items = [p.strip() for p in re.split(r"[,/;]", s)]
    return [i for i in items if i and i.lower() != "not mentioned"]


def _scalar(value, default="Not mentioned"):
    if value is None:
        return default
    s = str(value).strip()
    return s if s else default


def _esc(value):
    return _html.escape(str(value))


def render_dossier(data: dict):
    title = _scalar(data.get("movie_name"), "Untitled")
    year = _scalar(data.get("release_year"), "")
    director = _scalar(data.get("director"))
    cast = _as_list(data.get("cast"))
    genres = _as_list(data.get("genre"))
    themes = _as_list(data.get("key_themes"))
    rating_raw = _scalar(data.get("imdb_rating"), "")
    summary = _scalar(data.get("quick_summary"), "No summary available.")

    # header chips: genres + rating badge
    chips = "".join(f'<span class="chip">{_esc(g)}</span>' for g in genres[:4])
    rating_html = ""
    m = re.search(r"\d+(?:\.\d+)?", rating_raw)
    if m:
        rating_html = (
            f'<div class="rating"><b>{_esc(m.group(0))}</b>'
            f'<span>/10 · imdb</span></div>'
        )

    year_html = f'<span class="year">{_esc(year)}</span>' if year else ""

    # director value
    director_html = (
        f'<div class="val">{_esc(director)}</div>' if director.lower() != "not mentioned"
        else '<div class="val muted">Not mentioned</div>'
    )
    # cast value
    if cast:
        cast_html = '<div class="val">' + ", ".join(_esc(c) for c in cast) + "</div>"
    else:
        cast_html = '<div class="val muted">Not mentioned</div>'
    # theme tags
    if themes:
        theme_html = '<div class="tags">' + "".join(
            f'<span class="tag">{_esc(t)}</span>' for t in themes
        ) + "</div>"
    else:
        theme_html = '<div class="val muted">Not mentioned</div>'

    html_out = f"""
    <div class="dossier">
      <div class="kicker">Extraction complete · structured dossier</div>
      <div class="title-row">
        <h2>{_esc(title)}</h2>
        {year_html}
        <div class="chips">{chips}{rating_html}</div>
      </div>
      <div class="grid">
        <div class="field"><div class="lab">Director</div>{director_html}</div>
        <div class="field"><div class="lab">Principal Cast</div>{cast_html}</div>
        <div class="field" style="grid-column:1 / -1"><div class="lab">Key Themes</div>{theme_html}</div>
      </div>
      <div class="summary">
        <div class="lab">Quick Summary</div>
        <p>{_esc(summary)}</p>
      </div>
    </div>
    """
    st.html(html_out)


if st.session_state.error:
    st.html(
        f'<div class="empty" style="border-color:rgba(217,140,134,.5);color:var(--rose)">'
        f'<h3>Hold on.</h3><p>{_esc(st.session_state.error)}</p></div>'
    )
elif st.session_state.result:
    render_dossier(st.session_state.result)
    with st.expander("View raw JSON"):
        st.json(st.session_state.result)
else:
    st.html(
        '<div class="empty"><h3>Your dossier will appear here.</h3>'
        '<p>Paste a paragraph above (or load a sample) and hit Extract.</p></div>'
    )
