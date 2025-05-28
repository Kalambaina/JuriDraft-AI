import gradio as gr
import requests
import re
import os
from docx import Document

# ========== API Configuration ==========
API_KEY = "AIzaSyALyNrInhxAQ9kbr8XbxpXiA6gDCsQUYXc"
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

# ========== Ensure output directory exists ==========
os.makedirs("outputs", exist_ok=True)

# ========== Output Cleaner ==========
def clean_output(text):
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    disclaimer_patterns = [
        r"This is not (a substitute for|legal) advice.*",
        r"I am not a lawyer.*",
        r"As an AI language model.*",
        r"The model's responses.*",
        r"Please consult.*(a licensed attorney|legal professional).*",
        r"The information provided.*(general informational|not constitute).*",
        r"Always seek professional legal advice.*",
        r"Note:.*legal.*",
        r"This response is for informational purposes.*",
        r"Disclaimer*",
        r"Recommendation*",
        r"This analysis is based on my understanding*",
        r"Okay, let's provide a legal opinion*",
        r"Important Notes*",
    ]
    for pattern in disclaimer_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    return re.sub(r"\n{2,}", "\n\n", text).strip()

# ========== Core Gemini API call ==========
def ask_gemini(prompt):
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    response = requests.post(ENDPOINT, json=payload)
    result = response.json()
    try:
        raw_text = result["candidates"][0]["content"]["parts"][0]["text"]
        return clean_output(raw_text)
    except Exception as e:
        return f"Error: Unable to fetch response. Details: {str(e)}"

# ========== Save output to DOCX ==========
def save_to_docx(text, filename="output.docx"):
    file_path = os.path.join("outputs", filename)
    doc = Document()
    doc.add_paragraph(text)
    doc.save(file_path)
    return file_path

# ========== Feature implementations ==========

# 1. Draft court processes
def draft_court_process(document_type, facts, parties):
    prompt = (
        f"Draft a {document_type} court process document based on the following facts:\n\n"
        f"Facts: {facts}\n\n"
        f"Parties: {parties}\n\n"
        "Format it as a formal legal document."
    )
    return ask_gemini(prompt)

# 2. Legal research assistant
def legal_research(query):
    prompt = f"Provide a detailed legal research summary on Nigerian law related to the following query:\n{query}"
    return ask_gemini(prompt)

# 3. Draft review / critique
def draft_review(document_text):
    prompt = (
        f"Review this legal draft, identify errors, inconsistencies, or improvements, "
        f"and provide clear suggestions:\n\n{document_text}"
    )
    return ask_gemini(prompt)

# 4. Chatbot assistant
def chatbot_assistant(question):
    prompt = f"You are a helpful Nigerian legal assistant. Answer this query clearly and professionally:\n{question}"
    return ask_gemini(prompt)

# ========== Gradio UI ==========
with gr.Blocks() as juri_draft_ui:
    gr.Markdown("# ⚖️ JuriDraft AI Legal Assistant MVP")

    with gr.Tab("📄 Draft Court Process"):
        doc_type = gr.Textbox(label="Document Type (e.g., Motion, Affidavit)")
        facts = gr.Textbox(label="Key Facts", lines=4)
        parties = gr.Textbox(label="Parties Involved")
        draft_btn = gr.Button("Generate Draft")
        draft_output = gr.Textbox(label="Generated Draft", lines=15)
        download_draft = gr.File(label="Download Draft (.docx)")

        def generate_draft_and_save(t, f, p):
            draft = draft_court_process(t, f, p)
            path = save_to_docx(draft, "court_process_draft.docx")
            return draft, path

        draft_btn.click(
            fn=generate_draft_and_save,
            inputs=[doc_type, facts, parties],
            outputs=[draft_output, download_draft]
        )

    with gr.Tab("🔎 Legal Research Assistant"):
        research_query = gr.Textbox(label="Enter Research Query")
        research_btn = gr.Button("Run Research")
        research_output = gr.Textbox(label="Research Result", lines=15)
        research_download = gr.File(label="Download Research (.docx)")

        def research_and_save(q):
            result = legal_research(q)
            path = save_to_docx(result, "legal_research.docx")
            return result, path

        research_btn.click(
            fn=research_and_save,
            inputs=research_query,
            outputs=[research_output, research_download]
        )

    with gr.Tab("📝 Draft Review"):
        draft_text = gr.Textbox(label="Paste Draft Here", lines=15)
        review_btn = gr.Button("Review Draft")
        review_output = gr.Textbox(label="Review Comments", lines=15)

        review_btn.click(
            fn=draft_review,
            inputs=draft_text,
            outputs=review_output
        )

    with gr.Tab("💬 Chatbot Assistant"):
        chat_input = gr.Textbox(label="Ask your legal question")
        chat_btn = gr.Button("Ask")
        chat_output = gr.Textbox(label="Response", lines=10)

        chat_btn.click(
            fn=chatbot_assistant,
            inputs=chat_input,
            outputs=chat_output
        )

juri_draft_ui.launch(share=True)
