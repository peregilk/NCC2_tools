#!/usr/bin/env python
import re
import json
import argparse

def validate_llama3(prompt):
    """Updated validation with better error messages"""
    if not re.match(r"^<\|begin_of_text\|>(\s*<\|start_header_id\|>.+?<\|end_header_id\|>.+?<\|eot_id\|>\s*)+<\|end_of_text\|>$", prompt, re.DOTALL):
        raise ValueError("Invalid Llama3 structure")

def validate_gemma2(prompt):
    """Relaxed validation focusing on essential structure"""
    if not re.match(r"^(<start_of_turn>(user|model)\n.*?\n<end_of_turn>\s*)+$", prompt, re.DOTALL):
        raise ValueError("Invalid Gemma2 structure")

def convert_llama3_to_gemma2(prompt):
    """Conversion with essential checks only"""
    try:
        # Remove BOS/EOS tokens
        clean_prompt = re.sub(r"^<\|begin_of_text\|>\s*|\s*<\|end_of_text\|>$", "", prompt, flags=re.DOTALL)
        
        # Extract message pairs
        blocks = re.findall(
            r"<\|start_header_id\|>(user|assistant|system)<\|end_header_id\|>\s*([\s\S]*?)\s*<\|eot_id\|>",
            clean_prompt
        )
        
        output = []
        for role, content in blocks:
            role = role.strip().lower()
            content = content.strip()
            
            if role == "system":
                continue
                
            output.append(f"<start_of_turn>{'user' if role == 'user' else 'model'}")
            output.append(content)
            output.append("<end_of_turn>")
        
        return "\n".join(output)
    
    except Exception as e:
        raise ValueError(f"Conversion failed: {str(e)}")

def process_file(input_file, output_file):
    """Process files with strict validation and proper filtering"""
    with open(input_file, "r", encoding="utf-8") as infile, \
         open(output_file, "w", encoding="utf-8") as outfile:
        
        total = 0
        kept = 0
        errors = 0
        
        for line in infile:
            total += 1
            try:
                data = json.loads(line)
                valid = True
                
                # Process both fields
                for field in ['chosen', 'rejected']:
                    if field in data:
                        try:
                            # Convert and validate
                            converted = convert_llama3_to_gemma2(data[field])
                            validate_gemma2(converted)
                            data[field] = converted
                        except Exception as e:
                            print(f"Skipping {field} in line {total}: {str(e)}")
                            valid = False
                
                # Only write if both fields are valid
                if valid:
                    outfile.write(json.dumps(data, ensure_ascii=False) + "\n")
                    kept += 1
                else:
                    errors += 1
                    
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON at line {total}")
                errors += 1
        
        print(f"\nProcessing complete:")
        print(f"- Total entries: {total}")
        print(f"- Successfully converted: {kept}")
        print(f"- Failed conversions: {errors}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", required=True)
    parser.add_argument("--output_file", required=True)
    args = parser.parse_args()
    process_file(args.input_file, args.output_file)
