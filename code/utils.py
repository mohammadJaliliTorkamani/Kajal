import json
import os
import re

import tiktoken

import constants


def load_data(path: str):
    try:
        with open(path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data, None
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return None, e


def save_json(address, content):
    directory = os.path.dirname(address)
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Write the JSON content to the file
    with open(address, 'w', encoding='utf-8') as file:
        json.dump(content, file, ensure_ascii=False, indent=4)


def count_gpt_tokens(text: str) -> int:
    tokenizer = tiktoken.encoding_for_model(constants.LLM_MODEL)
    tokens = tokenizer.encode(text)
    return len(tokens)


def extract_json_from_string(input_string):
    try:
        # Regular expression to find JSON objects, supporting newlines
        json_pattern = re.compile(r'({.*?})', re.DOTALL)
        match = json_pattern.search(input_string)

        if match:
            json_obj = match.group(1)
            return json_obj
        else:
            return None
    except json.JSONDecodeError:
        return None


def is_not_in_list(str_corpus: list, key: str) -> bool:
    return all(key != item for item in str_corpus)


def print_nested(output: str, nest_degree: int = 0):
    if nest_degree < 0:
        nest_degree = 0
    print("\t" * nest_degree, output)


def load_datasets(input_data_path, fsl_data_path):
    dataset_1, error_message_1 = load_data(input_data_path)
    dataset_2, error_message_2 = load_data(fsl_data_path)
    return dataset_1, error_message_1, dataset_2, error_message_2
