import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
PROMPTS_DIR = 'prompts'
RESPONSES_DIR = 'responses'

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

def load_prompt(prompt_file):
    """
    Reads prompt_file to retrieve prompt

    Args:
        prompt_file (str): File path to prompt
    """
    with open(prompt_file, 'r') as f:
        prompt = f.read()

    return prompt

def run(prompt_file):
    """
    Workflow for processing prompt file and saving the model's response in a file

    Args:
        prompt_file (str): File path to prompt
    """
    
    prompt = load_prompt(prompt_file)
    task_name = os.path.splitext(os.path.basename(prompt_file))[0] # Retrieve name of prompt

    models = ['gpt-4o-mini', 'Codestral-2501']
    
    for model in models:
        response = generate_response(model, prompt)
        response_path = os.path.join(RESPONSES_DIR, f"{task_name}-{model}.txt")
        
        with open(response_path, 'w') as f:
            f.write(response)
            print(f"Saving {model} response to {task_name} in {response_path}")


if __name__ == '__main__':
    if not os.path.exists(PROMPTS_DIR):
        print("Prompt directory does not exist! Terminating run.")
        sys.exit(1)
    
    if not os.path.exists(RESPONSES_DIR):
        os.makedirs(RESPONSES_DIR)

    for prompt_file in os.listdir(PROMPTS_DIR):
        if prompt_file.endswith('.txt'):
            run(os.path.join(PROMPTS_DIR, prompt_file))

