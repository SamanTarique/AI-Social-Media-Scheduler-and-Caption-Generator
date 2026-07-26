import os
import glob
import pandas as pd


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
KB_FOLDER = os.path.join(SCRIPT_DIR, "Knowledge_base")


def load_knowledge():

    csv_files = sorted(glob.glob(os.path.join(KB_FOLDER, "*.csv")))

    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {KB_FOLDER}")

    csv_tables = {}
    for file in csv_files:
        name = os.path.basename(file)
        csv_tables[name] = pd.read_csv(file, on_bad_lines="skip")
        print(f" Successfully Loaded: {file}")

    print("CSV Files Successfully Loaded.\n")

   
    md_files = sorted(glob.glob(os.path.join(KB_FOLDER, "*.md")))

    if not md_files:
        raise FileNotFoundError(f"No Markdown files found in {KB_FOLDER}")

    md_documents = []
    for file in md_files:
        with open(file, "r", encoding="utf-8") as f:
            md_documents.append(f.read())
        print(f" Successfully Loaded: {file}")

    print("Markdown Files Successfully Loaded.\n")

    return csv_tables, md_documents


if __name__ == "__main__":
    csv_tables, md_data = load_knowledge()

    print("Knowledge Base Loaded Successfully!")
    total_rows = sum(len(df) for df in csv_tables.values())
    print(f"CSV files loaded: {list(csv_tables.keys())}")
    print(f"Total CSV Rows (across all files): {total_rows}")
    print(f"Total Markdown Files: {len(md_data)}")
