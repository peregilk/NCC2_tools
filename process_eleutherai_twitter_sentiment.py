import argparse
import json
import random
from datasets import load_dataset
from tqdm import tqdm

def convert_label(label, language):
    if language == "no":
        return "Positiv" if label == 1 else "Negativ"
    else:
        return "Positive" if label == 1 else "Negative"

def process_dataset(output_file, num_shots, language):
    # Load the dataset
    dataset = load_dataset('EleutherAI/twitter-sentiment', split='train')

    with open(output_file, 'w', encoding='utf-8') as f:
        for i in tqdm(range(0, len(dataset), num_shots if num_shots else random.randint(1, 9)), desc="Processing dataset"):
            num_shots_actual = random.randint(1, 9) if num_shots is None else num_shots
            indices = range(i, min(i + num_shots_actual, len(dataset)))
            
            text_parts = []
            for idx in indices:
                shot_text = dataset[idx]['text']
                shot_label = dataset[idx]['label']
                shot_label_text = convert_label(shot_label, language)
                if language == "no":
                    text_parts.append(f"Hva er sentimentet i denne teksten?\n\n\"{shot_text}\"\n\n\"{shot_label_text}\"")
                else:
                    text_parts.append(f"What is the sentiment in this text?\n\n\"{shot_text}\"\n\n\"{shot_label_text}\"")
            text = "\n\n".join(text_parts)

            record = {
                "source": "EleutherAI/twitter-sentiment",
                "num_shots": num_shots_actual,
                "text": text
            }
            f.write(json.dumps(record) + '\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process EleutherAI Twitter Sentiment dataset and convert to JSONLines format.')
    parser.add_argument('--output_file', type=str, required=True, help='Path to the output JSONLines file')
    parser.add_argument('--num_shots', type=int, choices=range(1, 100), help='Number of examples to include in each text field, between 1 and 99. If not set, a random number between 1 and 9 will be used.')
    parser.add_argument('--language', type=str, choices=['en', 'no'], default='en', help='Language of the output. "en" for English, "no" for Norwegian.')

    args = parser.parse_args()
    process_dataset(args.output_file, args.num_shots, args.language)
