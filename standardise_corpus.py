import argparse
import json
import os
import uuid
import pandas as pd

def process_jsonl(input_file, output_folder):
    doc_type = os.path.splitext(os.path.basename(input_file))[0]
    output_name = os.path.join(output_folder, os.path.basename(input_file))

    with open(input_file, 'r') as infile, open(output_name, 'w') as outfile:
        for idx, line in enumerate(infile):
            try:
                data = json.loads(line)
                
                # Determine the id
                if 'id' in data:
                    data_id = data['id']
                elif 'uuid' in data:
                    data_id = data['uuid']
                else:
                    data_id = idx + 1
                
                output_data = {
                    "id": f"{doc_type}_{data_id}",
                    "text": data["text"],
                    "edu_score": data.get("edu_score", float('nan')),
                    "ling_score": data.get("ling_score", float('nan')),
                    "doc_type": doc_type
                }
                
                outfile.write(json.dumps(output_data) + '\n')
            except KeyError:
                raise ValueError(f"Missing 'text' field in the input file at line {idx + 1}")
            except json.JSONDecodeError:
                raise ValueError(f"Invalid JSON format at line {idx + 1}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a JSONL file to extract specific fields.")
    parser.add_argument("--input_file", required=True, help="The input JSONL file")
    parser.add_argument("--output_folder", required=True, help="The output folder for the processed file")
    
    args = parser.parse_args()
    
    process_jsonl(args.input_file, args.output_folder)
