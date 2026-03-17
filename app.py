import os
import streamlit as st
from anthropic import Anthropic
from dotenv import load_dotenv
from pypdf import PdfReader

# -----------------------------
# LOAD API KEY
# -----------------------------
load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

BASE_PATH = "/Users/shaivibhandekar/Desktop/Pradeepthi Medical Agent"

# -----------------------------
# READ PDF
# -----------------------------
def read_pdf(file_path):
    text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() or ""
    except:
        pass
    return text

# -----------------------------
# READ ALL FILES
# -----------------------------
def read_all_files():
    matched_text = ""

    for root, dirs, files in os.walk(BASE_PATH):
        for file in files:
            file_path = os.path.join(root, file)

            try:
                if file.lower().endswith(".pdf"):
                    text = read_pdf(file_path)
                elif file.lower().endswith((".txt", ".csv")):
                    with open(file_path, "r", errors="ignore") as f:
                        text = f.read()
                else:
                    continue

                if text:
                    matched_text += f"\n\n--- {file} ---\n"
                    matched_text += text[:1200]

            except:
                continue

    return matched_text

# -----------------------------
# STREAMLIT UI
# -----------------------------
st.set_page_config(page_title="Medical AI Agent", layout="wide")

st.title("🧠 Medical AI Agent")
st.caption("Analyzing Pradeepthi Medical Records")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Ask about medical history, medications, risks..."):

    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Read data
    with st.spinner("Reading medical records..."):
        context = read_all_files()

    # Claude response
    with st.spinner("Thinking..."):
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1200,
            messages=[
                {
                    "role": "user",
                    "content": f"""
You are a medical assistant analyzing long-term patient records.

Instructions:
- Use ONLY the provided records
- Identify patterns across years
- Highlight key medications
- Explain risks clearly
- Be structured and clear

Medical Records:
{context}

Question:
{prompt}
"""
                }
            ]
        )

        answer = response.content[0].text

    # Show assistant response
    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)