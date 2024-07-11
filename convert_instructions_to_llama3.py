import json
import argparse

def convert_to_llama3_format(conversation, input_file_name, index):
    prompt = "<|begin_of_text|>\n"
    role_map = {"human": "user", "gpt": "assistant"}
    
    for message in conversation:
        role = role_map.get(message["from"], "user")
        prompt += f"<|start_header_id|>{role}<|end_header_id|>\n{message['value']}<|eot_id|>\n"
    
    prompt += "<|end_of_text|>"
    return {
        "id": f"{input_file_name}_{index}",
        "text": prompt
    }

def process_file(input_file, output_file):
    input_file_name = input_file.split('/')[-1].replace('.jsonl', '')
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for index, line in enumerate(infile):
            data = json.loads(line)
            formatted_data = convert_to_llama3_format(data["conversations"], input_file_name, index + 1)
            outfile.write(json.dumps(formatted_data) + '\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert JSONL data to Llama 3 prompt format.')
    parser.add_argument('--input_file', type=str, required=True, help='The input file in JSON lines format')
    parser.add_argument('--output_file', type=str, required=True, help='The output file to write formatted data')
    
    args = parser.parse_args()
    process_file(args.input_file, args.output_file)
