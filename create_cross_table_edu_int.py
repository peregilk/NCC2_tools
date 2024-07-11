import pandas as pd
import json
import argparse

def read_jsonlines(filepath, limit=None):
    data = []
    with open(filepath, 'r', encoding='utf-8') as file:
        for i, line in enumerate(file):
            if limit is not None and i >= limit:
                break
            data.append(json.loads(line))
    return data

def create_cross_table(data, input_file):
    df = pd.DataFrame(data)
    if 'int_score' not in df.columns or 'ling_int_score' not in df.columns:
        print(f"There are no values like 'int_score' or 'ling_int_score' in {input_file}")
        return None
    df = df.sort_values(by='int_score')
    cross_table = pd.crosstab(df['int_score'], df['ling_int_score'], normalize='index') * 100
    return cross_table

def create_int_score_table(data, input_file):
    df = pd.DataFrame(data)
    if 'int_score' not in df.columns:
        print(f"There are no values like 'int_score' in {input_file}")
        return None
    df = df.sort_values(by='int_score')
    int_score_table = df['int_score'].value_counts(normalize=True).sort_index() * 100
    int_score_table.index.name = 'edu_int_score'
    int_score_table.name = 'percentage'
    return int_score_table

def create_ling_int_score_table(data, input_file):
    df = pd.DataFrame(data)
    if 'ling_int_score' not in df.columns:
        print(f"There are no values like 'ling_int_score' in {input_file}")
        return None
    df = df.sort_values(by='int_score')
    ling_int_score_table = df['ling_int_score'].value_counts(normalize=True).sort_index() * 100
    ling_int_score_table.index.name = 'ling_int_score'
    ling_int_score_table.name = 'percentage'
    return ling_int_score_table

def main(input_file, edu, ling, limit):
    data = read_jsonlines(input_file, limit)
    
    print(input_file)  # Print the input file name
    
    if edu:
        int_score_table = create_int_score_table(data, input_file)
        if int_score_table is not None:
            markdown_table = int_score_table.to_markdown()
            print(markdown_table)
    elif ling:
        ling_int_score_table = create_ling_int_score_table(data, input_file)
        if ling_int_score_table is not None:
            markdown_table = ling_int_score_table.to_markdown()
            print(markdown_table)
    else:
        cross_table = create_cross_table(data, input_file)
        if cross_table is not None:
            markdown_table = cross_table.to_markdown()
            print(markdown_table)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create tables from JSON lines file.")
    parser.add_argument('--input_file', type=str, required=True, help='Path to the input JSON lines file.')
    parser.add_argument('--edu', action='store_true', help='Create table for edu_int_score only.')
    parser.add_argument('--ling', action='store_true', help='Create table for ling_int_score only.')
    parser.add_argument('--limit', type=int, help='Limit the number of lines read from the file.')

    args = parser.parse_args()
    main(args.input_file, args.edu, args.ling, args.limit)
