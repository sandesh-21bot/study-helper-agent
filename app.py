import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
import docx

# Initialize Groq client using Streamlit Secrets
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("📘 Study Helper AI Agent (SANDESH vvVersion)")

# New: friendly introduction and brief instructions
st.markdown("Upload your file (Word (.docx) or PDF) to get simplified, point-wise answers tailored to the marks you choose.")
st.info("Tip: Upload study notes or lecture slides. Select marks (2, 5, 10, 15) and ask a concise question for a structured answer.")

# Upload file (improved label + caption)
uploaded_file = st.file_uploader("Upload your study notes (Word or PDF)", type=["pdf", "docx"])
st.caption("Accepted formats: .pdf, .docx — The agent will read your notes and produce a concise, point-wise answer.")

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

    # New: show a short preview and length so user can confirm content
    preview = text[:1000] + ("..." if len(text) > 1000 else "")
    st.subheader("Preview of extracted notes")
    st.text_area("Notes preview (read-only)", value=preview, height=200)

    st.caption(f"Extracted text length: {len(text)} characters")

    # New: sample questions expander and placeholder
    with st.expander("Example questions"):
        st.write("- Explain the main concepts of X in point form.")
        st.write("- Summarize the key differences between A and B.")
        st.write("- Provide a 10-mark answer on topic Y with bullet points.")

    question = st.text_input("Enter your question:", placeholder="e.g., Summarize key points about photosynthesis")
    marks = st.selectbox("Select marks:", [2, 5, 10, 15])

    if st.button("Generate Answer"):
        if question.strip() and text.strip():
            try:
                with st.spinner("Generating answer..."):
                    answer = ask_ai(text, question, marks)
                st.subheader("🧾 Generated Answer:")
                st.write(answer)
            except Exception as e:
                st.error(f"An error occurred while generating the answer: {e}")
        else:
            st.warning("Please upload a valid file and enter a question.")
