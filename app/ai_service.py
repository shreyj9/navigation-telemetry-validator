from openai import OpenAI


def analyze_incident(log_text: str) -> str:
    client = OpenAI()

    response = client.responses.create(
        model="gpt-6-luna",
        input=[
            {
                "role": "system",
                "content": (
                    "You are a navigation telemetry incident triage assistant. "
                    "Analyze only the information provided. "
                    "Do not invent facts. "
                    "Return a concise explanation of the likely issue, "
                    "severity, and recommended next steps."
                ),
            },
            {
                "role": "user",
                "content": log_text,
            },
        ],
    )

    return response.output_text