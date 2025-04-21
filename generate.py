import json
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
PROMPTS_DIR = 'prompts'
RESPONSES_DIR = 'responses'

def generate_response(model, prompt, client):
    """
    Generates model output from given prompt
    
    Args:
        model (str): Name of model
        prompt (str): Prompt

    Returns:
        response (str)
    """
    response = client.chat.completions.create(
        model = model,
        messages = [{"role": "user","content": prompt}],
        max_tokens = 1024,
        temperature = 0.7
        )

    return response.choices[0].message.content

def generate_all_responses(models, prompt, client):
    return {model: generate_response(model, prompt, client) for model in models}



def load_prompt(prompt_file):
    """
    Reads prompt_file to retrieve prompt

    Args:
        prompt_file (str): File path to prompt
    """
    with open(prompt_file, 'r') as f:
        prompt = f.read()

    return prompt

def save_responses(task_name, responses):
    for model, response in responses.items():
        file_path = os.path.join(RESPONSES_DIR, f"{task_name}-{model}.txt")
        with open(file_path, 'w') as f:
            f.write(response)
        print(f"Saved response for {model} to {file_path}")

def run(prompt_file, models, client):
    """
    Workflow for processing prompt file and saving the models' responses in a file

    Args:
        prompt_file (str): File path to prompt
        models (list[str]): List of models
    """
    
    prompt = load_prompt(prompt_file)
    task_name = os.path.splitext(os.path.basename(prompt_file))[0] # Retrieve name of prompt
    
    responses = generate_all_responses(models, prompt, client)
    save_responses(task_name, responses)

    return task_name

if __name__ == '__main__':
    if not os.path.exists(PROMPTS_DIR):
        print("Prompt directory does not exist! Terminating run.")
        sys.exit(1)
    
    if not os.path.exists(RESPONSES_DIR):
        os.makedirs(RESPONSES_DIR)

    client = OpenAI(
        base_url = "https://models.inference.ai.azure.com",
        api_key = GITHUB_TOKEN,
    )

    models = ['gpt-4o-mini', 'Codestral-2501']
    # scores = {}
    for prompt_file in os.listdir(PROMPTS_DIR):
        if prompt_file.endswith('.txt'):
            task_name, score = run(os.path.join(PROMPTS_DIR, prompt_file), models, client)
            # scores[task_name] = score

    # with open('scores.json', 'w') as f:
    #     json.dump(scores, f, indent=4)


