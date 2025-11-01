import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
import docx
import urllib.parse  # required for printable view

# Initialize Groq client using Streamlit Secrets
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("📘 Study Helper AI Agent (SANDESH Version)")

# --- UI Customization ---
st.markdown(
    """
    <style>
    /* Hide Streamlit main menu (contains Fork in some deployments) */
    #MainMenu { visibility: hidden; }
    /* Hide any fork or edit buttons if present */
    div[title="Fork this app"], button[title="Fork this app"], a[aria-label="Fork"] { display: none !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Intro + Instructions ---
st.markdown("Upload your study file (Word or PDF) to get simplified, point-wise answers tailored to your selected marks.")
st.info("💡 Tip: Upload class notes or study material. Then select 2, 5, 10, or 15 marks and ask your question.")

# --- File Upload ---
uploaded_file = st.file_uploader("📄 Upload your study notes", type=["pdf", "docx"])
st.caption("Accepted formats: PDF or DOCX — The AI will read your notes and create concise answers.")

# --- Text Extraction Function ---
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

# --- AI Query Function ---
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

# --- Main Logic ---
if uploaded_file:
    text = extract_text(uploaded_file)
    st.success("✅ File processed successfully!")

    # Show preview
    preview = text[:1000] + ("..." if len(text) > 1000 else "")
    st.subheader("📄 Preview of Extracted Notes")
    st.text_area("Notes Preview (read-only)", value=preview, height=200)
    st.caption(f"Extracted text length: {len(text)} characters")

    # --- Download + Printable View ---
    col1, col2 = st.columns([1, 1])

    with col1:
        st.download_button(
            label="📥 Download Notes",
            data=text.encode("utf-8"),
            file_name="extracted_notes.txt",
            mime="text/plain"
        )

    with col2:
        # Encode for printable HTML
        html_escape = urllib.parse.quote(text)
        printable_html = f"""
        <html>
          <head><title>Printable Notes</title></head>
          <body><pre style="white-space:pre-wrap">{html_escape}</pre></body>
        </html>
        """
        data_url = "data:text/html;charset=utf-8," + urllib.parse.quote(printable_html)
        st.markdown(f"[🖨️ Open printable view]({data_url})", unsafe_allow_html=True)

    # --- Example Questions ---
    with st.expander("💬 Example Questions"):
        st.write("- Explain the main concepts of Object-Oriented Programming.")
        st.write("- Summarize the key differences between procedural and OOP.")
        st.write("- Provide a 10-mark answer on system architecture in point form.")

    # --- Question Input ---
    question = st.text_input("✏️ Enter your question:", placeholder="e.g., Explain inheritance in OOP.")
    marks = st.selectbox("🏷️ Select marks:", [2, 5, 10, 15])

    # --- Generate Answer Button ---
    if st.button("🚀 Generate Answer"):
        if question.strip() and text.strip():
            try:
                with st.spinner("🧠 Generating answer..."):
                    answer = ask_ai(text, question, marks)
                st.subheader("🧾 Generated Answer:")
                st.write(answer)
            except Exception as e:
                st.error(f"⚠️ An error occurred while generating the answer: {e}")
        else:
            st.warning("⚠️ Please upload a valid file and enter a question.")
