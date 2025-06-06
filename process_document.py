import json
import random
import argparse
import sys
from pathlib import Path
from collections import defaultdict

def debug_print(*args, **kwargs):
    print(*args, **kwargs)
    sys.stdout.flush()

def load_templates(template_path):
    templates = []
    debug_print(f"⏳ Loading templates from: {template_path}")
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    template = json.loads(line)
                    templates.append(template['pre_prompt'])
                except (json.JSONDecodeError, KeyError) as e:
                    debug_print(f"🚨 Template error line {line_num}: {str(e)}")
                    debug_print(f"🚨 Problematic line: '{line[:50]}'")
                    sys.exit(1)
        debug_print(f"✅ Loaded {len(templates)} templates")
        return templates
    except Exception as e:
        debug_print(f"🚨 Critical template error: {str(e)}")
        sys.exit(1)

def format_gemma(template, first_para, rest):
    return (
        f"<bos><start_of_turn>user\n"
        f"{template}\n"
        f"{first_para.strip()}\n"
        f"<end_of_turn>\n"
        f"<start_of_turn>model\n"
        f"{rest.strip()}\n"
        f"<end_of_turn><eos>"
    )

def format_gemma2(template, first_para, rest):
    return (
        "<start_of_turn>user\n"
        f"{template}\n"
        f"{first_para.strip()}<end_of_turn>\n"
        "<start_of_turn>assistant\n"
        f"{rest.strip()}<end_of_turn>"
    )

def format_llama3(template, first_para, rest):
    return (
        "<|begin_of_text|>"
        "<|start_header_id|>user<|end_header_id|>\n\n"
        f"{template}\n"
        f"{first_para.strip()}\n\n"
        "<|eot_id|>\n"
        "<|start_header_id|>assistant<|end_header_id|>\n\n"
        f"{rest.strip()}\n"
        "<|eot_id|><|end_of_text|>"
    )

def find_fifth_punctuation(text):
    punctuations = {'.', '!', '?'}
    indexes = []
    for idx, char in enumerate(text):
        if char in punctuations:
            indexes.append(idx)
            if len(indexes) == 5:
                return idx + 1  # Include the punctuation
    return None

def process_documents(template_path, input_path, output_path, template_format):
    stats = defaultdict(int)
    try:
        debug_print(f"🔍 Checking input file: {input_path}")
        if not input_path.exists():
            debug_print(f"🚨 Input file not found: {input_path}")
            sys.exit(1)
            
        templates = load_templates(template_path)
        formatters = {
            'gemma': format_gemma,
            'gemma2': format_gemma2,
            'llama3': format_llama3
        }
        formatter = formatters[template_format]
        
        debug_print(f"📂 Preparing output directory: {output_path.parent}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        processed = 0
        with open(input_path, 'r', encoding='utf-8') as infile, \
             open(output_path, 'w', encoding='utf-8') as outfile:
            
            debug_print(f"🚀 Starting processing with format '{template_format}'")
            for line_num, line in enumerate(infile, 1):
                try:
                    line = line.strip()
                    if not line:
                        continue
                        
                    doc = json.loads(line)
                    if 'text' not in doc:
                        stats['missing_text'] += 1
                        debug_print(f"⚠️  Missing 'text' field in line {line_num}")
                        continue
                        
                    original_text = doc['text']
                    first_para, rest = "", ""
                    valid = False
                    split_method = ""

                    # Try newline split first
                    if '\n' in original_text:
                        parts = original_text.split('\n', 1)
                        first_para = parts[0].strip()
                        rest = parts[1].strip() if len(parts) > 1 else ""
                        split_method = "newline"
                    else:
                        # Try punctuation split if no newline
                        split_pos = find_fifth_punctuation(original_text)
                        if split_pos:
                            first_para = original_text[:split_pos].strip()
                            rest = original_text[split_pos:].strip()
                            split_method = "punctuation"
                        else:
                            stats['no_split'] += 1
                            #debug_print(f"⚠️  Line {line_num}: No valid split found")
                            continue

                    # Validate word counts
                    words_before = len(first_para.split())
                    words_after = len(rest.split())
                    
                    if words_before >= 8 and words_after >= 20:
                        valid = True
                    else:
                        stats['word_count'] += 1
                        #debug_print(f"⚠️  Line {line_num}: Invalid word counts "
                        #          f"({words_before} before, {words_after} after)")
                        continue
                    
                    if valid:
                        selected_template = random.choice(templates)
                        new_text = formatter(selected_template, first_para, rest)
                        
                        new_doc = {**doc, "text": new_text}
                        outfile.write(json.dumps(new_doc, ensure_ascii=False) + '\n')
                        processed += 1
                        stats['success'] += 1
                        
                        if processed % 100000 == 0:
                            debug_print(f"📦 Processed {processed} documents...")
                        
                except Exception as e:
                    stats['other'] += 1
                    #debug_print(f"⚠️  Error line {line_num}: {str(e)}")
                    continue
                    
            # Print final statistics
            debug_print("\n📊 Processing Statistics:")
            debug_print(f"✅ Successfully processed: {stats['success']}")
            debug_print(f"🚫 Total failures: {sum(stats.values()) - stats['success']}")
            debug_print(f"  ├─ Missing 'text' field: {stats['missing_text']}")
            debug_print(f"  ├─ No valid split found: {stats['no_split']}")
            debug_print(f"  ├─ Word count issues: {stats['word_count']}")
            debug_print(f"  └─ Other errors: {stats['other']}")
            
            debug_print(f"\n🎉 Processing complete! Total processed: {processed}")
            debug_print(f"💾 Output saved to: {output_path.resolve()}")

    except Exception as e:
        debug_print(f"🚨 Critical processing error: {str(e)}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='Process JSONL documents with template-based text transformation',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--templates', '-t', type=Path, required=True,
                       help='Path to template JSONL file')
    parser.add_argument('--input', '-i', type=Path, required=True,
                       help='Input JSONL file to process')
    parser.add_argument('--output', '-o', type=Path, required=True,
                       help='Output JSONL file path')
    parser.add_argument('--seed', '-s', type=int, default=None,
                       help='Random seed for reproducibility')
    parser.add_argument('--format', '-f', choices=['gemma', 'gemma2', 'llama3'], default='gemma',
                       help='Template format to use')

    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    process_documents(
        template_path=args.templates,
        input_path=args.input,
        output_path=args.output,
        template_format=args.format
    )

if __name__ == "__main__":
    main()
