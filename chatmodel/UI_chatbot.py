from langchain_mistralai import ChatMistralAI
from dotenv import load_dotenv
load_dotenv()
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import streamlit as st

# ----------------------------------------------------------------------------
# CORE CHATBOT  (same functions as chatbot.py — nothing added)
#   - Mistral model (mistral-small-2506, temperature 0.9)
#   - SystemMessage sets the tone of the bot
#   - messages list = short-term memory (Human / AI messages)
#   - model.invoke(messages) generates the reply with full context
# ----------------------------------------------------------------------------
model = ChatMistralAI(model="mistral-small-2506", temperature=0.9)

# Conversation memory lives in the session so it survives reruns
if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(content="you are a funny ai agent "),  # set the tone of the bot
    ]

# ----------------------------------------------------------------------------
# PAGE + STYLE  (sporty, dark, bold — built to NOT look like a generic AI app)
# ----------------------------------------------------------------------------
st.set_page_config(page_title="MOMENTUM", page_icon="⚡", layout="wide")

# st.html() injects raw HTML/CSS inline without sanitizing it, so <style>,
# <link> and class="" all survive (st.markdown strips those out).
st.html(
    """
    <link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;600;700;800;900&display=swap" rel="stylesheet">
    <style>
      #MainMenu, header[data-testid="stHeader"], footer {visibility: hidden;}
      [data-testid="stToolbar"] {display: none;}
      [data-testid="stDecoration"] {display: none;}

      :root{
        --bg:#070809;
        --ink:#f4f6f8;
        --muted:#8b94a0;
        --c1:#22d3ee;
        --c2:#a855f7;
        --c3:#ec4899;
        --c4:#f97316;
      }

      html, body, [data-testid="stAppViewContainer"]{
        font-family: 'Hanken Grotesk', sans-serif;
        background:
          radial-gradient(900px 500px at 85% -5%, rgba(34,211,238,.18), transparent 60%),
          radial-gradient(800px 600px at 0% 110%, rgba(236,72,153,.16), transparent 55%),
          var(--bg);
        color: var(--ink);
      }
      [data-testid="stAppViewContainer"] .block-container{
        max-width: 980px;
        padding-top: 2.2rem;
        padding-bottom: 9rem;
      }

      .badge{
        display:inline-flex; align-items:center; gap:.5rem;
        margin: 0 auto 1.4rem; padding:.42rem 1rem;
        font-size:.82rem; font-weight:700; letter-spacing:.02em;
        color:#cdd4dd;
        background: rgba(255,255,255,.05);
        border:1px solid rgba(255,255,255,.12);
        border-radius:999px;
        backdrop-filter: blur(6px);
      }
      .badge .dot{
        width:.5rem; height:.5rem; border-radius:50%;
        background: var(--c1);
        box-shadow: 0 0 12px var(--c1);
      }
      .hero{ text-align:center; margin: .4rem 0 1.2rem; }
      .hero h1{
        font-weight:900;
        font-size: clamp(2.8rem, 7vw, 5.2rem);
        line-height:.95;
        letter-spacing:-.03em;
        margin:0;
        text-transform: lowercase;
      }
      .hero .grad{
        background: linear-gradient(100deg, var(--c1), var(--c2) 38%, var(--c3) 66%, var(--c4));
        -webkit-background-clip:text; background-clip:text;
        -webkit-text-fill-color:transparent;
      }
      .hero p{
        max-width: 540px; margin: 1.3rem auto 0;
        color: var(--muted); font-size:1.05rem; font-weight:500; line-height:1.5;
      }

      .row{ display:flex; margin:.7rem 0; }
      .row.me{ justify-content:flex-end; }
      .who{
        font-size:.7rem; font-weight:800; letter-spacing:.14em;
        text-transform:uppercase; margin:0 .25rem .3rem; color:var(--muted);
      }
      .bubble{
        max-width: 78%; padding:.85rem 1.15rem; border-radius:18px;
        font-size:1rem; font-weight:500; line-height:1.5;
        border:1px solid rgba(255,255,255,.08);
      }
      .me .bubble{
        background: linear-gradient(120deg, var(--c1), var(--c2));
        color:#06080a; font-weight:700;
        border:none; border-bottom-right-radius:6px;
      }
      .bot .bubble{
        background: rgba(255,255,255,.045);
        color: var(--ink);
        border-bottom-left-radius:6px;
      }
      .stack{ display:flex; flex-direction:column; }
      .me .stack{ align-items:flex-end; }

      [data-testid="stChatInput"]{
        background: rgba(15,18,22,.85);
        border:1px solid rgba(255,255,255,.12);
        border-radius:16px;
        backdrop-filter: blur(10px);
      }
      [data-testid="stChatInput"] textarea{ color:var(--ink) !important; }
      [data-testid="stChatInput"] textarea::placeholder{ color:#6b7280 !important; }
      [data-testid="stBottomBlockContainer"]{ background: transparent; }

      .pitch{
        height:3px; width:120px; margin:1.6rem auto 2.2rem; border-radius:3px;
        background: linear-gradient(90deg, var(--c1), var(--c2), var(--c3), var(--c4));
      }
    </style>
    """
)

# ----------------------------------------------------------------------------
# HERO
# ----------------------------------------------------------------------------
st.html(
    """
    <div style="text-align:center;">
      <span class="badge"><span class="dot"></span>Powered by your home team · live now</span>
    </div>
    <div class="hero">
      <h1>conversations<br><span class="grad">without the bench</span></h1>
      <p>Step into the arena and talk it out. Quick on its feet, never out of breath 
         Your sideline companion for every play.</p>
    </div>
    <div class="pitch"></div>
    """
)

# ----------------------------------------------------------------------------
# RENDER THE CONVERSATION (skip the SystemMessage)
# ----------------------------------------------------------------------------
import html as _html

for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        side, who = "me", "You"
    elif isinstance(msg, AIMessage):
        side, who = "bot", "Momentum"
    else:
        continue  # SystemMessage stays hidden
    body = _html.escape(msg.content).replace("\n", "<br>")
    st.html(
        f'<div class="row {side}"><div class="stack">'
        f'<div class="who">{who}</div>'
        f'<div class="bubble">{body}</div>'
        f"</div></div>"
    )

# ----------------------------------------------------------------------------
# INPUT  ->  same invoke flow as chatbot.py (append, invoke, append)
# ----------------------------------------------------------------------------
prompt = st.chat_input("Pass the ball — type your message…")
if prompt:
    st.session_state.messages.append(HumanMessage(content=prompt))
    response = model.invoke(st.session_state.messages)
    st.session_state.messages.append(AIMessage(content=response.content))
    st.rerun()
