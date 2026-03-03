import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")


def generate_response(question: str, context_data: list):
    context_text = "\n\n".join(
        f"Title: {item['title']}\nContent: {item['content']}"for item in context_data)

    prompt = f"""
    You are an assistant. Answer the question using ONLY the provided context.
    Context:{context_text}
    Question:{question}
    Answer:
    """

    response = model.generate_content(prompt)

    if not response or not response.text:
        return "Sorry, I couldn't generate a response."

    return response.text
