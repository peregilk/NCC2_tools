import argparse
import json
import random
from tqdm import tqdm
from datasets import load_dataset

def process_dataset(output_file, num_shots):
    # Load the dataset
    print("Loading dataset...")
    dataset = load_dataset("nampdn-ai/tiny-codes", split='train')
    print("Loaded dataset. Total records:", len(dataset))
    
    with open(output_file, 'w', encoding='utf-8') as f:
        i = 0
        while i < len(dataset):
            num_shots_actual = random.randint(1, 3) if num_shots is None else num_shots
            indices = range(i, min(i + num_shots_actual, len(dataset)))
            i += num_shots_actual
            
            text_parts = []
            for idx in indices:
                try:
                    prompt = dataset[idx]['prompt']
                    response = dataset[idx]['response']
                    
                    combined_text = f'{prompt}\n\n{response}'.strip()
                    text_parts.append(combined_text)
                except KeyError as e:
                    print(f"Skipping record {idx} due to missing column: {e}")
                    continue
                except Exception as e:
                    print(f"Skipping record {idx} due to error: {e}")
                    continue
            
            if text_parts:
                text = "\n\n".join(text_parts)
                record = {
                    "source": "nampdn-ai/tiny-codes",
                    "num_shots": num_shots_actual,
                    "text": text
                }
                f.write(json.dumps(record) + '\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process nampdn-ai/tiny-codes and convert to JSONLines format.')
    parser.add_argument('--output_file', type=str, required=True, help='Path to the output JSONLines file')
    parser.add_argument('--num_shots', type=int, choices=range(1, 4), help='Number of examples to include in each text field, between 1 and 3. If not set, a random number between 1 and 3 will be used.')

    args = parser.parse_args()
    process_dataset(args.output_file, args.num_shots)
