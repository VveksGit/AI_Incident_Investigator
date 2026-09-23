import os

import requests
from dotenv import load_dotenv

load_dotenv()


def call_llm(prompt):
    api_key = os.getenv("OPENROUTER_API_KEY")

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    data = {
        "model": "openrouter/free",
        "messages": [
            {
                "role": "system",
                "content": "You are an incident investigation assistant.",
            },
            {"role": "user", "content": prompt},
        ],
        "response_format": {"type": "json_object"},
    }

    response = requests.post(url, headers=headers, json=data)

    response.raise_for_status()

    return response.json()
