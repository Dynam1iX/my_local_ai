import ollama
from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup

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

def ask_ai(question):
    print("🔎 Ищу в интернете...")
    links = search_web(question)

    combined_text = ""
    for link in links:
        combined_text += extract_text(link)

    prompt = f"""
Ответь на вопрос используя информацию ниже.

Вопрос: {question}

Информация:
{combined_text[:3000]}
"""

    return ask_llm(prompt)

if __name__ == "__main__":
    while True:
        question = input("\nТы: ")
        answer = ask_ai(question)
        print("\nИИ:", answer)