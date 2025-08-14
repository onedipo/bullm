import os
import google.generativeai as genai
import gradio as gr
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Ensure uploads folder exists
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def process_input(user_input, file):
    # Handle file upload if present
    if file:
        file_path = os.path.join(UPLOAD_FOLDER, file.name)
        with open(file_path, "wb") as f:
            f.write(file.read())
        response = f"Processed file: {file.name}"
        os.remove(file_path)
    else:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(user_input).text
    return response

with gr.Blocks(css="#chatbot {height: 500px; overflow: auto;}") as demo:
    gr.Markdown("<h1 style='text-align:center'>Gemini LLM Chatbot</h1>")
    chatbot = gr.Chatbot(elem_id="chatbot")
    msg = gr.Textbox(label="Your message")
    file_upload = gr.File(label="Upload a file", file_types=[".txt", ".pdf", ".csv", ".docx"], type="file")
    send_btn = gr.Button("Send")

    def respond(message, file, history):
        bot_reply = process_input(message, file)
        history.append((message, bot_reply))
        return history, ""

    send_btn.click(respond, inputs=[msg, file_upload, chatbot], outputs=[chatbot, msg])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 10000)))
