#!/usr/bin/env python3

import argparse
import json
import glob
import os
import ftfy  # Make sure ftfy is installed: pip install ftfy

def check_and_fix_file(filename, max_text_length, fix):
    anomalies = 0
    total_lines = 0
    good_lines = []  # store valid (and possibly fixed) lines when fixing
    print(f"Processing file: {filename}")

    try:
        with open(filename, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f, start=1):
                total_lines += 1
                original_line = line
                stripped = line.strip()
                error_found = False

                # Check if the entire line is empty.
                if not stripped:
                    print(f"  Line {idx}: Empty line.")
                    anomalies += 1
                    error_found = True
                else:
                    # Check for encoding issues (replacement characters)
                    if "�" in stripped:
                        fixed_text = ftfy.fix_text(stripped)
                        if "�" in fixed_text:
                            print(f"  Line {idx}: Encoding issue detected (replacement character found) and ftfy could not fix it.")
                            anomalies += 1
                            error_found = True
                        else:
                            print(f"  Line {idx}: Encoding issue detected but ftfy fixed it.")
                            stripped = fixed_text
                            # If in fix mode, update the original line as well.
                            original_line = fixed_text + "\n"

                    # Check for valid JSON.
                    try:
                        data = json.loads(stripped)
                    except json.JSONDecodeError as e:
                        print(f"  Line {idx}: JSON parse error -> {e}")
                        anomalies += 1
                        error_found = True
                    else:
                        # Check that no string field is empty and that no field exceeds max_text_length.
                        for k, v in data.items():
                            if isinstance(v, str):
                                if v.strip() == "":
                                    print(f"  Line {idx}: Field '{k}' is empty.")
                                    anomalies += 1
                                    error_found = True
                                    break
                                if len(v) > max_text_length:
                                    print(f"  Line {idx}: Field '{k}' has {len(v)} characters, exceeds {max_text_length} chars.")
                                    anomalies += 1
                                    error_found = True
                                    break

                if fix:
                    if not error_found:
                        good_lines.append(original_line)
                # In non-fix mode, we simply report anomalies.
        if fix:
            with open(filename, "w", encoding="utf-8") as f_out:
                f_out.writelines(good_lines)
            print(f"Finished fixing {filename}. Removed {total_lines - len(good_lines)} bad lines.")
        else:
            print(f"Finished checking {filename}. Found {anomalies} anomalies in {total_lines} lines.\n")
        return anomalies, total_lines
    except OSError as e:
        print(f"Error opening file {filename}: {e}")
        return 0, 0

def main():
    parser = argparse.ArgumentParser(
        description="Check JSONL data for anomalies (valid JSON, non-empty fields, encoding issues) across multiple files. "
                    "With --fix, bad lines are removed (no backup is created)."
    )
    parser.add_argument("--input_file", required=True, nargs="+",
                        help="Glob pattern(s) for JSONL files, e.g. '*.jsonl'.")
    parser.add_argument("--max_text_length", type=int, default=10000,
                        help="Threshold for flagging overly long text fields.")
    parser.add_argument("--fix", action="store_true",
                        help="If set, remove lines with errors (no backup is created).")
    args = parser.parse_args()

    # Expand each input pattern into a list of files.
    all_files = []
    for pattern in args.input_file:
        matched = glob.glob(pattern)
        if matched:
            all_files.extend(matched)
        else:
            print(f"No files matched pattern: {pattern}")

    if not all_files:
        print("No files found for the provided pattern(s).")
        return

    total_anomalies = 0
    total_lines_processed = 0

    for file in all_files:
        anomalies, lines = check_and_fix_file(file, args.max_text_length, args.fix)
        total_anomalies += anomalies
        total_lines_processed += lines

    print(f"\nOverall summary: Processed {len(all_files)} files, {total_lines_processed} lines total. "
          f"Found {total_anomalies} anomalies overall.")

if __name__ == "__main__":
    main()
