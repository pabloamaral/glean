import requests
from config import CLIENT_BASE_URL, CLIENT_HEADERS


def chat(question: str, search_results: list[dict]) -> str:
    if search_results:
        context_lines = []
        for i, r in enumerate(search_results, 1):
            context_lines.append(
                f"[Source {i}: {r['title']}]\n{r['snippet']}"
            )
        context_block = "\n\n".join(context_lines)

        message_text = (
            f"Using only the following internal Banks & Banjo LLC HR documents "
            f"as your source, please answer this question:\n\n"
            f"Question: {question}\n\n"
            f"Context from internal documents:\n\n{context_block}\n\n"
            f"Cite which document(s) you used in your answer."
        )
    else:
        # No results — instruct the model to say so rather than hallucinate
        message_text = (
            f"A user asked: '{question}'\n\n"
            f"No relevant internal Banks & Banjo LLC HR documents were found "
            f"for this question. Please let the user know and suggest they "
            f"contact People Operations at people@banksandbanjo.com."
        )

    payload = {
        "messages": [
            {
                "fragments": [{"text": message_text}],
                "author": "USER",
            }
        ],
        "saveChat": False,
        "stream": False,  # Don't persist to Glean chat history in sandbox
    }

    response = requests.post(
        f"{CLIENT_BASE_URL}/chat",
        headers=CLIENT_HEADERS,
        json=payload,
        timeout=120,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Chat API error {response.status_code}: {response.text}"
        )

    data = response.json()

# Extract the text from the last assistant message fragment
    messages = data.get("messages", [])
    for msg in reversed(messages):
        if msg.get("author") in ("GLEAN_AI", "ASSISTANT", "BOT"):
            for fragment in msg.get("fragments", []):
                text = fragment.get("text", "").strip()
                if text:
                    return text

# Fallback
    return data.get("answer", {}).get("text", "No answer returned from Chat API.")


if __name__ == "__main__":
    import sys

    question = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What is the PTO policy?"
    print(f"Asking Chat (no search context): '{question}'\n")

    answer = chat(question, search_results=[])
    print(answer)
