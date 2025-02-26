#!/usr/bin/env python3
import pandas as pd
from fuzzywuzzy import fuzz
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def full_name(row):
    return f"{row['first_name'].strip().lower()} {row['middle_name'].strip().lower() if pd.notnull(row['middle_name']) else ''} {row['last_name'].strip().lower()}".strip()

def identify_duplicates(df, threshold=90):
    """
    Identifies duplicate or misspelled names based on fuzzy matching of full names.
    """
    df['full_name'] = df.apply(full_name, axis=1)
    duplicates = []
    seen = set()
    for i in range(len(df)):
        name_i = df.loc[i, 'full_name']
        if i in seen:
            continue
        group = [i]
        for j in range(i+1, len(df)):
            name_j = df.loc[j, 'full_name']
            score = fuzz.token_set_ratio(name_i, name_j)
            if score >= threshold:
                group.append(j)
                seen.add(j)
        if len(group) > 1:
            duplicates.append(group)
    return duplicates

def main():
    parser = argparse.ArgumentParser(description="Duplicate/Misspelled Name Detection Utility")
    parser.add_argument("--input", required=True, help="Input CSV file path containing first_name, middle_name, last_name columns")
    parser.add_argument("--threshold", type=int, default=90, help="Fuzzy matching threshold (default: 90)")
    args = parser.parse_args()

    try:
        df = pd.read_csv(args.input)
        logging.info(f"Input data loaded from {args.input}.")
    except Exception as e:
        logging.error(f"Error reading input file: {e}")
        return

    duplicates = identify_duplicates(df, args.threshold)
    if duplicates:
        logging.info(f"Found {len(duplicates)} groups of duplicate/misspelled names.")
        for group in duplicates:
            print("Duplicate group:")
            for idx in group:
                print(f"  {df.loc[idx, ['first_name', 'middle_name', 'last_name']].to_dict()}")
    else:
        logging.info("No duplicate or misspelled names detected.")

if __name__ == "__main__":
    main()
