from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import ollama
from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Question(BaseModel):
    question: str

def search_web(query):
    links = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=3):
            links.append(r["href"])
    return links

def extract_text(url):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text() for p in paragraphs[:5])
        return text[:2000]
    except:
        return ""

def ask_llm(prompt):
    response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]

@app.post("/ask")
def ask(body: Question):
    links = search_web(body.question)
    combined_text = ""
    for link in links:
        combined_text += extract_text(link)

    prompt = f"""
Ответь на вопрос используя информацию ниже.

Вопрос: {body.question}

Информация:
{combined_text[:3000]}
"""
    answer = ask_llm(prompt)
    return {"answer": answer}

@app.get("/")
def root():
    return FileResponse("index.html")

# Run with: uvicorn server:app --reload --port 8000
