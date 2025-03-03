#!/usr/bin/env python
import re
import json
import argparse

def validate_gemma2_format(prompt):
    """
    Validates that the prompt follows the Gemma2 template.
    
    Each turn must be exactly in the following format:
    
    <start_of_turn>role
    [message text]<end_of_turn>
    
    Where role is either 'user' or 'model'. Multi-turn prompts are allowed.
    The regex requires the entire prompt to be one or more such blocks.
    """
    # Define a regex pattern that matches one or more turns in Gemma2 format.
    # Each turn starts with <start_of_turn> followed immediately by 'user' or 'model',
    # a newline, then any message text (non-greedy), then <end_of_turn>.
    pattern = r"^(?:<start_of_turn>(user|model)\n.*?<end_of_turn>\n?)+$"
    
    if re.match(pattern, prompt, re.DOTALL):
        return True, "Valid Gemma2 format."
    else:
        return False, "Prompt does not match the strict Gemma2 template."

def main(input_file):
    """
    Reads a JSONL file and validates the 'text' field in each JSON object using the Gemma2 format.
    Prints detailed error messages for invalid prompts.
    """
    with open(input_file, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            try:
                data = json.loads(line.strip())
                text = data.get("text", "")
                if not text:
                    print(f"Line {line_number}: Missing 'text' field.")
                    continue
                is_valid, message = validate_gemma2_format(text)
                if is_valid:
                    print(f"Line {line_number}: ✅ Valid format.")
                else:
                    print(f"Line {line_number}: ❌ Invalid format - {message}")
                    print(f"   ▶ Text preview: {text[:200]!r}...\n")
            except json.JSONDecodeError as e:
                print(f"Line {line_number}: ❌ Invalid JSON - {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate Gemma2 prompt format in JSONL files.")
    parser.add_argument("--input_file", required=True, help="Path to the input JSONL file.")
    args = parser.parse_args()
    main(args.input_file)
