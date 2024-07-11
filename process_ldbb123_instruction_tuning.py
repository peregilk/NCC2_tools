import argparse
import json
import os
import random
from tqdm import tqdm

def load_jsonl_files(dataset_path):
    data = []
    for filename in os.listdir(dataset_path):
        if filename.endswith('.jsonl'):
            with open(os.path.join(dataset_path, filename), 'r', encoding='utf-8') as file:
                for line in file:
                    try:
                        data.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        print(f"Skipping line in {filename} due to JSON decode error: {e}")
    return data

def process_dataset(output_file, num_shots, dataset_path):
    # Load the dataset manually from JSONL files
    print("Loading dataset...")
    data = load_jsonl_files(dataset_path)
    print("Loaded dataset. Total records:", len(data))
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for i in tqdm(range(0, len(data)), desc="Processing dataset"):
            num_shots_actual = random.randint(1, 9) if num_shots is None else num_shots
            indices = range(i, min(i + num_shots_actual, len(data)))
            
            text_parts = []
            for idx in indices:
                try:
                    instruction = data[idx]['instruction']
                    input_text = data[idx]['input']
                    output = data[idx]['output']
                    
                    combined_text = f"{instruction} {input_text}\n\n{output}".strip()
                    text_parts.append(f"\"{combined_text}\"")
                except KeyError as e:
                    print(f"Skipping record {idx} due to missing column: {e}")
                    continue
                except Exception as e:
                    print(f"Skipping record {idx} due to error: {e}")
                    continue
            
            if text_parts:
                text = "\n\n".join(text_parts)
                record = {
                    "source": "ldbb123/Instruction-tuning_Datasets",
                    "num_shots": num_shots_actual,
                    "text": text
                }
                f.write(json.dumps(record) + '\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process ldbb123 Instruction-tuning Datasets and convert to JSONLines format.')
    parser.add_argument('--output_file', type=str, required=True, help='Path to the output JSONLines file')
    parser.add_argument('--num_shots', type=int, choices=range(1, 100), help='Number of examples to include in each text field, between 1 and 99. If not set, a random number between 1 and 9 will be used.')
    parser.add_argument('--dataset_path', type=str, required=True, help='Path to the downloaded dataset JSONL files')

    args = parser.parse_args()
    process_dataset(args.output_file, args.num_shots, args.dataset_path)
