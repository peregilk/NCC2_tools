import argparse
import json
import random
from tqdm import tqdm

def process_dataset(input_file, output_file, direction, max_distance, num_shots):
    # Load the dataset
    print("Loading dataset...")
    data = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            record = json.loads(line)
            if record['semantic_distance'] <= max_distance:
                data.append(record)
    
    print("Loaded dataset. Total records after filtering:", len(data))
    
    with open(output_file, 'w', encoding='utf-8') as f:
        i = 0
        while i < len(data):
            num_shots_actual = random.randint(1, 9) if num_shots is None else num_shots
            indices = range(i, min(i + num_shots_actual, len(data)))
            i += num_shots_actual
            
            text_parts = []
            for idx in indices:
                try:
                    norwegian = data[idx]['norwegian']
                    english = data[idx]['english']
                    
                    if direction == "enno":
                        combined_text = f'Translate the following text from English to Norwegian: "{english}" {norwegian}'
                    elif direction == "noen":
                        combined_text = f'Oversett følgende tekst fra norsk til engelsk: "{norwegian}" {english}'
                    else:
                        raise ValueError('Invalid direction parameter. Use "enno" or "noen".')
                    
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
                    "source": input_file,
                    "num_shots": num_shots_actual,
                    "text": text
                }
                f.write(json.dumps(record) + '\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process a translation dataset and convert to JSONLines format.')
    parser.add_argument('--input_file', type=str, required=True, help='Path to the input JSONLines file')
    parser.add_argument('--output_file', type=str, required=True, help='Path to the output JSONLines file')
    parser.add_argument('--direction', type=str, required=True, choices=['enno', 'noen'], help='Translation direction: "enno" or "noen"')
    parser.add_argument('--max_distance', type=float, default=0.1, help='Maximum distance to include a record, between 0 and 1')
    parser.add_argument('--num_shots', type=int, choices=range(1, 10), help='Number of examples to include in each text field, between 1 and 9. If not set, a random number between 1 and 9 will be used.')

    args = parser.parse_args()
    process_dataset(args.input_file, args.output_file, args.direction, args.max_distance, args.num_shots)
