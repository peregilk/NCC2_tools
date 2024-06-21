import argparse
import pandas as pd
import json
import asciichartpy as ac
import matplotlib.pyplot as plt
import os
import numpy as np

def read_scores_from_jsonl(file_path):
    scores = []
    with open(file_path, 'r') as f:
        for line in f:
            data = json.loads(line)
            if 'score' in data:
                score = data['score']
                if score < 0:
                    score = 0
                scores.append(score)
    return scores

def plot_histogram(scores, save_path=None):
    # Create a DataFrame from the scores
    df = pd.DataFrame(scores, columns=['score'])

    # Plot the histogram with fixed bins of 0.1 from 0 to 5
    bins = np.linspace(0, 5, 51)
    plt.hist(df['score'], bins=bins, edgecolor='black', alpha=0.7)
    plt.title('Score Histogram')
    plt.xlabel('Score')
    plt.ylabel('Frequency')
    plt.grid(True)
    
    if save_path:
        plt.savefig(save_path)
        print(f"Image is saved to {save_path}")
    else:
        plt.show()

def plot_histogram_ascii(scores):
    # Create histogram data with fixed bins of 0.1 from 0 to 5
    bins = np.linspace(0, 5, 51)
    counts, _ = np.histogram(scores, bins=bins)

    # Generate the ASCII histogram
    chart = ac.plot(counts.tolist(), {'height': 20})

    print(chart)

def save_bin_counts(scores, save_path):
    # Create histogram data with fixed bins of 0.1 from 0 to 5
    bins = np.linspace(0, 5, 51)
    counts, bin_edges = np.histogram(scores, bins=bins)

    # Prepare the JSONL data
    bin_data = [{"bin_start": float(bin_edges[i]), "bin_end": float(bin_edges[i+1]), "count": int(count)}
                for i, count in enumerate(counts)]

    # Save the bin counts to a JSONL file
    with open(save_path, 'w') as f:
        for item in bin_data:
            f.write(json.dumps(item) + '\n')
    print(f"Bin counts saved to {save_path}")

def main():
    parser = argparse.ArgumentParser(description="Plot histogram of scores from JSONL file")
    parser.add_argument('--input_file', type=str, required=True, help='Path to the input JSONL file')
    parser.add_argument('--ascii', action='store_true', help='Output histogram as ASCII art')
    parser.add_argument('--save_dir', type=str, help='Directory to save the histogram image and bin counts')
    args = parser.parse_args()

    # Read scores from the JSONL file
    scores = read_scores_from_jsonl(args.input_file)

    # Plot the ASCII histogram if requested
    if args.ascii:
        plot_histogram_ascii(scores)

    # Determine save paths if provided
    image_save_path = None
    jsonl_save_path = None
    if args.save_dir:
        if not os.path.exists(args.save_dir):
            os.makedirs(args.save_dir)
        file_name = os.path.splitext(os.path.basename(args.input_file))[0]
        image_save_path = os.path.join(args.save_dir, file_name + '.png')
        jsonl_save_path = os.path.join(args.save_dir, file_name + '.jsonl')

    # Plot the matplotlib histogram and save if save_path is set
    plot_histogram(scores, image_save_path)

    # Save the bin counts to a JSONL file if save_path is set
    if jsonl_save_path:
        save_bin_counts(scores, jsonl_save_path)

if __name__ == '__main__':
    main()
