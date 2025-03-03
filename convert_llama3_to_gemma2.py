#!/usr/bin/env python
import re
import json
import argparse

def convert_llama3_to_gemma2(prompt):
    """
    Converts a Llama3-formatted prompt to a Gemma2-formatted prompt.
    
    Llama3 prompt is assumed to have:
      <|begin_of_text|>
      <|start_header_id|>role<|end_header_id|>
      message text
      <|eot_id|>
      ... (possibly repeated)
      <|end_of_text|>
      
    Gemma2 prompt requires turns in this format:
      <start_of_turn>user
      [User's message text]<end_of_turn>
      <start_of_turn>model
      [Model's message text]<end_of_turn>
      
    System messages are ignored.
    """
    begin_token = "<|begin_of_text|>"
    end_token = "<|end_of_text|>"
    
    if not (prompt.startswith(begin_token) and prompt.endswith(end_token)):
        raise ValueError("Prompt does not have proper Llama3 wrapping tokens.")
    
    # Extract inner content
    inner = prompt[len(begin_token):-len(end_token)].strip()
    
    # Regex to extract each block:
    # Matches: <|start_header_id|>role<|end_header_id|> followed by message text until <|eot_id|>
    pattern = r"<\|start_header_id\|>(.*?)<\|end_header_id\|>\s*(.*?)\s*<\|eot_id\|>"
    blocks = re.findall(pattern, inner, re.DOTALL)
    
    gemma2_lines = []
    for role, message in blocks:
        role = role.strip().lower()
        message = message.strip()
        if role == "system":
            # Optionally ignore system messages.
            continue
        elif role == "user":
            gemma2_role = "user"
        elif role == "assistant":
            gemma2_role = "model"
        else:
            # Skip unknown roles.
            continue
        gemma2_lines.append(f"<start_of_turn>{gemma2_role}")
        gemma2_lines.append(message)
        gemma2_lines.append("<end_of_turn>")
    
    # Join the blocks with newlines.
    gemma2_prompt = "\n".join(gemma2_lines)
    return gemma2_prompt

def process_file(input_file, output_file):
    """
    Reads a JSONL file with Llama3 prompts (in the "text" field),
    converts each to Gemma2 format, and writes them to an output JSONL file.
    """
    with open(input_file, "r", encoding="utf-8") as infile, \
         open(output_file, "w", encoding="utf-8") as outfile:
        for line in infile:
            try:
                data = json.loads(line)
                text = data.get("text", "")
                if text:
                    try:
                        converted = convert_llama3_to_gemma2(text)
                        data["text"] = converted
                    except ValueError as e:
                        print(f"Skipping line due to conversion error: {e}")
                outfile.write(json.dumps(data) + "\n")
            except json.JSONDecodeError as e:
                print(f"Skipping invalid JSON line: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert prompts from the Llama3 template to the Gemma2 template in JSONL files."
    )
    parser.add_argument("--input_file", required=True, help="Path to the input JSONL file with Llama3 prompts.")
    parser.add_argument("--output_file", required=True, help="Path to the output JSONL file with Gemma2 prompts.")
    args = parser.parse_args()
    process_file(args.input_file, args.output_file)
