import argparse

def merge_files(files, unique_only):
    seen = set()
    for fname in files:
        with open(fname, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.rstrip("\\n")
                if not unique_only:
                    print(line)
                elif line not in seen:
                    seen.add(line)
                    print(line)

def delete_entries(from_file, delete_file):
    delete_set = set()
    with open(delete_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            delete_set.add(line.rstrip("\\n"))
    with open(from_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.rstrip("\\n")
            if line not in delete_set:
                print(line)

def filter_length(file, min_len, max_len):
    with open(file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.rstrip("\\n")
            if min_len <= len(line) <= max_len:
                print(line)

def main():
    parser = argparse.ArgumentParser(
        description="Wordlist Toolkit - Swiss Army Knife für Wordlists"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Merge
    merge_parser = subparsers.add_parser("merge", help="Wordlists zusammenfügen")
    merge_parser.add_argument("files", nargs="+", help="Input-Dateien")
    merge_parser.add_argument("--unique", action="store_true", help="Nur eindeutige Einträge behalten")

    # Delete
    delete_parser = subparsers.add_parser("delete", help="Einträge aus Datei löschen")
    delete_parser.add_argument("from_file", help="Zieldatei (die große)")
    delete_parser.add_argument("delete_file", help="Datei mit zu entfernenden Wörtern")

    # Filter nach Länge
    filter_parser = subparsers.add_parser("filter-length", help="Nach Wortlänge filtern")
    filter_parser.add_argument("file", help="Input-Datei")
    filter_parser.add_argument("min_len", type=int, help="Minimale Länge")
    filter_parser.add_argument("max_len", type=int, help="Maximale Länge")

    args = parser.parse_args()

    if args.command == "merge":
        merge_files(args.files, args.unique)
    elif args.command == "delete":
        delete_entries(args.from_file, args.delete_file)
    elif args.command == "filter-length":
        filter_length(args.file, args.min_len, args.max_len)

if __name__ == "__main__":
    main()
"""

# Speichern als Datei
with open("/mnt/data/wltool.py", "w") as f:
    f.write(code)

"/mnt/data/wltool.py"
