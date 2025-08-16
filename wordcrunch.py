#!/usr/bin/env python3

import argparse
import re

ASCII_ART = r'''
_ _  _ ____ ____ ____ ____ ____ ____ ____ ____
| |\ | |___ |  | [__  |___ |    |___ |  | |__/
| | \| |    |__| ___] |___ |___ |    |__| |  \
'''

def write_output(lines, output_file):
    if output_file:
        with open(output_file, "w", encoding="utf-8") as out:
            for line in lines:
                out.write(line + "\n")
    else:
        for line in lines:
            print(line)

def merge_files(files, unique_only, output_file):
    seen = set()
    result = []
    for fname in files:
        with open(fname, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.rstrip("\n")
                if not unique_only or line not in seen:
                    result.append(line)
                    seen.add(line)
    write_output(result, output_file)

def delete_entries(from_file, delete_file, output_file):
    delete_set = set()
    result = []
    with open(delete_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            delete_set.add(line.rstrip("\n"))
    with open(from_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.rstrip("\n")
            if line not in delete_set:
                result.append(line)
    write_output(result, output_file)

def filter_length(file, min_len, max_len, output_file):
    result = []
    with open(file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.rstrip("\n")
            if min_len <= len(line) <= max_len:
                result.append(line)
    write_output(result, output_file)

def filter_contains(file, substring, output_file):
    result = []
    with open(file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.rstrip("\n")
            if substring in line:
                result.append(line)
    write_output(result, output_file)

def filter_regex(file, pattern, output_file):
    regex = re.compile(pattern)
    result = []
    with open(file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.rstrip("\n")
            if regex.search(line):
                result.append(line)
    write_output(result, output_file)

def main():
    print(ASCII_ART)
    parser = argparse.ArgumentParser(description="Wordlist Swiss Army Knife")
    subparsers = parser.add_subparsers(dest="command")                                     

    merge_parser = subparsers.add_parser("merge", help="Merge multiple wordlists")
    merge_parser.add_argument("files", nargs="+")
    merge_parser.add_argument("--unique", action="store_true", help="Remove duplicates")
    merge_parser.add_argument("--output", help="Output file (default: stdout)")

    delete_parser = subparsers.add_parser("delete", help="Remove entries from one list based on another")
    delete_parser.add_argument("from_file")
    delete_parser.add_argument("delete_file")
    delete_parser.add_argument("--output", help="Output file (default: stdout)")

    filter_len_parser = subparsers.add_parser("filter-length", help="Filter by word length")
    filter_len_parser.add_argument("file")
    filter_len_parser.add_argument("min_len", type=int)
    filter_len_parser.add_argument("max_len", type=int)
    filter_len_parser.add_argument("--output", help="Output file (default: stdout)")

    contains_parser = subparsers.add_parser("contains", help="Filter by substring")
    contains_parser.add_argument("file")
    contains_parser.add_argument("substring")
    contains_parser.add_argument("--output", help="Output file (default: stdout)")

    regex_parser = subparsers.add_parser("regex", help="Filter by regex pattern")
    regex_parser.add_argument("file")
    regex_parser.add_argument("pattern")
    regex_parser.add_argument("--output", help="Output file (default: stdout)")

    args = parser.parse_args()

    if args.command == "merge":
        merge_files(args.files, args.unique, args.output)
    elif args.command == "delete":
        delete_entries(args.from_file, args.delete_file, args.output)
    elif args.command == "filter-length":
        filter_length(args.file, args.min_len, args.max_len, args.output)
    elif args.command == "contains":
        filter_contains(args.file, args.substring, args.output)
    elif args.command == "regex":
        filter_regex(args.file, args.pattern, args.output)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
