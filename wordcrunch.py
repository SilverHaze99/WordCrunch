#!/usr/bin/env python3

import argparse
import re
import gzip
import zipfile
import statistics
import sys
from pathlib import Path
from collections import Counter

# Beautiful ASCII Art for WordCrunch
def print_banner():
    """Print cool ASCII banner."""
    banner = """
╔═════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                         ║
║  ██╗    ██╗ ██████╗ ██████╗ ██████╗  ██████╗██████╗ ██╗   ██╗███╗   ██╗ ██████╗██╗  ██╗ ║
║  ██║    ██║██╔═══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗██║   ██║████╗  ██║██╔════╝██║  ██║ ║
║  ██║ █╗ ██║██║   ██║██████╔╝██║  ██║██║     ██████╔╝██║   ██║██╔██╗ ██║██║     ███████║ ║
║  ██║███╗██║██║   ██║██╔══██╗██║  ██║██║     ██╔══██╗██║   ██║██║╚██╗██║██║     ██╔══██║ ║
║  ╚███╔███╔╝╚██████╔╝██║  ██║██████╔╝╚██████╗██║  ██║╚██████╔╝██║ ╚████║╚██████╗██║  ██║ ║
║   ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═════╝  ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝╚═╝  ╚═╝ ║
║                                                                                         ║
║     Enhanced Wordlist Manipulation Tool v3.0                                            ║
║     Forensic Analysis • Data Processing • Advanced Filtering                            ║
║                                                                                         ║
╚═════════════════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)

def progress_bar(current, total, width=50):
    """Simple progress bar for large operations"""
    if total == 0:
        return ""
    percent = (current / total) * 100
    filled = int(width * current // total)
    bar = '█' * filled + '-' * (width - filled)
    return f'\r|{bar}| {percent:.1f}% ({current}/{total})'

def read_file_lines(filename, show_progress=False):
    """Read lines from various file formats with optional progress"""
    lines = []
    path = Path(filename)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filename}")
    
    # Determine file type and read accordingly
    if filename.endswith('.gz'):
        with gzip.open(filename, 'rt', encoding='utf-8', errors='ignore') as f:
            if show_progress:
                # For compressed files, we can't easily show progress
                print(f"Reading compressed file: {filename}")
            lines = [line.rstrip('\n\r') for line in f]
    elif filename.endswith('.zip'):
        with zipfile.ZipFile(filename, 'r') as zf:
            for file_info in zf.filelist:
                if file_info.filename.endswith('.txt'):
                    with zf.open(file_info) as f:
                        content = f.read().decode('utf-8', errors='ignore')
                        lines.extend([line.rstrip('\n\r') for line in content.splitlines()])
                    break
    else:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            if show_progress:
                # Get file size for progress
                f.seek(0, 2)
                file_size = f.tell()
                f.seek(0)
                
                for i, line in enumerate(f):
                    lines.append(line.rstrip('\n\r'))
                    if i % 10000 == 0:
                        pos = f.tell()
                        print(progress_bar(pos, file_size), end='', flush=True)
                print()  # New line after progress
            else:
                lines = [line.rstrip('\n\r') for line in f]
    
    return lines

def clean_lines(lines, strip_whitespace=False, remove_empty=False):
    """Clean lines by removing whitespace and empty entries"""
    if strip_whitespace:
        lines = [line.strip() for line in lines]
    
    if remove_empty:
        lines = [line for line in lines if line]
    
    return lines

def sort_lines(lines, sort_type="alpha", reverse=False):
    """Sort lines by various criteria"""
    if sort_type == "alpha":
        return sorted(lines, reverse=reverse)
    elif sort_type == "length":
        return sorted(lines, key=len, reverse=reverse)
    elif sort_type == "numeric":
        try:
            return sorted(lines, key=lambda x: float(x) if x.replace('.', '').replace('-', '').isdigit() else float('inf'), reverse=reverse)
        except:
            return sorted(lines, reverse=reverse)
    return lines

def transform_lines(lines, transform_type):
    """Transform lines according to specified type"""
    if transform_type == "lower":
        return [line.lower() for line in lines]
    elif transform_type == "upper":
        return [line.upper() for line in lines]
    elif transform_type == "capitalize":
        return [line.capitalize() for line in lines]
    elif transform_type == "reverse":
        return [line[::-1] for line in lines]
    return lines

def filter_by_content(lines, filter_type):
    """Filter lines by content type"""
    result = []
    for line in lines:
        if filter_type == "digits":
            if line.isdigit():
                result.append(line)
        elif filter_type == "alpha":
            if line.isalpha():
                result.append(line)
        elif filter_type == "has_special":
            if not line.isalnum():
                result.append(line)
        elif filter_type == "has_upper":
            if any(c.isupper() for c in line):
                result.append(line)
        elif filter_type == "has_number":
            if any(c.isdigit() for c in line):
                result.append(line)
    return result

def get_statistics(lines):
    """Get detailed statistics about the wordlist"""
    if not lines:
        return "No data to analyze."
    
    lengths = [len(line) for line in lines]
    unique_lines = set(lines)
    
    stats = f"""
📊 Wordlist Statistics:
═══════════════════════
Total lines: {len(lines):,}
Unique entries: {len(unique_lines):,}
Duplicates: {len(lines) - len(unique_lines):,}

📏 Length Analysis:
Shortest word: {min(lengths)} chars ("{min(lines, key=len)}")
Longest word: {max(lengths)} chars ("{max(lines, key=len)}")
Average length: {statistics.mean(lengths):.2f} chars
Median length: {statistics.median(lengths):.2f} chars

🔤 Character Analysis:
Lines with numbers: {len([l for l in lines if any(c.isdigit() for c in l)]):,}
Lines with uppercase: {len([l for l in lines if any(c.isupper() for c in l)]):,}
Lines with special chars: {len([l for l in lines if not l.isalnum()]):,}
"""
    return stats

def write_output(lines, output_file, preview=False, dry_run=False):
    """Write output with various options"""
    if dry_run:
        print(f"🔍 DRY RUN: Would write {len(lines):,} lines to {'stdout' if not output_file else output_file}")
        return
    
    if preview:
        print(f"📋 Preview (first 10 lines of {len(lines):,} total):")
        print("-" * 50)
        for i, line in enumerate(lines[:10]):
            print(f"{i+1:2d}: {line}")
        if len(lines) > 10:
            print(f"... and {len(lines) - 10:,} more lines")
        return
    
    if output_file:
        with open(output_file, "w", encoding="utf-8") as out:
            for line in lines:
                out.write(line + "\n")
        print(f"✅ Written {len(lines):,} lines to {output_file}")
    else:
        for line in lines:
            print(line)

def merge_files(files, unique_only, case_insensitive, output_file, **kwargs):
    seen = set()
    result = []
    
    for fname in files:
        print(f"📁 Processing: {fname}")
        lines = read_file_lines(fname, kwargs.get('progress', False))
        
        for line in lines:
            compare_line = line.lower() if case_insensitive else line
            
            if not unique_only or compare_line not in seen:
                result.append(line)
                seen.add(compare_line)
    
    result = apply_common_operations(result, **kwargs)
    write_output(result, output_file, kwargs.get('preview'), kwargs.get('dry_run'))

def delete_entries(from_file, delete_file, case_insensitive, output_file, **kwargs):
    delete_set = set()
    
    # Load deletion list
    delete_lines = read_file_lines(delete_file)
    for line in delete_lines:
        compare_line = line.lower() if case_insensitive else line
        delete_set.add(compare_line)
    
    # Process main file
    main_lines = read_file_lines(from_file, kwargs.get('progress', False))
    result = []
    
    for line in main_lines:
        compare_line = line.lower() if case_insensitive else line
        if compare_line not in delete_set:
            result.append(line)
    
    result = apply_common_operations(result, **kwargs)
    write_output(result, output_file, kwargs.get('preview'), kwargs.get('dry_run'))

def filter_length(file, min_len, max_len, output_file, **kwargs):
    lines = read_file_lines(file, kwargs.get('progress', False))
    result = [line for line in lines if min_len <= len(line) <= max_len]
    
    result = apply_common_operations(result, **kwargs)
    write_output(result, output_file, kwargs.get('preview'), kwargs.get('dry_run'))

def filter_contains(file, substring, case_insensitive, output_file, **kwargs):
    lines = read_file_lines(file, kwargs.get('progress', False))
    
    if case_insensitive:
        substring = substring.lower()
        result = [line for line in lines if substring in line.lower()]
    else:
        result = [line for line in lines if substring in line]
    
    result = apply_common_operations(result, **kwargs)
    write_output(result, output_file, kwargs.get('preview'), kwargs.get('dry_run'))

def filter_regex(file, pattern, case_insensitive, output_file, **kwargs):
    flags = re.IGNORECASE if case_insensitive else 0
    regex = re.compile(pattern, flags)
    
    lines = read_file_lines(file, kwargs.get('progress', False))
    result = [line for line in lines if regex.search(line)]
    
    result = apply_common_operations(result, **kwargs)
    write_output(result, output_file, kwargs.get('preview'), kwargs.get('dry_run'))

def filter_starts_ends(file, starts_with, ends_with, case_insensitive, output_file, **kwargs):
    lines = read_file_lines(file, kwargs.get('progress', False))
    result = []
    
    for line in lines:
        check_line = line.lower() if case_insensitive else line
        check_starts = starts_with.lower() if case_insensitive and starts_with else starts_with
        check_ends = ends_with.lower() if case_insensitive and ends_with else ends_with
        
        if starts_with and not check_line.startswith(check_starts):
            continue
        if ends_with and not check_line.endswith(check_ends):
            continue
        result.append(line)
    
    result = apply_common_operations(result, **kwargs)
    write_output(result, output_file, kwargs.get('preview'), kwargs.get('dry_run'))

def filter_unique_chars(file, min_unique, output_file, **kwargs):
    lines = read_file_lines(file, kwargs.get('progress', False))
    result = [line for line in lines if len(set(line.lower())) >= min_unique]
    
    result = apply_common_operations(result, **kwargs)
    write_output(result, output_file, kwargs.get('preview'), kwargs.get('dry_run'))

def apply_common_operations(lines, **kwargs):
    """Apply common operations like cleaning, sorting, transforming"""
    # Clean
    if kwargs.get('strip') or kwargs.get('remove_empty'):
        lines = clean_lines(lines, kwargs.get('strip'), kwargs.get('remove_empty'))
    
    # Transform
    if kwargs.get('transform'):
        lines = transform_lines(lines, kwargs['transform'])
    
    # Filter by content type
    if kwargs.get('content_filter'):
        lines = filter_by_content(lines, kwargs['content_filter'])
    
    # Sort
    if kwargs.get('sort'):
        lines = sort_lines(lines, kwargs['sort'], kwargs.get('reverse_sort', False))
    
    return lines

def show_statistics(file, **kwargs):
    lines = read_file_lines(file, kwargs.get('progress', False))
    print(get_statistics(lines))

def main():
    print_banner()
    
    parser = argparse.ArgumentParser(
        description="WordCrunch - The Ultimate Wordlist Swiss Army Knife",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Global options
    parser.add_argument('--case-insensitive', '-i', action='store_true', help='Ignore case differences')
    parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    parser.add_argument('--sort', choices=['alpha', 'length', 'numeric'], help='Sort output')
    parser.add_argument('--reverse-sort', action='store_true', help='Reverse sort order')
    parser.add_argument('--strip', action='store_true', help='Strip whitespace from lines')
    parser.add_argument('--remove-empty', action='store_true', help='Remove empty lines')
    parser.add_argument('--transform', choices=['lower', 'upper', 'capitalize', 'reverse'], help='Transform text')
    parser.add_argument('--content-filter', choices=['digits', 'alpha', 'has_special', 'has_upper', 'has_number'], help='Filter by content type')
    parser.add_argument('--preview', action='store_true', help='Show first 10 lines only')
    parser.add_argument('--dry-run', action='store_true', help='Show what would happen without doing it')
    parser.add_argument('--progress', action='store_true', help='Show progress bar for large files')
    
    subparsers = parser.add_subparsers(dest="command", help='Available commands')
    
    # Merge command
    merge_parser = subparsers.add_parser("merge", help="Merge multiple wordlists")
    merge_parser.add_argument("files", nargs="+", help="Files to merge")
    merge_parser.add_argument("--unique", action="store_true", help="Remove duplicates")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Remove entries from one list based on another")
    delete_parser.add_argument("from_file", help="Main file")
    delete_parser.add_argument("delete_file", help="File with entries to delete")
    
    # Filter length command
    filter_len_parser = subparsers.add_parser("filter-length", help="Filter by word length")
    filter_len_parser.add_argument("file", help="Input file")
    filter_len_parser.add_argument("min_len", type=int, help="Minimum length")
    filter_len_parser.add_argument("max_len", type=int, help="Maximum length")
    
    # Contains command
    contains_parser = subparsers.add_parser("contains", help="Filter by substring")
    contains_parser.add_argument("file", help="Input file")
    contains_parser.add_argument("substring", help="Substring to find")
    
    # Regex command
    regex_parser = subparsers.add_parser("regex", help="Filter by regex pattern")
    regex_parser.add_argument("file", help="Input file")
    regex_parser.add_argument("pattern", help="Regex pattern")
    
    # Starts/Ends command
    starts_ends_parser = subparsers.add_parser("starts-ends", help="Filter by prefix/suffix")
    starts_ends_parser.add_argument("file", help="Input file")
    starts_ends_parser.add_argument("--starts-with", help="Must start with this string")
    starts_ends_parser.add_argument("--ends-with", help="Must end with this string")
    
    # Unique chars command
    unique_chars_parser = subparsers.add_parser("unique-chars", help="Filter by minimum unique characters")
    unique_chars_parser.add_argument("file", help="Input file")
    unique_chars_parser.add_argument("min_unique", type=int, help="Minimum unique characters")
    
    # Statistics command
    stats_parser = subparsers.add_parser("stats", help="Show wordlist statistics")
    stats_parser.add_argument("file", help="Input file to analyze")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Convert args to kwargs
    kwargs = vars(args)
    
    try:
        if args.command == "merge":
            merge_files(args.files, args.unique, args.case_insensitive, args.output, **kwargs)
        elif args.command == "delete":
            delete_entries(args.from_file, args.delete_file, args.case_insensitive, args.output, **kwargs)
        elif args.command == "filter-length":
            filter_length(args.file, args.min_len, args.max_len, args.output, **kwargs)
        elif args.command == "contains":
            filter_contains(args.file, args.substring, args.case_insensitive, args.output, **kwargs)
        elif args.command == "regex":
            filter_regex(args.file, args.pattern, args.case_insensitive, args.output, **kwargs)
        elif args.command == "starts-ends":
            filter_starts_ends(args.file, args.starts_with, args.ends_with, args.case_insensitive, args.output, **kwargs)
        elif args.command == "unique-chars":
            filter_unique_chars(args.file, args.min_unique, args.output, **kwargs)
        elif args.command == "stats":
            show_statistics(args.file, **kwargs)
            
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
