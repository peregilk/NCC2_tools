import argparse
import json
import os

def check_jsonl_file(filepath):
    error_log = []
    with open(filepath, 'r') as file:
        for i, line in enumerate(file, 1):
            try:
                record = json.loads(line)
                text_field = record.get('text')
                if not isinstance(text_field, str):
                    raise ValueError(f"Row {i}: 'text' field is not a string.")
            except (json.JSONDecodeError, ValueError) as e:
                error_log.append((i, str(e)))
                print(f"Checking {filepath} - Error found at row {i}")
                print(f"Command to remove the error line: sed -i '{i}d' {filepath}")
    
    if not error_log:
        print(f"Checking {filepath} - No error")
    else:
        print(f"Errors found in {filepath}:")
        for row, error in error_log:
            print(f"Row {row}: {error}")

def check_jsonl_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".jsonl"):
            filepath = os.path.join(directory, filename)
            check_jsonl_file(filepath)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check JSONL files for inconsistent data types in the 'text' column.")
    parser.add_argument("--directory", type=str, help="Directory containing JSONL files.")
    parser.add_argument("--filename", type=str, help="Single JSONL file to check.")
    args = parser.parse_args()

    if args.filename:
        check_jsonl_file(args.filename)
    elif args.directory:
        check_jsonl_files(args.directory)
    else:
        print("Please provide either a directory or a filename.")
