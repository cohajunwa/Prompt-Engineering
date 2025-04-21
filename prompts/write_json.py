import os
import json
from collections import defaultdict

if __name__ == '__main__':
    # Folder containing the prompt files
    input_folder = "prompt_text"

    # Strategy dictionary
    strategy_map = {
        "pc": "prompt_chaining",
        "cot": "chain_of_thought",
        "zs": "zero_shot",
        "fs": "few_shot",
        "sc": "self_consistency"
    }

    # Group files by (task_name, strategy_code)
    grouped_files = defaultdict(list)

    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            parts = filename[:-4].split("_")  # Remove .txt and split by underscore
            if len(parts) >= 2:
                task_name = parts[0]
                strategy_code = parts[1]
                key = (task_name, strategy_code)
                grouped_files[key].append(f"{input_folder}/{filename}")

    for (task_name, strategy_code), files in grouped_files.items():
        strategy_name = strategy_map.get(strategy_code, "unknown_strategy")
        json_obj = {
            "task_name": task_name,
            "strategy": strategy_name,
            "prompt_files": sorted(files)  
        }

        output_filename = f"{task_name}_{strategy_code}.json"
        output_path = os.path.join(output_filename)
        with open(output_path, "w") as json_file:
            json.dump(json_obj, json_file, indent=4)