import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

GITHUB_TOKEN = os.environ['GITHUB_TOKEN']

def generate_response(model, prompt):
    """
    Generates model output from given prompt
    
    Args:
        model (str): Name of model
        prompt (str): Prompt

    Returns:
        response (str)
    """
    client = OpenAI(
        base_url = "https://models.inference.ai.azure.com",
        api_key = GITHUB_TOKEN,
    )

    response = client.chat.completions.create(
        model = model,
        messages = [{"role": "user","content": prompt}],
        max_tokens = 1024,
        temperature = 0.7
        )

    return response.choices[0].message.content

def generate_and_compare_responses(model1, model2, prompt):
    """
    Inputs the same prompt into two different models (model1 and model2), generates outputs,
    and performs comparative analysis using various metrics
    
    Args:
        model1 (str): Name of first model
        model2 (str): Name of second model
        prompt (str): Prompt

    Output:
        model1_response (str): Response from first model
        model2_response (str): Response from second model
        scores (dict): --
    """

    model1_response = generate_response(model1, prompt)
    model2_response = generate_response(model2, prompt)

    print(f"Model 1 ({model1}) Response:")
    print(model1_response)

    print(f"Model 2 ({model2}) Response:")
    print(model2_response)

if __name__ == '__main__':
    with open('prompt.txt', 'r') as f:
        prompt = f.read()

    with open('response.txt', 'w') as f:
        f.write(generate_response('gpt-4o-mini', prompt))

