import argparse
import json
from transformers import AutoTokenizer

def count_tokens(input_file):
    tokenizer = AutoTokenizer.from_pretrained("north/llama3-8b-reference")

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            text = data.get('text', '')
            tokens = tokenizer.tokenize(text)
            print(f"Number of tokens: {len(tokens)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate the number of tokens in text fields of a JSONL file.")
    parser.add_argument("--input_file", type=str, required=True, help="Path to the input JSONL file.")
    
    args = parser.parse_args()
    count_tokens(args.input_file)
