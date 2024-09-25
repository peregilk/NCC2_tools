import argparse
import json
from transformers import AutoTokenizer

def process_file(input_file, output_file):
    tokenizer = AutoTokenizer.from_pretrained("north/llama3-8b-reference")
    max_tokens = 128000
    separator = "<s>"

    concatenated_text = ""
    concatenated_ids = []
    current_tokens_count = 0

    def write_jsonl(id_list, text):
        with open(output_file, 'a', encoding='utf-8') as out_f:
            out_f.write(json.dumps({"id": "__".join(id_list), "text": text}) + "\n")

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            text = data.get('text', '')
            id = data.get('id', '')
            
            tokens = tokenizer.tokenize(text)
            tokens_count = len(tokens)
            separator_tokens_count = len(tokenizer.tokenize(separator))

            # If adding the new text exceeds the max token limit, write the current concatenated text to the output file
            if current_tokens_count + tokens_count + separator_tokens_count > max_tokens:
                write_jsonl(concatenated_ids, concatenated_text)
                concatenated_text = ""
                concatenated_ids = []
                current_tokens_count = 0
            
            # Append the text to the concatenated text
            if concatenated_text:
                concatenated_text += f" {separator} {text}"
                current_tokens_count += separator_tokens_count
            else:
                concatenated_text = text

            concatenated_ids.append(id)
            current_tokens_count += tokens_count

        # Write any remaining concatenated text
        if concatenated_text:
            write_jsonl(concatenated_ids, concatenated_text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Concatenate text fields from a JSONL file up to 128,000 tokens per line.")
    parser.add_argument("--input_file", type=str, required=True, help="Path to the input JSONL file.")
    parser.add_argument("--output_file", type=str, required=True, help="Path to the output JSONL file.")
    
    args = parser.parse_args()
    process_file(args.input_file, args.output_file)
