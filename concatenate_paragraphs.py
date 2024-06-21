import json
import argparse

def process_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            record = json.loads(line)
            # Ensure id is a string
            record['id'] = str(record['id'])
            # Concatenate text from paragraphs
            concatenated_text = "\n".join(paragraph['text'] for paragraph in record.get('paragraphs', []))
            # Replace paragraphs with the concatenated text
            record['text'] = concatenated_text
            # Remove paragraphs field
            record.pop('paragraphs', None)
            # Write the processed record to the output file
            json.dump(record, outfile)
            outfile.write('\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process JSONL file to concatenate paragraph texts.')
    parser.add_argument('--input_file', type=str, required=True, help='Input JSONL file')
    parser.add_argument('--output_file', type=str, required=True, help='Output JSONL file')
    args = parser.parse_args()
    process_file(args.input_file, args.output_file)
