import argparse
import json
import os
import random
from transformers import GPT2Tokenizer
from tqdm import tqdm
import mmap

def parse_arguments():
    parser = argparse.ArgumentParser(description="Estimate token count in JSONL files.")
    parser.add_argument("--input_file", type=str, help="Path to the input JSONL file.")
    parser.add_argument("--input_dir", type=str, help="Path to the directory containing JSONL files.")
    parser.add_argument("--sample_size", type=int, default=1000, help="Number of lines to sample from each file.")
    return parser.parse_args()

def count_lines(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        buf = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        return sum(1 for _ in iter(buf.readline, b""))

def sample_lines(file_path, sample_size):
    samples = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= sample_size:
                break
            samples.append(json.loads(line))
    return samples

def estimate_token_count(file_path, sample_size):
    total_lines = count_lines(file_path)
    print(f"Total number of lines in {file_path}: {total_lines}")

    sampled_lines = sample_lines(file_path, sample_size)

    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    total_tokens = 0

    for line in tqdm(sampled_lines, desc=f"Tokenizing samples from {file_path}"):
        text = line.get("text", "")
        tokens = tokenizer.encode(text)
        total_tokens += len(tokens)

    avg_tokens_per_line = total_tokens / sample_size
    estimated_total_tokens = avg_tokens_per_line * total_lines
    return estimated_total_tokens / 1e9  # Convert to B tokens

def process_files_in_directory(directory, sample_size):
    markdown_lines = ["| File Name | Estimated Token Count (B) |", "| --- | ---: |"]
    total_tokens = 0.0

    for file_name in os.listdir(directory):
        if file_name.endswith(".jsonl"):
            file_path = os.path.join(directory, file_name)
            estimated_tokens = estimate_token_count(file_path, sample_size)
            markdown_lines.append(f"| {file_name} | {estimated_tokens:.1f} |")
            total_tokens += estimated_tokens

    markdown_lines.append(f"| **Total** | **{total_tokens:.1f}** |")
    markdown_output = "\n".join(markdown_lines)
    print(markdown_output)
    with open(os.path.join(directory, "token_counts.md"), 'w') as f:
        f.write(markdown_output)

def main():
    args = parse_arguments()

    if args.input_file:
        estimated_tokens = estimate_token_count(args.input_file, args.sample_size)
        print(f"Estimated token count: {estimated_tokens:.1f} B tokens")
    elif args.input_dir:
        process_files_in_directory(args.input_dir, args.sample_size)
    else:
        print("Please provide either --input_file or --input_dir.")

if __name__ == "__main__":
    main()
