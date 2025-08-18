# babcock_university_assistant.py
# Babcock University branded multi-source assistant with enhanced UI
#!pip install pdfplumber
#!pip install python-docx
import os
import pdfplumber
import gradio as gr
import google.generativeai as genai
from pathlib import Path
import docx
import json
from pydantic import BaseModel

class MyModel(BaseModel):
    request: Request

    class Config:
        arbitrary_types_allowed = True

# Configuration
try:
    genai.configure(api_key='AIzaSyCC3gThKBUqmdSDgcrjUSyUvxUEhOdS5gs')  # ⚠️ Replace with your actual API key
except KeyError:
    print("Error: GOOGLE_API_KEY environment variable not set.")
    pass

# Configuration for multiple document sources
DOCUMENT_SOURCES = {
    "handbook": "handbook.pdf",
    "catalog": "course_catalog.pdf",
    "policies": "student_policies.pdf",
    "admissions": "admissions_guide.pdf",
    "faq": "frequently_asked_questions.pdf",
    "extra": "extra_unit_form.pdf",
    "bulletin": "bulletin.pdf",
    "info": "information_policy.pdf"
}

# Also support text files and Word documents
TEXT_SOURCES = {
    "requirements": "admission_requirements.txt",
    "schedule": "academic_schedule.txt",
    "procedures": "enrollment_procedures.docx",
    "handbook": "handbook.docx"
}

# Babcock University branding colors and styles
BABCOCK_CSS = """
/* Babcock University Brand Colors */
:root {
    --babcock-primary: #003366;      /* Deep Navy Blue */
    --babcock-secondary: #006633;    /* Forest Green */
    --babcock-accent: #FFD700;       /* Gold */
    --babcock-light: #E8F4FD;        /* Light Blue */
    --babcock-white: #FFFFFF;
    --babcock-text: #333333;
    --babcock-gray: #F5F5F5;
}

/* Main container styling */
.gradio-container {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    background: linear-gradient(135deg, var(--babcock-light) 0%, var(--babcock-white) 100%) !important;
}

/* Header styling */
.header-section {
    background: linear-gradient(135deg, var(--babcock-primary) 0%, var(--babcock-secondary) 100%) !important;
    color: var(--babcock-white) !important;
    padding: 20px !important;
    border-radius: 12px !important;
    margin-bottom: 20px !important;
    box-shadow: 0 4px 15px rgba(0, 51, 102, 0.2) !important;
}

.header-section h1 {
    color: var(--babcock-white) !important;
    font-size: 2.5em !important;
    font-weight: 700 !important;
    margin: 0 !important;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3) !important;
}

.header-section p {
    color: var(--babcock-accent) !important;
    font-size: 1.2em !important;
    margin: 10px 0 0 0 !important;
    font-weight: 500 !important;
}

/* Logo container */
.logo-container {
    display: flex !important;
    align-items: center !important;
    gap: 20px !important;
    margin-bottom: 15px !important;
}

.logo-placeholder {
    width: 80px !important;
    height: 80px !important;
    background: var(--babcock-white) !important;
    border-radius: 50% !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 24px !important;
    font-weight: bold !important;
    color: var(--babcock-primary) !important;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2) !important;
}

/* Tab styling */
.tab-nav {
    background: var(--babcock-white) !important;
    border-radius: 8px !important;
    padding: 5px !important;
    margin: 20px 0 !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
}

.tab-nav button {
    background: transparent !important;
    border: none !important;
    color: var(--babcock-primary) !important;
    font-weight: 600 !important;
    padding: 12px 24px !important;
    border-radius: 6px !important;
    transition: all 0.3s ease !important;
}

.tab-nav button:hover {
    background: var(--babcock-light) !important;
    color: var(--babcock-primary) !important;
}

.tab-nav button.selected {
    background: var(--babcock-primary) !important;
    color: var(--babcock-white) !important;
    box-shadow: 0 2px 8px rgba(0, 51, 102, 0.3) !important;
}

/* Input styling */
.input-container {
    background: var(--babcock-white) !important;
    border-radius: 12px !important;
    padding: 25px !important;
    margin: 20px 0 !important;
    box-shadow: 0 3px 15px rgba(0, 0, 0, 0.1) !important;
    border: 1px solid var(--babcock-light) !important;
}

.left-panel {
    background: var(--babcock-white) !important;
    border-radius: 12px !important;
    padding: 25px !important;
    margin: 10px 0 !important;
    box-shadow: 0 3px 15px rgba(0, 0, 0, 0.1) !important;
    border: 1px solid var(--babcock-light) !important;
    height: fit-content !important;
}

.right-panel {
    background: var(--babcock-white) !important;
    border-radius: 12px !important;
    padding: 25px !important;
    margin: 10px 0 !important;
    box-shadow: 0 3px 15px rgba(0, 0, 0, 0.1) !important;
    border: 1px solid var(--babcock-light) !important;
    min-height: 400px !important;
}

input[type="text"], textarea {
    border: 2px solid var(--babcock-light) !important;
    border-radius: 8px !important;
    padding: 15px !important;
    font-size: 16px !important;
    transition: border-color 0.3s ease !important;
}

input[type="text"]:focus, textarea:focus {
    border-color: var(--babcock-primary) !important;
    box-shadow: 0 0 0 3px rgba(0, 51, 102, 0.1) !important;
    outline: none !important;
}

/* Button styling */
.primary-button {
    background: linear-gradient(135deg, var(--babcock-primary) 0%, var(--babcock-secondary) 100%) !important;
    color: var(--babcock-white) !important;
    border: none !important;
    padding: 15px 30px !important;
    border-radius: 8px !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(0, 51, 102, 0.3) !important;
}

.primary-button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(0, 51, 102, 0.4) !important;
}

.secondary-button {
    background: var(--babcock-white) !important;
    color: var(--babcock-primary) !important;
    border: 2px solid var(--babcock-primary) !important;
    padding: 12px 24px !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
}

.secondary-button:hover {
    background: var(--babcock-primary) !important;
    color: var(--babcock-white) !important;
}

/* Output styling */
.output-container {
    background: var(--babcock-white) !important;
    border-radius: 12px !important;
    padding: 25px !important;
    margin: 20px 0 !important;
    box-shadow: 0 3px 15px rgba(0, 0, 0, 0.1) !important;
    border-left: 4px solid var(--babcock-accent) !important;
}

/* Status card styling */
.status-card {
    background: var(--babcock-white) !important;
    border-radius: 12px !important;
    padding: 20px !important;
    margin: 15px 0 !important;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1) !important;
    border: 1px solid var(--babcock-light) !important;
}

.status-card h3 {
    color: var(--babcock-primary) !important;
    margin-bottom: 15px !important;
}

/* Examples styling */
.examples-container {
    background: var(--babcock-gray) !important;
    border-radius: 8px !important;
    padding: 20px !important;
    margin: 20px 0 !important;
}

.examples-container h4 {
    color: var(--babcock-primary) !important;
    margin-bottom: 15px !important;
}

/* Success and warning messages */
.success-message {
    background: #d4edda !important;
    color: #155724 !important;
    border: 1px solid #c3e6cb !important;
    padding: 12px 20px !important;
    border-radius: 6px !important;
    margin: 10px 0 !important;
}

.warning-message {
    background: #fff3cd !important;
    color: #856404 !important;
    border: 1px solid #ffeaa7 !important;
    padding: 12px 20px !important;
    border-radius: 6px !important;
    margin: 10px 0 !important;
}

/* Footer styling */
.footer {
    background: var(--babcock-primary) !important;
    color: var(--babcock-white) !important;
    padding: 20px !important;
    text-align: center !important;
    border-radius: 8px !important;
    margin-top: 40px !important;
}

/* Responsive design */
@media (max-width: 768px) {
    .header-section h1 {
        font-size: 2em !important;
    }

    .logo-container {
        flex-direction: column !important;
        text-align: center !important;
    }

    .left-panel, .right-panel {
        padding: 15px !important;
    }

    /* Stack panels vertically on mobile */
    .main-row {
        flex-direction: column !important;
    }
}
"""

# Function to extract text from PDF
def extract_pdf_text(file_path):
    """Extract text from PDF file"""
    try:
        with pdfplumber.open(file_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
        return ""

# Function to extract text from Word document
def extract_docx_text(file_path):
    """Extract text from Word document"""
    try:
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error reading Word document {file_path}: {e}")
        return ""

# Function to extract text from text file
def extract_txt_text(file_path):
    """Extract text from text file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except Exception as e:
        print(f"Error reading text file {file_path}: {e}")
        return ""

# Function to load all available documents
def load_all_documents():
    """Load all available university documents"""
    all_documents = {}
    total_chars = 0

    print("Loading Babcock University documents...")

    # Load PDF documents
    for doc_type, file_path in DOCUMENT_SOURCES.items():
        if os.path.exists(file_path):
            print(f"Loading {doc_type}: {file_path}")
            text = extract_pdf_text(file_path)
            if text:
                all_documents[doc_type] = text
                total_chars += len(text)
                print(f"✓ Loaded {doc_type}: {len(text)} characters")
            else:
                print(f"⚠️ No text extracted from {file_path}")
        else:
            print(f"⚠️ {file_path} not found")

    # Load text and Word documents
    for doc_type, file_path in TEXT_SOURCES.items():
        if os.path.exists(file_path):
            print(f"Loading {doc_type}: {file_path}")
            if file_path.endswith('.docx'):
                text = extract_docx_text(file_path)
            else:
                text = extract_txt_text(file_path)

            if text:
                all_documents[doc_type] = text
                total_chars += len(text)
                print(f"✓ Loaded {doc_type}: {len(text)} characters")
            else:
                print(f"⚠️ No text extracted from {file_path}")
        else:
            print(f"⚠️ {file_path} not found")

    # Load from documents directory if it exists
    docs_dir = Path("documents")
    if docs_dir.exists():
        print(f"Scanning documents directory: {docs_dir}")
        for file_path in docs_dir.glob("*"):
            if file_path.is_file():
                doc_name = file_path.stem
                if doc_name not in all_documents:
                    print(f"Loading additional document: {file_path}")

                    if file_path.suffix.lower() == '.pdf':
                        text = extract_pdf_text(str(file_path))
                    elif file_path.suffix.lower() == '.docx':
                        text = extract_docx_text(str(file_path))
                    elif file_path.suffix.lower() in ['.txt', '.md']:
                        text = extract_txt_text(str(file_path))
                    else:
                        continue

                    if text:
                        all_documents[doc_name] = text
                        total_chars += len(text)
                        print(f"✓ Loaded {doc_name}: {len(text)} characters")

    print(f"Total documents loaded: {len(all_documents)}")
    print(f"Total characters: {total_chars}")
    return all_documents

# Function to create comprehensive context from all documents
def create_comprehensive_context(all_documents, max_chars=15000):
    """Create context from all available documents"""
    if not all_documents:
        return ""

    combined_context = ""

    for doc_type, content in all_documents.items():
        combined_context += f"\n=== {doc_type.upper()} INFORMATION ===\n"
        combined_context += content[:max_chars//len(all_documents)] + "\n"

    if len(combined_context) > max_chars:
        combined_context = combined_context[:max_chars]
        last_period = combined_context.rfind('.')
        if last_period > max_chars * 0.8:
            combined_context = combined_context[:last_period + 1]

    return combined_context

# Setup Gemini
try:
    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    print("✓ Gemini model initialized")
except Exception as e:
    print(f"❌ Error setting up Gemini: {e}")
    exit()

# Global storage for all documents
university_documents = {}

def answer_question(question):
    """Answer questions using Babcock University documents and general knowledge"""
    if not question.strip():
        return "Please ask a question about Babcock University or any related topic."

    print(f"Processing question: {question}")

    context = create_comprehensive_context(university_documents)

    if context:
        prompt = f"""You are an intelligent assistant for Babcock University, a prestigious Seventh-day Adventist institution in Nigeria. You have access to comprehensive university information and general knowledge.

Babcock University Information:
{context}

Student Question: {question}

Instructions:
- Provide helpful, accurate answers that reflect Babcock University's excellence and values
- For university-specific questions, use the provided information
- For general academic topics or any topic (except vulgar or potentially dangerous topic), integrate your broader knowledge seamlessly
- Maintain a professional, supportive tone appropriate for a university setting
- Be comprehensive yet concise in your responses

Answer:"""
    else:
        prompt = f"""You are an intelligent assistant for Babcock University, a prestigious Seventh-day Adventist institution in Nigeria.

Student Question: {question}

Please provide a helpful and accurate response using your knowledge about universities and academic topics.

Answer:"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        error_msg = f"I apologize, but I encountered an error while processing your question. Please try again or contact support if the issue persists."
        print(f"Error: {str(e)}")
        return error_msg

def get_document_status():
    """Get status of loaded documents"""
    if not university_documents:
        return """
        <div class="warning-message">
            <strong>⚠️ No university documents loaded</strong><br>
            The assistant is currently running with general knowledge only.
        </div>
        """

    status_items = []
    total_chars = 0
    for doc_type, content in university_documents.items():
        chars = len(content)
        total_chars += chars
        status_items.append(f"<li><strong>{doc_type.title()}</strong>: {chars:,} characters</li>")

    return f"""
    <div class="success-message">
        <strong>✅ Documents Successfully Loaded</strong><br>
        Total: {len(university_documents)} documents, {total_chars:,} characters
    </div>
    <ul>
        {''.join(status_items)}
    </ul>
    """

def reload_documents():
    """Reload all documents"""
    global university_documents
    university_documents = load_all_documents()
    return get_document_status()

# Main execution
if __name__ == "__main__":
    print("Starting Babcock University LLM Assistant...")

    # Load all available documents
    university_documents = load_all_documents()

    if not university_documents:
        print("No university documents found. The assistant will work with general knowledge only.")
        print("To add documents, place them in the same directory or create a 'documents' folder.")

    # Create the interface
    with gr.Blocks(
        title="Babcock University Assistant",
        css=BABCOCK_CSS,
        theme=gr.themes.Soft()
    ) as interface:

        # Header Section
        with gr.Row():
            with gr.Column():
                gr.HTML("""
                <div class="header-section">
                    <div class="logo-container">
                        <div class="logo-placeholder"><img src = "BULOGO.JPEG" alt ="BU" /></div>
                        <div>
                            <h1>🎓 Babcock University LLM</h1>
                            <p>A Seventh-day Adventist Institution of Higher Learning</p>
                        </div>
                    </div>
                </div>
                """)

        # Welcome message
        gr.HTML("""
        <div class="input-container">
            <h3 style="color: var(--babcock-primary); margin-bottom: 15px;">Welcome to Your University Assistant</h3>
            <p>Get comprehensive answers about Babcock University programs, policies, admissions, and general academic topics. Our AI assistant combines university-specific information with broader knowledge to help you succeed.</p>
        </div>
        """)

        # Main interaction section - Side by side layout
        with gr.Row(elem_classes=["main-row"]):
            # Left panel - Question input
            with gr.Column(scale=1, elem_classes=["left-panel"]):
                gr.HTML("<h3 style='color: var(--babcock-primary); margin-bottom: 15px;'>💬 Ask Your Question</h3>")

                question_input = gr.Textbox(
                    placeholder="e.g., What are the admission requirements for the School of Medicine? What is artificial intelligence?",
                    lines=6,
                    show_label=False
                )

                with gr.Row():
                    submit_btn = gr.Button(
                        "Get Answer",
                        variant="primary",
                        size="lg",
                        elem_classes=["primary-button"]
                    )
                    clear_btn = gr.Button(
                        "Clear",
                        variant="secondary",
                        elem_classes=["secondary-button"]
                    )

                # Quick examples
                gr.HTML("""
                <div class="examples-container">
                    <h4>💡 Quick Examples:</h4>
                    <p><em>Click on any example to try it:</em></p>
                </div>
                """)

                gr.Examples(
                    examples=[
                        "What programs does Babcock University offer?",
                        "How do I apply for admission?",
                        "What are the tuition fees?",

                    ],
                    inputs=question_input
                )

            # Right panel - Answer display
            with gr.Column(scale=1, elem_classes=["right-panel"]):
                gr.HTML("<h3 style='color: var(--babcock-primary); margin-bottom: 15px;'>📝 Answer</h3>")

                answer_output = gr.Textbox(
                    lines=20,
                    show_label=False,
                    interactive=False,
                    placeholder="Your answer will appear here after you submit a question..."
                )

        # Document status section
        with gr.Accordion("📚 Document Status & Management", open=False):
            with gr.Row():
                with gr.Column(scale=2):
                    status_display = gr.HTML(get_document_status())
                with gr.Column(scale=1):
                    reload_btn = gr.Button(
                        "🔄 Reload Documents",
                        variant="secondary",
                        elem_classes=["secondary-button"]
                    )

            gr.HTML("""
            <div class="status-card">
                <h3>📋 Adding New Documents</h3>
                <p><strong>Supported formats:</strong> PDF, Word (.docx), Text (.txt), Markdown (.md)</p>
                <p><strong>How to add:</strong></p>
                <ul>
                    <li>Place files in the same directory as this application</li>
                    <li>Or create a 'documents' folder and place files there</li>
                    <li>Click 'Reload Documents' to refresh the system</li>
                </ul>
                <p><strong>Recommended document types:</strong> University handbook, Course catalog, Admission guide, Student policies, Academic calendar, FAQs</p>
            </div>
            """)

        # Footer
        gr.HTML("""
        <div class="footer">
            <p><strong>Babcock University</strong> | Ilishan-Remo, Ogun State, Nigeria</p>
            <p>Empowering minds, transforming lives through quality education</p>
        </div>
        """)

        # Event handlers
        submit_btn.click(
            fn=answer_question,
            inputs=question_input,
            outputs=answer_output
        )

        clear_btn.click(
            fn=lambda: ("", ""),
            outputs=[question_input, answer_output]
        )

        reload_btn.click(
            fn=reload_documents,
            outputs=status_display
        )

        question_input.submit(
            fn=answer_question,
            inputs=question_input,
            outputs=answer_output
        )

        # Add this script at the end of your Gradio interface definition


    # Launch the interface
    print("🚀 Launching Babcock University Assistant...")
    interface.launch(
     server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 8080)))
    )
