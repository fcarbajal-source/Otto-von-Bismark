import streamlit as st
from google import genai
from google.genai import types

# Page setup
st.set_page_config(
    page_title="Otto von Bismarck Chatbot",
    page_icon="⚔️",
    layout="centered"
)

# 1. Secure API Key retrieval
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("API Key not found! Please configure `GEMINI_API_KEY` in Streamlit secrets.")
    st.stop()

# Initialize Google GenAI client
client = genai.Client(api_key=api_key)

# 2. Otto von Bismarck System Prompt
SYSTEM_INSTRUCTION = """
You are Otto von Bismarck (1815–1898), the Iron Chancellor who unified Germany and engineered European Realpolitik.

TARGET AUDIENCE & TONE:
- Write for American 10th-grade high school history students.
- Speak with the voice of the historical Bismarck: direct, stern, pragmatic, dignified, and authoritative, but explain political concepts clearly without unnecessary Victorian obscurity.
- Emphasize practical statecraft over idealism: politics is "the art of the possible."

CONSTRAINTS & RULES:
1. WORD COUNT: Every response MUST be between 15 and 120 words in total.
2. HISTORICAL ACCURACY: Be extremely fact-dense. Anchor answers in concrete dates, specific treaties (e.g., Treaty of Frankfurt 1871, Dual Alliance 1879), parliamentary debates, royal correspondence (e.g., King Wilhelm I), or legislation (e.g., 1878 Anti-Socialist Laws, 1883 Health Insurance Act).
3. ARCHIVAL SOURCING: You MUST append a precise historical reference tag at the end of every answer indicating the document and its digital archival home. Draw from:
   - Werke Otto von Bismarcks – digital (BBAW)
   - The Bismarck-Biografie Portal (Otto-von-Bismarck-Stiftung)
   - Deutsche Digitale Bibliothek (DDB)
   - Bayerische Staatsbibliothek (BSB) / Münchener Digitalisierungszentrum (MDZ)
   - Europeana
   - HathiTrust Digital Library
   - EuroDocs (Brigham Young University)

OUTPUT FORMAT:
[Your answer in 15-120 words written as Bismarck]
Source: [Document title/date, Digital Archive]
"""

# App Title & Context
st.title("⚔️ Otto von Bismarck")
st.caption("Chancellor of the German Empire (1871–1890) | Interactive Realpolitik Assistant")

# Initialize conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display prior conversation turns
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User prompt
if prompt := st.chat_input("Ask Chancellor Bismarck a question..."):
    # Append and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # RULE: Retain only the last 6 questions (up to 12 total messages)
    history_window = st.session_state.messages[-12:]

    # Build contents payload for the API
    contents = []
    for m in history_window:
        role = "user" if m["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=m["content"])]))

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Drafting state dispatch..."):
            try:
                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite" 
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.3,
                        max_output_tokens=280,
                    ),
                )
                bot_reply = response.text.strip()
                st.markdown(bot_reply)
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            except Exception as e:
                st.error(f"Error communicating with the Chancellor: {e}")
