import re
import argparse
import json

def validate_prompt_format(prompt):
    """
    Validates the Llama 3 prompt format with loosened requirements for whitespace.
    Returns a tuple (is_valid, error_message).
    """
    expected_start = "<|begin_of_text|>"
    expected_end = "<|end_of_text|>"
    
    # Check start/end tokens
    if not prompt.startswith(expected_start):
        return False, f"Prompt does not start with '{expected_start}'."
    if not prompt.endswith(expected_end):
        return False, f"Prompt does not end with '{expected_end}'."
    
    # Remove wrapping tokens and trim surrounding whitespace
    core_prompt = prompt[len(expected_start):-len(expected_end)].strip()
    
    # Loosen the regex by allowing any whitespace (\s*) around tokens.
    # Optional system block:
    system_pattern = r"(?:(<\|start_header_id\|>\s*system\s*<\|end_header_id\|>\s*.*?\s*<\|eot_id\|>\s*))?"
    # At least one user block is required:
    user_pattern = r"((<\|start_header_id\|>\s*user\s*<\|end_header_id\|>\s*.*?\s*<\|eot_id\|>\s*))+"
    # Optional assistant block(s):
    assistant_pattern = r"((<\|start_header_id\|>\s*assistant\s*<\|end_header_id\|>\s*.*?\s*<\|eot_id\|>\s*))*"
    
    full_pattern = f"^{system_pattern}{user_pattern}{assistant_pattern}$"
    
    if not re.match(full_pattern, core_prompt, re.DOTALL):
        return False, "Prompt structure does not match the expected (loosened) format."
    
    return True, "Valid format."

def main(input_file):
    """
    Reads a JSONL file and validates the 'text' field in each JSON object.
    Prints detailed error messages for invalid prompts.
    """
    with open(input_file, 'r', encoding='utf-8') as file:
        for line_number, line in enumerate(file, start=1):
            try:
                data = json.loads(line.strip())
                text = data.get("text", "")
                if not text:
                    print(f"Line {line_number}: Missing 'text' field.")
                    continue

                is_valid, message = validate_prompt_format(text)
                if is_valid:
                    ...
                    # print(f"Line {line_number}: ✅ Valid format.")
                else:
                    print(f"Line {line_number}: ❌ Invalid format - {message}")
                    print(f"   ▶ Text preview: {text[:200]!r}...\n")
            except json.JSONDecodeError as e:
                print(f"Line {line_number}: ❌ Invalid JSON - {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Loosened validation for Llama 3 prompt format in JSONL files.")
    parser.add_argument("--input_file", required=True, help="Path to the input JSONL file.")
    args = parser.parse_args()
    main(args.input_file)
