# babcock_university_assistant.py
# Babcock University branded multi-source assistant with streaming
import os
import gradio as gr
import google.generativeai as genai
import pdfplumber
import docx
from pathlib import Path
import json

# ==============================
# CONFIGURATION
# ==============================
try:
    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY", ""))
except Exception as e:
    print("⚠️ Google Gemini API key not found or invalid.", e)

model = genai.GenerativeModel("gemini-1.5-flash")

# ==============================
# DOCUMENT LOADING
# ==============================
def load_pdf(file_path):
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"⚠️ Error loading PDF {file_path}: {e}")
    return text

def load_docx(file_path):
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"⚠️ Error loading DOCX {file_path}: {e}")
    return text

def load_txt(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"⚠️ Error loading TXT {file_path}: {e}")
        return ""

def load_documents(folder="documents"):
    docs = {}
    folder_path = Path(folder)
    if not folder_path.exists():
        folder_path.mkdir(parents=True, exist_ok=True)
    for file in folder_path.iterdir():
        if file.suffix.lower() == ".pdf":
            docs[file.name] = load_pdf(file)
        elif file.suffix.lower() == ".docx":
            docs[file.name] = load_docx(file)
        elif file.suffix.lower() == ".txt":
            docs[file.name] = load_txt(file)
    return docs

university_documents = load_documents()

# ==============================
# CONTEXT BUILDER
# ==============================
def create_comprehensive_context(docs):
    context = ""
    for name, content in docs.items():
        context += f"\n--- {name} ---\n{content}\n"
    return context

# ==============================
# STREAMING FUNCTION
# ==============================
def stream_answer(question):
    """Stream tokens from Gemini to avoid Render timeout"""
    if not question.strip():
        yield "Please ask a question about Babcock University or academics."
        return

    context = create_comprehensive_context(university_documents)
    if context:
        prompt = f"""You are an intelligent assistant for Babcock University.

Babcock University Information:
{context}

Student Question: {question}

Answer:"""
    else:
        prompt = f"""You are an intelligent assistant for Babcock University.

Student Question: {question}

Answer:"""

    try:
        response = model.generate_content(prompt, stream=True)
        partial = ""
        for chunk in response:
            if chunk.text:
                partial += chunk.text
                yield partial
    except Exception as e:
        yield f"⚠️ Error while processing: {e}"

# ==============================
# GRADIO UI WITH BABCOCK BRAND
# ==============================
css = """
#babcock-container {background: #f4f9ff; font-family: Arial, sans-serif;}
#title {color: #00274d; font-size: 28px; font-weight: bold; margin-bottom: 20px;}
.panel {background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);}
"""

with gr.Blocks(css=css) as demo:
    with gr.Column(elem_id="babcock-container", equal_height=False):
        gr.Markdown("<div id='title'>🎓 Babcock University Multi-Source Assistant</div>")

        with gr.Row():
            with gr.Column(scale=2):
                question_input = gr.Textbox(
                    label="Ask a Question",
                    placeholder="E.g., What is Babcock’s grading system?",
                    lines=2
                )
                submit_btn = gr.Button("Submit", elem_classes="panel")

                answer_output = gr.Textbox(
                    label="Answer",
                    interactive=False,
                    lines=10,
                    elem_classes="panel"
                )

            with gr.Column(scale=1):
                gr.Markdown("### 📘 Available Documents")
                doc_list = gr.JSON(value=list(university_documents.keys()), label="Loaded Files")

        # Hook up streaming
        submit_btn.click(fn=stream_answer, inputs=question_input, outputs=answer_output)
        question_input.submit(fn=stream_answer, inputs=question_input, outputs=answer_output)

# ==============================
# ENTRY POINT
# ==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    demo.launch(server_name="0.0.0.0", server_port=port)
