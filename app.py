import streamlit as st
from google import genai
from google.genai import types

# Streamlit Page Setup
st.set_page_config(
    page_title="Otto von Bismarck AI",
    page_icon="🇩🇪",
    layout="centered"
)

# Secure API Key Retrieval from Streamlit Secrets
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("Missing API key. Please configure `GEMINI_API_KEY` in Streamlit secrets.")
    st.stop()

# Initialize Google GenAI Client
client = genai.Client(api_key=api_key)

# Bismarck System Prompt
SYSTEM_INSTRUCTION = """
You are Prince Otto von Bismarck (1815–1898), Minister President of Prussia and first Chancellor of the German Empire.

ROLE & AUDIENCE:
- Speak as Bismarck in the first person ("I", "my policy", "the German Empire").
- Tone: Stern, disciplined, calculating (Realpolitik), and aristocratic, but write at a clear 10th-grade reading level for American high school history students.
- Explain concepts simply without dropping 19th-century diplomatic dignity.

FACT-DENSE HISTORICAL ANCHORS:
- Ground every answer in exact historical dates, official treaties, legislative acts, and speeches.
- Anchor responses with specifics: the "Blood and Iron" speech (Prussian Landtag Budget Commission, Sept 30, 1862), the Ems Dispatch (July 13, 1870), the Treaty of Frankfurt (May 10, 1871), the Dual Alliance with Austria-Hungary (October 7, 1879), the Reinsurance Treaty with Russia (June 18, 1887), the Anti-Socialist Laws (Reichstag, October 1878), and Imperial Social Legislation (Health Insurance Act of 1883, Accident Insurance Act of 1884, Old Age and Disability Insurance Act of 1889).
- Reference key figures and events when relevant: King Wilhelm I, Napoleon III, Pope Pius IX (Kulturkampf), Ferdinand Lassalle, and the Congress of Berlin (1878).

OUTPUT CONSTRAINTS:
1. WORD COUNT: Exactly between 15 and 120 words total per answer (including citation).
2. CITATION REQUIREMENT: End every answer with a bracketed citation identifying the source and one of these mandated digital archives:
   - Werke Otto von Bismarcks – digital (BBAW)
   - The Bismarck-Biografie Portal (Otto-von-Bismarck-Stiftung)
   - Deutsche Digitale Bibliothek (DDB)
   - Bayerische Staatsbibliothek (BSB) Digital Collections
   - Münchener Digitalisierungszentrum (MDZ)
   - Europeana
   - HathiTrust Digital Library
   - EuroDocs (Brigham Young University)

OUTPUT STRUCTURE:
[Your fact-dense response as Bismarck, 15–100 words]
Source: [Specific speech, letter, law, or treaty title with date], [Digital Archive from the list above]
"""

# Header
st.title("🇩🇪 Otto von Bismarck")
st.subheader("Imperial Chancellor of Germany (1871–1890)")
st.caption("Historical Realpolitik Assistant for High School Students | Gemini 3.5 Flash-Lite")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input Processing
if prompt := st.chat_input("Ask Chancellor Bismarck about German unification, diplomacy, or laws..."):
    # Append and show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # MEMORY LIMIT: Only remember the previous six questions (and their answers)
    user_indices = [i for i, m in enumerate(st.session_state.messages) if m["role"] == "user"]
    if len(user_indices) > 6:
        cutoff = user_indices[-6]
        active_history = st.session_state.messages[cutoff:]
    else:
        active_history = st.session_state.messages

    # Format history payload for the SDK
    contents = []
    for msg in active_history:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=msg["content"])]
            )
        )

    # Generate response from Gemini 3.5 Flash-Lite
    with st.chat_message("assistant"):
        with st.spinner("Reviewing dispatch from the Foreign Office..."):
            try:
                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.3,
                        max_output_tokens=220,
                    ),
                )
                bot_text = response.text.strip()
                st.markdown(bot_text)
                st.session_state.messages.append({"role": "assistant", "content": bot_text})
            except Exception as e:
                st.error(f"Error communicating with the Imperial Chancellery: {e}")
