import os
import sys

from openai import OpenAI


def client_authentication(token_file = "token.txt"):
    with open(token_file, "r") as f:
        github_token = f.read().strip()

    client = OpenAI(
        base_url = "https://models.inference.ai.azure.com",
        api_key = github_token,
    )
    return client

if __name__ == '__main__':
    try:
        client = client_authentication()
        print("Successfully authenticated OpenAI client")
    except Exception as e:
        print(f"Error during client authentication: {e}")
        sys.exit(1)