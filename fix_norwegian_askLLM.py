import json
import argparse

def process_file(input_file, output_file, min_translation_score, verbose):
    total_valid_entries = 0
    total_errors = 0
    low_translation_score_count = 0

    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for index, line in enumerate(infile):
            try:
                data = json.loads(line)
                askLLMresult_str = data.get("askLLMresult", "")
                
                if isinstance(askLLMresult_str, str):
                    askLLMresult = json.loads(askLLMresult_str)
                    
                    valid_score = True
                    for msg in askLLMresult:
                        if "translation_score" in msg:
                            try:
                                score = int(msg["translation_score"])
                                if score < min_translation_score:
                                    valid_score = False
                                    low_translation_score_count += 1
                                    break
                            except ValueError:
                                valid_score = False
                                total_errors += 1
                                if verbose:
                                    print(f"Invalid translation score at line {index + 1}: {msg['translation_score']}")
                    
                    if valid_score:
                        askLLMresult = [msg for msg in askLLMresult if msg and "from" in msg and "value" in msg]  # Remove empty and incomplete dictionaries
                        for msg in askLLMresult:
                            msg.pop("translation_quality", None)
                            msg.pop("translation_score", None)
                        data["askLLMresult"] = askLLMresult
                        if askLLMresult:  # Ensure non-empty result
                            outfile.write(json.dumps(data, ensure_ascii=False) + "\n")
                            total_valid_entries += 1
                else:
                    total_errors += 1
                    if verbose:
                        print(f"askLLMresult is not a string at line {index + 1}")
            
            except (json.JSONDecodeError, TypeError) as e:
                total_errors += 1
                if verbose:
                    print(f"JSON decode error at line {index + 1}: {str(e)}")
                continue

    print(f"Processing complete. Total valid entries: {total_valid_entries}.")
    print(f"Total errors: {total_errors}.")
    print(f"Total low translation score entries: {low_translation_score_count}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a JSONL file to filter entries based on translation score.")
    parser.add_argument("--input_file", required=True, help="Path to the input JSONL file.")
    parser.add_argument("--output_file", required=True, help="Path to the output JSONL file.")
    parser.add_argument("--min_translation_score", type=int, default=3, help="Minimum translation score to include an entry.")
    parser.add_argument("--verbose", action='store_true', help="If set, output detailed error messages.")

    args = parser.parse_args()
    process_file(args.input_file, args.output_file, args.min_translation_score, args.verbose)
