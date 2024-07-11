import argparse
import json
from tqdm import tqdm

def process_dataset(input_file, output_file):
    # Load the dataset
    print("Loading dataset...")
    data = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"Skipping line due to JSON decode error: {e}")
    
    print("Loaded dataset. Total records:", len(data))
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for record in tqdm(data, desc="Processing dataset"):
            try:
                text = record['text']
                askLLMresult = record['askLLMresult']
                
                if isinstance(askLLMresult, str):
                    # Ensure askLLMresult is a valid JSON array
                    askLLMresult = f"[{askLLMresult.replace('}{', '},{')}]"
                    try:
                        askLLMresult = json.loads(askLLMresult)
                    except json.JSONDecodeError as e:
                        print(f"Skipping record due to JSON decode error in askLLMresult: {e} in record: {record['id']}")
                        continue
                else:
                    print(f"Skipping record because askLLMresult is not a string in record: {record['id']}")
                    continue
                
                combined_text_parts = []
                
                for item in askLLMresult:
                    if isinstance(item, list):
                        for sub_item in item:
                            phrase = sub_item.get('Frase')
                            named_entities = sub_item.get('Navngitte enheter')
                            if phrase is not None and named_entities is not None:
                                combined_text_parts.append(f'Frase: {phrase}\nNavngitte enheter: {json.dumps(named_entities)}')
                    elif isinstance(item, dict):
                        phrase = item.get('Frase')
                        named_entities = item.get('Navngitte enheter')
                        if phrase is not None and named_entities is not None:
                            combined_text_parts.append(f'Frase: {phrase}\nNavngitte enheter: {json.dumps(named_entities)}')
                    else:
                        print(f"Skipping non-dict item in askLLMresult: {item} in record: {record['id']}")
                
                if combined_text_parts:
                    combined_text = "Følgende er fraser og JSON-ordbøker med de navngitte enhetene som forekommer i den gitte frasen.\n\n" + "\n\n".join(combined_text_parts)
                    
                    output_record = {
                        "source": input_file,
                        "text": combined_text
                    }
                    f.write(json.dumps(output_record) + '\n')
                else:
                    print(f"Skipping record because no valid items were found in askLLMresult: {record['id']}")
            except KeyError as e:
                print(f"Skipping record due to missing column: {e} in record: {record['id']}")
                continue
            except ValueError as e:
                print(f"Skipping record due to value error: {e} in record: {record['id']}")
                continue
            except Exception as e:
                print(f"Skipping record due to error: {e} in record: {record['id']}")
                continue

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process a dataset and convert to JSONLines format.')
    parser.add_argument('--input_file', type=str, required=True, help='Path to the input JSONLines file')
    parser.add_argument('--output_file', type=str, required=True, help='Path to the output JSONLines file')

    args = parser.parse_args()
    process_dataset(args.input_file, args.output_file)
