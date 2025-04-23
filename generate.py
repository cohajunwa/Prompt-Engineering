import argparse
import json
import os
import sys

from evaluate import get_cosine_similarity, get_bleu_4_score
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
PROMPTS_DIR = ''
RESPONSES_DIR = 'responses'

def generate_response(model, messages, client):
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
        messages = messages,
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
    with open(os.path.join(PROMPTS_DIR, prompt_file), 'r') as f:
        prompt = f.read()

    return prompt

def parse_json_file(json_file):
    """Reads JSON file and returns strategy, task name, and prompt files
    Args:
        json_file (str): JSON file with task_name, strategy, and prompt_files
    Returns:
        tuple: strategy, task_name, prompt_files
    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If the file content is invalid or missing required keys
    """

    if not os.path.exists(json_file):
        raise FileNotFoundError(f"The file {json_file} does not exist.")

    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON from file {json_file}: {e}")

    required_keys = {"strategy", "task_name", "prompt_files"}
    valid_strategies = {"zero_shot", "few_shot", "chain_of_thought", "self_consistency", "prompt_chaining"}

    if not required_keys.issubset(data.keys()):
        raise ValueError(f"JSON file {json_file} is missing required keys: {required_keys - data.keys()}")

    if not isinstance(data["prompt_files"], list) or not all(isinstance(file, str) for file in data["prompt_files"]):
        raise ValueError(f"'prompt_files' in {json_file} must be a list of strings.")
    
    if data["strategy"] not in valid_strategies:
        raise ValueError(f"Invalid strategy")

    return data["strategy"], data["task_name"], data["prompt_files"]

def include_comparison_scores(responses, models):
    """Gets cosine similarity and BLEU scores for models outputs and updates responses dictionary
    Args:
        responses (dict): Dictionary consisting of task name, strategy, and model outputs
        models (list[str]): List of models
    """
    responses["bleu_scores"] = []
    responses["similarity_scores"] = []

    for i, (output1, output2) in enumerate(zip(responses[f"{models[0]}_output"], responses[f"{models[1]}_output"])):
        try:
            if not output1 or not output2:
                raise ValueError("Empty model output string.")

            bleu_score = get_bleu_4_score(output1, output2)
            similarity_score = get_cosine_similarity(output1, output2)

        except Exception as e:
            print(f"[Warning] Skipping comparison for pair {i} due to error: {e}")
            bleu_score = None
            similarity_score = None

        responses["bleu_scores"].append(bleu_score)
        responses["similarity_scores"].append(similarity_score)

    return responses
   
def save_responses(responses, models):
    """
    Saves models' response data into JSON and text files
    Args:
        responses (dict): Dictionary consisting of task name, strategy, and model outputs
        models (list[str]): List of models
    Output:
        Saved JSON file with model response data and text files containing model outputs
    """

    strategy_codes = {"self_consistency": "sc", 
                    "prompt_chaining": "pc", 
                    "zero_shot": "zs", 
                    "few_shot": "fs", 
                    "chain_of_thought": "cot"}
    
    task_name, code = responses["task_name"], strategy_codes[responses["strategy"]]

    output_json_file = os.path.join(RESPONSES_DIR, f"{task_name}_{code}_responses.json")
    print(f"Saving model reponses to {output_json_file}")
    with open(output_json_file, 'w') as file:
        json.dump(responses, file, indent=4)

    for model in models:
        
        for i, model_output in enumerate(responses[f"{model}_output"]):
            output_text_file = os.path.join(RESPONSES_DIR, 'response_text', f"{task_name}_{code}_{model}_{i}_response.txt")
            with open(output_text_file, 'w') as f:
                f.write(model_output)    

def run_single_prompt(strategy, task_name, prompt_files, models, client):
    """
    Prompts models with one prompt and generates a response
    Used for prompting strategies: zero shot, few shot, and chain-of-thought

    Args:
        strategy (str): Prompting strategy
        task_file (str): Filename of the JSON file
        prompt_files (list[str]): List of filenames containing prompts
        models (list[str]): List of models
        client 
    Returns:
        responses (dict): Dictionary consisting of task name, strategy, and model outputs
    """

    if len(prompt_files) != 1:
        raise ValueError(f"Should have only one prompt file. Found {len(prompt_files)}")

    responses = {"task_name": task_name, "strategy": strategy}

    prompt = load_prompt(prompt_files[0])
    messages = [{"role": "user","content": prompt}]

    for model in models:
        responses[f"{model}_output"] = [generate_response(model, messages, client)]

    return responses
    
def run_multiple_prompts(strategy, task_name, prompt_files, models, client):
    """
    Prompts models with multiple prompt and generates responses
    Used for prompting strategies: self-consistency and prompt chaining

    If the strategy is self-consistency, we repeat the same prompt three times.
    If the strategy is prompt-chaining, we chain prompts by storing previous inputs/outputs for the given task

    Args:
        strategy (str): Prompting strategy
        task_file (str): Filename of the JSON file
        prompt_files (list[str]): List of filenames containing prompts
        models (list[str]): List of models
        client 
    Returns:
        responses (dict): Dictionary consisting of task name, strategy, and model outputs
    """

    responses = {"task_name": task_name, "strategy": strategy}

    if strategy == "self_consistency":
        prompt = load_prompt(prompt_files[0])
        messages = [{"role": "user","content": prompt}]

        for model in models:
            outputs = []
            for i in range(3): # Repeat prompt 3 different times for self-consistency
                output = generate_response(model, messages, client)
                outputs.append(output)

            responses[f"{model}_output"] = outputs

    elif strategy == "prompt_chaining":
        for model in models:
            messages = [{"role": "system", "content": "You are a helpful coding assistant."}]
            chained_outputs = []
            for prompt_file in prompt_files:
                prompt = load_prompt(prompt_file)

                messages.append({"role": "user","content": prompt})

                output = generate_response(model, messages, client)
                messages.append({"role": "assistant", "content": output})

                chained_outputs.append(output)

            responses[f"{model}_output"] = chained_outputs

    
    return responses


def run(task_file, models, client):
    """
    Workflow for processing JSON file consisting of the task, prompting strategy, and prompt text files
    and generating and saving model responses in a separate JSON file

    Args:
        task_file (str): Filename of the JSON file
        models (list[str]): List of models
        client
    Output:
        Saved JSON file with model response data and text files containing model outputs
    """
    print(f"Processing {task_file}...")

    try:
        strategy, task_name, prompt_files = parse_json_file(task_file)
        print(f"Parsed JSON file: strategy - {strategy}, task name - {task_name}, prompt_files - {prompt_files}")
    except Exception as err:
        return

    if strategy == "zero_shot" or strategy == "few_shot" or strategy == "chain_of_thought":
        responses = run_single_prompt(strategy, task_name, prompt_files, models, client)
    elif strategy == "self_consistency" or strategy == "prompt_chaining":
        responses = run_multiple_prompts(strategy, task_name, prompt_files, models, client)

    responses = include_comparison_scores(responses, models)
    save_responses(responses, models)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class = argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--prompts_dir", type = str, default = 'prompts', help = "Directory with prompts")
    parser.add_argument("--responses_dir", type = str, default = 'responses', help = 'Directory to save model responses')
    parser.add_argument("--models", type = str, nargs="*", default = ['gpt-4o-mini', 'Codestral-2501'], help = "List of models (only two allowed!)")

    args = parser.parse_args()

    if not os.path.exists(args.prompts_dir):
        print("Prompt directory does not exist! Terminating run.")
        sys.exit(1)
    else:
        PROMPTS_DIR = args.prompts_dir

    RESPONSES_DIR = args.responses_dir
    os.makedirs(os.path.join(RESPONSES_DIR, 'response_text'), exist_ok=True)


    models = args.models

    if not models or len(models) != 2:
        print("You must specify only two models. Terminating run.")
        sys.exit(1)

    client = OpenAI(
        base_url = "https://models.inference.ai.azure.com",
        api_key = OPENAI_API_KEY,
    )

    for prompt_file in os.listdir(PROMPTS_DIR):
        if prompt_file.endswith('.json'):
            run(os.path.join(PROMPTS_DIR, prompt_file), models, client)


