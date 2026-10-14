import logging
import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def call_llm(prompt):
    api_key = os.getenv("OPENROUTER_API_KEY")

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    data = {
        "model": os.getenv("OPENROUTER_MODEL"),
        "messages": [
            {
                "role": "system",
                "content": "You are an incident investigation assistant.",
            },
            {"role": "user", "content": prompt},
        ],
        "response_format": {"type": "json_object"},
    }

    for attempt in range(3):
        try:
            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=int(os.getenv("LLM_TIMEOUT")),
            )

            response.raise_for_status()
            return response.json()

        except requests.HTTPError as e:
            logger.error(
                "LLM HTTP ERROR (attempt %s/3): %s",
                attempt + 1,
                e,
            )

            if response.status_code < 500 or attempt == 2:
                raise

            time.sleep(2)

        except requests.RequestException as e:
            logger.error(
                "LLM API ERROR (attempt %s/3): %s",
                attempt + 1,
                e,
            )

            if attempt == 2:
                raise

            time.sleep(2)

        except ValueError as e:
            logger.error("LLM RESPONSE ERROR: %s", e)
            raise
