import argparse
import json
import re
import torch
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

def read_parallel_corpus(input_file, max_num_lines=None):
    data = []
    with open(input_file, 'r', encoding='utf-8') as file:
        for idx, line in enumerate(file):
            if max_num_lines and idx >= max_num_lines:
                break
            english, norwegian = line.strip().split('\t')
            data.append({"english": english, "norwegian": norwegian})
    return data

def write_jsonlines(data, output_file):
    with open(output_file, 'a', encoding='utf-8') as file:
        for entry in data:
            file.write(json.dumps(entry) + '\n')

def extract_numbers(text):
    return re.findall(r'\d+', text)

def calculate_semantic_distance_batch(data, model, only_embedding_model, device):
    english_sentences = [entry['english'] for entry in data]
    norwegian_sentences = [entry['norwegian'] for entry in data]
    
    english_embeddings = model.encode(english_sentences, batch_size=len(english_sentences), device=device)
    norwegian_embeddings = model.encode(norwegian_sentences, batch_size=len(norwegian_sentences), device=device)
    
    distances = cosine_similarity(english_embeddings, norwegian_embeddings)
    
    for i, entry in enumerate(data):
        semantic_distance = 1 - distances[i][i]
        if not only_embedding_model:
            english_numbers = extract_numbers(entry['english'])
            norwegian_numbers = extract_numbers(entry['norwegian'])
            if english_numbers != norwegian_numbers:
                semantic_distance = 1.0
        entry['semantic_distance'] = semantic_distance
    
    return data

def process_in_batches(data, model, batch_size, only_embedding_model, max_distance_score, output_file, device):
    for i in tqdm(range(0, len(data), batch_size)):
        batch = data[i:i+batch_size]
        processed_batch = calculate_semantic_distance_batch(batch, model, only_embedding_model, device)
        filtered_batch = [entry for entry in processed_batch if entry['semantic_distance'] <= max_distance_score]
        write_jsonlines(filtered_batch, output_file)

def main():
    parser = argparse.ArgumentParser(description='Convert parallel corpus to JSON lines and calculate semantic distance.')
    parser.add_argument('--input_file', type=str, required=True, help='Input file containing the parallel corpus.')
    parser.add_argument('--output_file', type=str, required=True, help='Output file to save the JSON lines.')
    parser.add_argument('--max_num_lines', type=int, help='Maximum number of lines to process.')
    parser.add_argument('--only_embedding_model', action='store_true', help='Use only the embedding model to calculate semantic distance.')
    parser.add_argument('--max_distance_score', type=float, default=1.0, help='Maximum distance score to include in the output.')
    parser.add_argument('--batch_size', type=int, default=512, help='Batch size for processing.')
    
    args = parser.parse_args()
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = SentenceTransformer('sentence-transformers/LaBSE', device=device)
    
    data = read_parallel_corpus(args.input_file, args.max_num_lines)
    process_in_batches(data, model, args.batch_size, args.only_embedding_model, args.max_distance_score, args.output_file, device)

if __name__ == "__main__":
    main()
