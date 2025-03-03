#!/usr/bin/env python
import re
import json
import argparse

def fix_prompt(text):
    """
    Fixes formatting issues in a Llama 3 prompt:
      - Replaces multiple newlines with a single newline.
      - Trims extra whitespace on each line.
      - Ensures each message block (starting with <|start_header_id|>)
        ends with an <|eot_id|> token.
    
    The prompt is expected to start with <|begin_of_text|> and end with <|end_of_text|>.
    """
    # Normalize newlines: replace any sequence of newlines with a single newline.
    text = re.sub(r'\n+', '\n', text)
    # Split text into lines and trim each line.
    lines = [line.strip() for line in text.splitlines()]

    begin_token = "<|begin_of_text|>"
    end_token = "<|end_of_text|>"
    eot_token = "<|eot_id|>"

    # Check that the text is wrapped by the expected tokens.
    if not lines or lines[0] != begin_token or lines[-1] != end_token:
        return text

    # Process inner lines (between begin and end tokens).
    inner_lines = lines[1:-1]
    fixed_lines = []
    block = []  # Collect lines belonging to one message block.

    def flush_block(block_lines):
        """If the block does not end with the eot token, add it."""
        if block_lines:
            if block_lines[-1] != eot_token:
                block_lines.append(eot_token)
        return block_lines

    for line in inner_lines:
        # A new message block starts when a line begins with <|start_header_id|>
        if line.startswith("<|start_header_id|>"):
            if block:
                fixed_lines.extend(flush_block(block))
                block = []
            fixed_lines.append(line)
        else:
            block.append(line)
    # Flush any remaining block.
    if block:
        fixed_lines.extend(flush_block(block))
    
    # Reassemble the prompt with proper begin/end tokens.
    fixed_text = begin_token + "\n" + "\n".join(fixed_lines) + "\n" + end_token
    return fixed_text

def process_file(input_file, output_file):
    """
    Processes a JSONL file, fixing the 'text' field for each JSON object,
    and writes corrected entries to the output file.
    """
    with open(input_file, "r", encoding="utf-8") as infile, \
         open(output_file, "w", encoding="utf-8") as outfile:
        for line in infile:
            try:
                data = json.loads(line)
                if "text" in data:
                    original_text = data["text"]
                    fixed_text = fix_prompt(original_text)
                    data["text"] = fixed_text
                outfile.write(json.dumps(data) + "\n")
            except json.JSONDecodeError as e:
                print(f"Skipping invalid JSON line: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fix formatting issues in Llama 3 formatted JSONL files."
    )
    parser.add_argument("--input_file", required=True, help="Path to the input JSONL file.")
    parser.add_argument("--output_file", required=True, help="Path to the output JSONL file.")
    args = parser.parse_args()
    process_file(args.input_file, args.output_file)
