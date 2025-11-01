import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
import docx

# Initialize Groq client using Streamlit Secrets
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("📘 Study Helper AI Agent (SANDESH vvVersion)")

# Upload file
uploaded_file = st.file_uploader("Upload your study notes (PDF or DOCX)", type=["pdf", "docx"])

def extract_text(file):
    if file.name.endswith(".pdf"):
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text()
        return text
    elif file.name.endswith(".docx"):
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        return ""

def ask_ai(context, question, marks):
    prompt = f"""
    You are a study helper AI. Use the notes below to generate a clear, structured answer.

    Notes:
    {context}

    Question: {question}
    Marks: {marks}

    Provide the answer as a concise, point-wise format suitable for a {marks}-mark question.
    """
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content

if uploaded_file:
    text = extract_text(uploaded_file)
    st.success("✅ File processed successfully!")

    question = st.text_input("Enter your question:")
    marks = st.selectbox("Select marks:", [2, 5, 10, 15])

    if st.button("Generate Answer"):
        if question.strip() and text.strip():
            answer = ask_ai(text, question, marks)
            st.subheader("🧾 Generated Answer:")
            st.write(answer)
        else:
            st.warning("Please upload a valid file and enter a question.")
