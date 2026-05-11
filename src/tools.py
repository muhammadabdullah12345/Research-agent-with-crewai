import requests
import os
from dotenv import load_dotenv

load_dotenv()


def fetch_research(topic: str) -> str:
    """Call Serper directly, return formatted results."""
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return f"No SERPER_API_KEY found. Using topic only: {topic}"

    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json",
    }
    payload = {"q": topic, "num": 8}

    try:
        response = requests.post(
            "https://google.serper.dev/search",
            headers=headers,
            json=payload,
            timeout=10,
        )
        data = response.json()
        results = []

        if "answerBox" in data:
            ab = data["answerBox"]
            answer = ab.get("answer") or ab.get("snippet", "")
            if answer:
                results.append(f"QUICK ANSWER: {answer}")

        for item in data.get("organic", [])[:8]:
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            link = item.get("link", "")
            results.append(f"- {title}\n  {snippet}\n  Source: {link}")

        paas = data.get("peopleAlsoAsk", [])[:3]
        if paas:
            results.append("\nRELATED QUESTIONS:")
            for paa in paas:
                results.append(f"  Q: {paa.get('question', '')}")
                results.append(f"  A: {paa.get('snippet', '')}")

        return "\n\n".join(results) if results else f"No results found for: {topic}"

    except Exception as e:
        return f"Search failed: {str(e)}. Proceeding with LLM knowledge only."