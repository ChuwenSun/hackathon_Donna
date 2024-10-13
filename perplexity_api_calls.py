import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
YOUR_PERPLEXITY_API_KEY = os.environ.get("YOUR_PERPLEXITY_API_KEY")


def ask_perplexity(prompt):
    messages = [
        {
            "role": "system",
            "content": (
                "You are an artificial intelligence assistant and you need to "
                "engage in a helpful, detailed, polite conversation with a user."
            ),
        },
        {
            "role": "user",
            "content": (prompt),
        },
    ]

    perplexity_client = OpenAI(
        api_key=YOUR_PERPLEXITY_API_KEY, base_url="https://api.perplexity.ai"
    )

    # chat completion without streaming
    perplexity_response = perplexity_client.chat.completions.create(
        model="llama-3.1-sonar-small-128k-online",
        messages=messages,
    )

    # print(perplexity_response)
    return perplexity_response.choices[-1].message.content
    # # chat completion with streaming
    # response_stream = client.chat.completions.create(
    #     model="llama-3.1-sonar-small-128k-online",
    #     messages=messages,
    #     stream=True,
    # )
    # for response in response_stream:
    #     print(response)
