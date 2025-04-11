#!/usr/bin/env python3

import os
import json
import argparse

publicnnewspaperurndict = {}

def logerror(tag, msg):
    print(f"[{tag}] ERROR: {msg}")

def readpublicnewspaperurnfile():
    filename = "publicurnnewspaper.lst"
    if not os.path.exists(filename):
        logerror("init", f"{filename} does not exist")
        exit(1)

    with open(filename, "r", encoding="utf-8") as fp:
        for line in fp:
            clean_line = line.strip()
            if len(clean_line) > 4:
                publicnnewspaperurndict[clean_line] = 1

def ispublicnewspaper(urn: str) -> bool:
    """Check if the provided URN exists in our loaded dictionary."""
    return urn in publicnnewspaperurndict

def build_urn_from_id(doc_id: str) -> str:
    """
    Example doc_id:
      firdafolkeblad_null_null_19680801_63_56_1_MODSMD_ARTICLE8
    Transform into:
      digavis_firdafolkeblad_null_null_19680801_63_56_1
    """
    parts = doc_id.split("_")
    if len(parts) < 7:
        return ""
    return "digavis_" + "_".join(parts[:7])

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Filter lines in a JSON-lines file according to the following rules:\n"
            " 1) If doc_type == 'newspaper_ocr', only keep if its URN is listed in publicurnnewspaper.lst.\n"
            " 2) If doc_type in ['newspapers_online_nb', 'newspapers_online_nn'], always delete.\n"
            " 3) Otherwise, keep all lines.\n"
        )
    )
    parser.add_argument("--input_file", required=True, help="Path to the JSON-lines file.")
    parser.add_argument("--output_file", required=True, help="Path to the new JSON-lines file.")
    args = parser.parse_args()

    # Load the public newspaper URN list into memory
    readpublicnewspaperurnfile()

    lines_deleted = 0
    lines_kept = 0

    with open(args.input_file, "r", encoding="utf-8") as fp, \
         open(args.output_file, "w", encoding="utf-8") as out_fp:

        for line in fp:
            line_stripped = line.strip()
            if not line_stripped:
                lines_deleted += 1
                #print("Deleted - NO_ID - EMPTY_LINE")
                continue

            try:
                data = json.loads(line_stripped)
            except json.JSONDecodeError:
                lines_deleted += 1
                print("Deleted - INVALID_JSON - UNKNOWN_DOCTYPE")
                continue

            doc_id = data.get("id", "NO_ID")
            doc_type = data.get("doc_type", "NO_DOCTYPE")

            # 1) If doc_type == "newspaper_ocr", check URN in dictionary.
            if doc_type == "newspaper_ocr":
                urn = build_urn_from_id(doc_id)
                if not ispublicnewspaper(urn):
                    lines_deleted += 1
                    #print(f"Deleted - {doc_id} - {doc_type}")
                    continue
                # Keep if URN is valid
                out_fp.write(line_stripped + "\n")
                lines_kept += 1

            # 2) If doc_type in ["newspapers_online_nb", "newspapers_online_nn"], always delete.
            elif doc_type in ["newspapers_online_nb", "newspapers_online_nn"]:
                lines_deleted += 1
                #print(f"Deleted - {doc_id} - {doc_type}")
                continue

            # 3) Otherwise, keep lines with other doc_types.
            else:
                out_fp.write(line_stripped + "\n")
                lines_kept += 1

    print(f"Number of lines deleted: {lines_deleted}")
    print(f"Number of lines kept: {lines_kept}")

if __name__ == "__main__":
    main()
