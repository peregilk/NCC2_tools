import os
import argparse
import json
import time
from concurrent.futures import ProcessPoolExecutor
import ftfy

def fix_text(text):
    return ftfy.fix_text(text)

def process_line(data, input_filename, id_prefix, id_counter, min_words, min_edu_score, min_ling_score, fix_text_flag):
    try:
        data = json.loads(data)
    except json.JSONDecodeError:
        print("JSONDecodeError")
        return None

    # Validate and fix id
    if 'id' in data:
        if isinstance(data['id'], int):
            data['id'] = f"{id_prefix}{data['id']}"
        elif not data['id'].startswith(id_prefix):
            data['id'] = f"{id_prefix}{data['id']}"
    else:
        data['id'] = f"{id_prefix}{id_counter[0]}"
        id_counter[0] += 1

    # Validate text field
    if 'text' not in data or not isinstance(data['text'], str) or len(data['text'].split()) < min_words:
        return None

    if fix_text_flag:
        data['text'] = fix_text(data['text'])

    # Validate and rename score fields
    if 'score' in data:
        try:
            score = float(data['score'])
        except ValueError:
            print("ValueError: Invalid score")
            return None
    else:
        return None

    if 'int_score' in data:
        try:
            int_score = int(data['int_score'])
        except ValueError:
            print("ValueError: Invalid int_score")
            return None
    else:
        return None

    if 'ling_score' in data:
        try:
            ling_score = float(data['ling_score'])
        except ValueError:
            print("ValueError: Invalid ling_score")
            return None
    else:
        ling_score = None

    if (min_edu_score is not None and score < min_edu_score) or (min_ling_score is not None and (ling_score is None or ling_score < min_ling_score)):
        return None

    data['edu_score'] = score
    if ling_score is not None:
        data['ling_score'] = ling_score
    del data['score']
    del data['int_score']

    # Validate doc_type
    if 'doc_type' not in data:
        data['doc_type'] = os.path.splitext(os.path.basename(input_filename))[0]

    # Only keep specific fields
    valid_data = {
        'id': data['id'],
        'text': data['text'],
        'edu_score': data['edu_score'],
        'doc_type': data['doc_type']
    }
    if ling_score is not None:
        valid_data['ling_score'] = ling_score

    return json.dumps(valid_data)

def process_chunk(chunk, input_filename, id_prefix, id_counter, min_words, min_edu_score, min_ling_score, fix_text_flag):
    results = []
    for line in chunk:
        result = process_line(line, input_filename, id_prefix, id_counter, min_words, min_edu_score, min_ling_score, fix_text_flag)
        if result:
            results.append(result)
    return results

def read_in_chunks(file_object, chunk_size=1000):
    """Lazy function (generator) to read a file piece by piece."""
    chunk = []
    for line in file_object:
        chunk.append(line)
        if len(chunk) >= chunk_size:
            yield chunk
            chunk = []
            print(".", end="", flush=True)
    if chunk:
        yield chunk
        print(".", end="", flush=True)

def main():
    parser = argparse.ArgumentParser(description="Filter and process a JSONL dataset.")
    parser.add_argument('--input_file', required=True, help='Path to the input JSONL file.')
    parser.add_argument('--output_dir', required=True, help='Directory to save the output JSONL file.')
    parser.add_argument('--min_words', type=int, default=10, help='Minimum number of words in the text field.')
    parser.add_argument('--min_edu_score', type=float, help='Minimum value of the edu_score field.')
    parser.add_argument('--min_ling_score', type=float, help='Minimum value of the ling_score field.')
    parser.add_argument('--max_cpu_count', type=int, default=48, help='Maximum number of CPU cores to use.')
    parser.add_argument('--fix_text', action='store_true', help='Fix text using ftfy.')
    args = parser.parse_args()

    start_time = time.time()

    num_cores = min(os.cpu_count(), args.max_cpu_count)
    print(f"Using {num_cores} cores")

    input_filename = os.path.basename(args.input_file)
    output_filename = os.path.join(args.output_dir, input_filename)
    id_prefix = f"{os.path.splitext(input_filename)[0]}_"

    id_counter = [1]

    print(f"Opening {args.input_file}")

    with open(args.input_file, 'r') as infile, open(output_filename, 'w') as outfile:
        chunk_generator = read_in_chunks(infile, chunk_size=1000)
        
        with ProcessPoolExecutor(max_workers=num_cores) as executor:
            future_to_chunk = {executor.submit(process_chunk, chunk, input_filename, id_prefix, id_counter, args.min_words, args.min_edu_score, args.min_ling_score, args.fix_text): chunk for chunk in chunk_generator}

            chunk_count = 0
            for future in future_to_chunk:
                chunk_count += 1
                results = future.result()
                for result in results:
                    outfile.write(result + '\n')
                print(".", end="", flush=True)

    print(f"\nFinished processing {args.input_file}")
    end_time = time.time()
    print(f"Total processing time: {end_time - start_time} seconds")

if __name__ == "__main__":
    main()
