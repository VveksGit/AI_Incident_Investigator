import json

from llm import call_llm


def main():
    incident = {
        "service": "Payment API",
        "timestamp": "2026-09-22 10:42:00",
        "description": "Users began receiving payment failures.",
        "logs": [
            "Database connection timeout.",
            "Retry attempt 1.",
            "Retry attempt 2.",
            "Request failed.",
        ],
        "deployment": {"version": "2.4.1", "deployed_at": "2026-09-22 10:30:00"},
    }
    if validate_incident(incident):
        print("The input is valid!")
    else:
        print("The input is invalid!")

    normalized_incident = normalize_incident(incident)
    prompt = build_prompt(normalized_incident)

    result = call_llm(prompt)
    content = result["choices"][0]["message"]["content"]
    investigation = json.loads(content)

    if validate_investigation(investigation):
        print("Investigation output is valid!")
        print(investigation)
    else:
        print("Invalid investigation output!")

    with open("llm_response.json", "w") as file:
        json.dump(result, file, indent=4)


def validate_incident(incident):
    required_fields = ["service", "timestamp", "description", "logs", "deployment"]
    for field in required_fields:
        if field not in incident:
            return False
    return True


def normalize_incident(incident):
    normalized = incident.copy()

    normalized["service"] = incident["service"].strip()
    normalized["timestamp"] = incident["timestamp"].strip()
    normalized["description"] = incident["description"].strip()

    normalized["logs"] = [log.strip() for log in incident["logs"] if log.strip()]

    return normalized


def build_prompt(incident):
    prompt = f"""
      You are an incident investigation assistant.

      Analyze the following software incident.

      Service:
      {incident["service"]}

      Timestamp:
      {incident["timestamp"]}

      Description:
      {incident["description"]}

      Logs:
      {chr(10).join(incident["logs"])}

      Deployment:
      Version: {incident["deployment"]["version"]}
      Deployed at: {incident["deployment"]["deployed_at"]}

      Return ONLY valid JSON.

      The JSON must follow this exact structure:

      {{
          "incident_type": "string",
          "summary": "string",
          "hypotheses": [
              {{
                  "cause": "string",
                  "evidence": ["string"],
                  "confidence": "low | medium | high"
              }}
          ],
          "missing_information": ["string"]
      }}

      Rules:
      - Do not use Markdown.
      - Do not include explanations outside the JSON.
      - Do not include recommendations.
      - Do not claim a hypothesis is confirmed unless the provided evidence establishes it.
      - Do not invent evidence.
      - Confidence describes how strongly the provided evidence supports the hypothesis.
    """

    return prompt


def validate_investigation(investigation):
    required_fields = ["incident_type", "summary", "hypotheses", "missing_information"]

    for field in required_fields:
        if field not in investigation:
            return False

    if not isinstance(investigation["incident_type"], str):
        return False

    if not isinstance(investigation["summary"], str):
        return False

    if not isinstance(investigation["hypotheses"], list):
        return False

    if not isinstance(investigation["missing_information"], list):
        return False

    for hypothesis in investigation["hypotheses"]:
        if not isinstance(hypothesis, dict):
            return False

        if "cause" not in hypothesis:
            return False

        if "evidence" not in hypothesis:
            return False

        if "confidence" not in hypothesis:
            return False

        if not isinstance(hypothesis["cause"], str):
            return False

        if not isinstance(hypothesis["evidence"], list):
            return False

        if hypothesis["confidence"] not in ["low", "medium", "high"]:
            return False

    return True


if __name__ == "__main__":
    main()
