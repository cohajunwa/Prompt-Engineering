# Prompt-Engineering

* [1. Introduction](#1-introduction)  
* [2. Getting Started](#2-getting-started)  
  * [2.1 Preparations](#21-preparations)  
  * [2.2 Install Packages](#22-install-packages)  
  * [2.3 Client Authentication](#23-client-authentication)  
* [3. Automating the Model Response Generation Process](#3-automating-the-model-response-generation-process)  
  * [3.1 Model Response Generation](#31-model-response-generation)  
  * [3.2 Input Formatting](#32-input-formatting)  
  * [3.3 Understanding the Outputs](#33-understanding-the-outputs)  
* [4. Report](#4-report)  
---

# **1. Introduction** 

Prompt engineering is the practice of crafting inputs to guide a large language model (LLM) toward generating a desired response. 
In this project, I explore the use of prompt engineering on 22 different tasks. For each task, I applied two different prompt strategies, 
which were input into two LLMs. In addition, I perform a comparative analysis by evaluating responses across models and 
prompting strategies using BLEU and cosine similarity (with CodeBERT). 

I wrote scripts to automate much of this process, which are described in the following sections. The prompts I wrote as well as the models'
outputs can be found in the `prompts` and `responses` folders, respectively.

---

# **2. Getting Started**  

This project is implemented in **Python 3.9+** and is compatible with **macOS, Linux, and Windows**.  

## **2.1 Preparations**  

(1) Clone the repository to your workspace:  
```shell
~ $ git clone https://github.com/cohajunwa/Prompt-Engineering.git
```

(2) Navigate into the project repository:
```
~ $ cd Prompt-Engineering
~/Prompt-Engineering $
```

(3) Set up a virtual environment and activate it:

For macOS/Linux:
```
~/Prompt-Engineering $ python -m venv ./venv/
~/Prompt-Engineering $ source venv/bin/activate
(venv) ~/Prompt-Engineering $ 
```

For Windows:
```
~/Prompt-Engineering $ python -m venv ./venv/
~/Prompt-Engineering $ ./venv/Scripts/activate
```

To deactivate the virtual environment, use the command:
```
(venv) $ deactivate
```

## **2.2 Install Packages**

Install the required dependencies:
```shell
(venv) ~/Prompt-Engineering $ pip install -r requirements.txt
```

## **2.3 Client Authentication**

This project uses the OpenAI API, which requires an API key to authenticate with the client.
At the root directory, create a `.env` file with the following line: 
```
OPENAI_API_KEY = [YOUR-API-KEY]
```
---

# **3. Automating the Model Response Generation Process**

## 3.1 Model Response Generation

The `generate.py` script automates the process of reading prompts, inputting them into the two models, and generating responses.
Given that a `prompts` directory is provided in the repository, you can
simply run 

```
(venv) ~/Prompt-Engineering $ python generate.py
```
The outputs I generated can be found in the `responses` directory.

You can also modify arguments for the prompts directory, responses directory, and the models used for generation:

```
(venv) ~/Prompt-Engineering $ python generate.py --help
usage: generate.py [-h] [--prompts_dir PROMPTS_DIR] [--responses_dir RESPONSES_DIR] [--models [MODELS ...]]

options:
  -h, --help            show this help message and exit
  --prompts_dir PROMPTS_DIR
                        Directory with prompts (default: prompts)
  --responses_dir RESPONSES_DIR
                        Directory to save model responses (default: responses)
  --models [MODELS ...]
                        List of models (only two allowed!) (default: ['gpt-4o-mini', 'Codestral-2501'])
```

The next section discusses how the inputs and outputs are formated.

## 3.2 Input Formatting

The `generate.py` script reads from a `prompts` directory, which contains a set of JSON files. Each JSON file contains the name of the task, the prompt engineering strategy, and a list of file paths to text files containing  the written prompts. Below is an example of one such JSON file:
```json
{
    "task_name": "task1",
    "strategy": "self_consistency",
    "prompt_files": [
        "prompt_text/task1_sc.txt"
    ]
}
```

Here is the prompt written in `task1_sc.txt`:
```
Summarize the functionality of the following method:

public Map <String, Integer> countWordFrequency(List <String> words) { 
	Map <String, Integer> freqMap = new HashMap <>() ; 
	for (String word : words) { 
		freqMap.put (word, freqMap.getOrDefault(word, 0) + 1); 
	} 
	return freqMap; 
}
```

If you wanted to add your own prompts, you can simply write new text files
titled as `[task_name]_[strategy_abbreviation].txt`. You can either create
your own JSON file following the model provided above or run the script
in `prompts_text` called `write_json.py`.

`generate.py` supports five types of prompt engineering strategies:
* prompt chaining (pc)
* chain of thought (cot)
* zero shot (zs)
* few shot (fs)
* self consistency (sc) [NOTE: For this strategy, `generate.py` inputs the prompt three times]

## 3.3 Understanding the Outputs

After running `generate.py`, the script outputs a set of JSON files and text files into a directory, which by default is called `responses`.
Each response JSON file is named `[task_name]_[strategy_abbreviation]_responses.json`. Here is an example of a response JSON file:
```json
{
    "task_name": "task1",
    "strategy": "self_consistency",
    "gpt-4o-mini_output": [
        "The `countWordFrequency` method takes a list of strings, `words`, as input and returns a map that represents the frequency of each word in the list. It initializes an empty `HashMap` called `freqMap`. The method iterates over each word in the `words` list and updates the frequency count for each word in the map. If a word is already present in the map, its count is incremented; if it is not present, it is added with an initial count of 1. Finally, the method returns the `freqMap`, which contains each unique word from the list as a key and its corresponding frequency as the value.",
        "The `countWordFrequency` method takes a list of strings (`words`) as input and returns a map (`freqMap`) that represents the frequency of each unique word in the list. It uses a `HashMap` to store the word as the key and its corresponding count as the value. The method iterates through each word in the input list, updating the count for each word by using the `getOrDefault` method to retrieve the current count (or 0 if the word is not yet in the map) and incrementing it by 1. Finally, it returns the frequency map containing each word and its frequency count.",
        "The `countWordFrequency` method takes a list of strings (words) as input and returns a map where each unique word is a key and its corresponding value is the number of times that word appears in the list. It initializes an empty hash map to store the word frequencies. As it iterates through each word in the list, it updates the map by using the `getOrDefault` method to either retrieve the current count of the word (or 0 if it doesn't exist) and then increments that count by 1. Finally, the method returns the populated frequency map."
    ],
    "Codestral-2501_output": [
        "The `countWordFrequency` method takes a list of strings (words) as input and returns a map that contains the frequency of each word in the list. Here's a breakdown of its functionality:\n\n1. **Input**: A `List<String>` named `words`, which contains the words to be counted.\n2. **Output**: A `Map<String, Integer>` where the keys are unique words from the input list and the values are the frequencies (counts) of those words.\n3. **Implementation**:\n   - It initializes an empty `HashMap` named `freqMap` to store the word frequencies.\n   - It iterates over each word in the input list.\n   - For each word, it checks if the word is already a key in `freqMap`:\n     - If the word is not in the map, it adds the word with an initial frequency of 1.\n     - If the word is already in the map, it increments the existing frequency by 1.\n   - Finally, it returns the `freqMap` containing the word frequencies.\n\nIn summary, this method counts how often each word appears in the input list and returns these counts in a map.",
        "The method `countWordFrequency` takes a list of strings (words) as input and returns a map that counts the frequency of each word in the list. Here is a step-by-step summary of its functionality:\n\n1. **Initialization**:\n   - It initializes an empty `HashMap` called `freqMap` to store the words as keys and their frequencies as values.\n\n2. **Iteration**:\n   - The method iterates over each word in the input list `words`.\n\n3. **Frequency Counting**:\n   - For each word, it checks if the word already exists in `freqMap`.\n   - If the word exists, it increments its current frequency by 1.\n   - If the word does not exist, it initializes its frequency to 1.\n   - This is achieved using the method `getOrDefault(word, 0)`, which returns the current frequency if the word is already in the map or 0 if it is not.\n\n4. **Return**:\n   - After iterating through all words, the method returns the `freqMap`, which now contains each word and its corresponding frequency.\n\nIn essence, the method provides a frequency count of each word in the input list, stored in a map for easy lookup.",
        "The method `countWordFrequency` takes a list of strings (words) as input and returns a map where the keys are the unique words from the list, and the values are the frequencies of those words in the list.\n\nHere's a step-by-step breakdown of its functionality:\n\n1. **Initialization**:\n   - It creates an empty `HashMap` called `freqMap` to store the word frequency.\n\n2. **Iteration**:\n   - It iterates over each word in the input list `words`.\n   - For each word in the list, it updates the `freqMap`:\n     - If the word is not already present in the map, it adds the word to the map with an initial frequency of 1.\n     - If the word is already present, it increments the frequency count by 1.\n\n3. **Return**:\n   - After processing all the words in the list, it returns the `freqMap` containing the word frequencies.\n\nIn summary, the method counts the frequency of each word in the input list and returns a map with the words as keys and their respective frequencies as values."
    ],
    "bleu_scores": [
        18.279532684081335,
        13.470065576405327,
        13.649506829847647
    ],
    "similarity_scores": [
        0.9744590520858765,
        0.9564342498779297,
        0.9612994194030762
    ]
}
```

In addition, the model output text is outputted into a subdirectory called
`response_text`.
Here is one instance of a generated response (found in: `task1_sc_Codestral-2501_0_response.txt`).

```
The `countWordFrequency` method takes a list of strings (words) as input and returns a map that contains the frequency of each word in the list. Here's a breakdown of its functionality:

1. **Input**: A `List<String>` named `words`, which contains the words to be counted.
2. **Output**: A `Map<String, Integer>` where the keys are unique words from the input list and the values are the frequencies (counts) of those words.
3. **Implementation**:
   - It initializes an empty `HashMap` named `freqMap` to store the word frequencies.
   - It iterates over each word in the input list.
   - For each word, it checks if the word is already a key in `freqMap`:
     - If the word is not in the map, it adds the word with an initial frequency of 1.
     - If the word is already in the map, it increments the existing frequency by 1.
   - Finally, it returns the `freqMap` containing the word frequencies.

In summary, this method counts how often each word appears in the input list and returns these counts in a map.
```
---

# **4. Report**
The assignment report is available in the file **GenAI for Software Development - Assignment 3.pdf**.