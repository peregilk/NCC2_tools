import argparse
import json
import os
import random
from transformers import AutoTokenizer
from tqdm import tqdm
import mmap

def parse_arguments():
    parser = argparse.ArgumentParser(description="Estimate token count in JSONL files using Llama 3 tokenizer.")
    parser.add_argument("--input_file", type=str, help="Path to the input JSONL file.")
    parser.add_argument("--input_dir", type=str, help="Path to the directory containing JSONL files.")
    parser.add_argument("--sample_size", type=int, default=1000, help="Number of lines to sample from each file.")
    return parser.parse_args()

def count_lines(file_path):
    try:
        # Check if file is empty first
        if os.path.getsize(file_path) == 0:
            return 0
            
        with open(file_path, 'r', encoding='utf-8') as f:
            buf = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            return sum(1 for _ in iter(buf.readline, b""))
    except ValueError:
        print(f"⚠️  Empty file detected: {file_path}")
        return 0

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

    # Initialize Llama 3 tokenizer with extended context
    tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B")
    tokenizer.model_max_length = 131072  # 128k context window
    tokenizer.deprecation_warnings["sequence-length-is-long"] = False

    sampled_lines = sample_lines(file_path, sample_size)
    total_tokens = 0

    for line in tqdm(sampled_lines, desc=f"Tokenizing samples from {file_path}"):
        text = line.get("text", "")
        # Encode without truncation or padding
        tokens = tokenizer.encode(text, truncation=False, add_special_tokens=False)
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
            
            # Skip empty files immediately
            if os.path.getsize(file_path) == 0:
                print(f"⚠️  Skipping empty file: {file_name}")
                continue
                
            estimated_tokens = estimate_token_count(file_path, sample_size)
            
            # Skip files with 0 estimated tokens
            if estimated_tokens <= 0:
                print(f"⚠️  Skipping file with 0 tokens: {file_name}")
                continue
                
            markdown_lines.append(f"| {file_name} | {estimated_tokens:.3f} |")
            total_tokens += estimated_tokens

    markdown_lines.append(f"| **Total** | **{total_tokens:.3f}** |")
    markdown_output = "\n".join(markdown_lines)
    print(markdown_output)
    with open(os.path.join(directory, "token_counts.md"), 'w') as f:
        f.write(markdown_output)


def main():
    args = parse_arguments()

    if args.input_file:
        estimated_tokens = estimate_token_count(args.input_file, args.sample_size)
        print(f"Estimated token count: {estimated_tokens:.3f} B tokens")
    elif args.input_dir:
        process_files_in_directory(args.input_dir, args.sample_size)
    else:
        print("Please provide either --input_file or --input_dir.")

if __name__ == "__main__":
    main()
