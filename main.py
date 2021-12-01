import os
import subprocess
from pathlib import Path

def main():
    blog_path = Path('../blog/')

    years = [
        2020,
    ]

    # cd to blog dir so git commands work
    os.chdir(blog_path)    
    for year in years:
        gather_stats(blog_path, year)
        

def gather_stats(blog_path: str, year: int):
    next_year_as_str = str(year + 1)
    cmd = f'git rev-list -1 --before="{next_year_as_str}-01-01" master'
    completed_proc = subprocess.run(cmd, capture_output=True)    
    last_commit_of_year = completed_proc.stdout.decode().strip('\n')
    print(f'Checking out commit {last_commit_of_year}')

    cmd = f'git checkout {last_commit_of_year}'
    completed_proc = subprocess.run(cmd, capture_output=True)

    # Now files are in state they were at year end
    stats = {}
    stats['num_markdown_files'] = 0
    stats['num_asciidoc_files'] = 0
    stats['num_images'] = 0
    stats['num_diagrams'] = 0
    stats['other_files'] = []
    stats['num_chars'] = 0
    stats['num_words'] = 0
    stats['num_lines'] = 0
    for root, dirs, files in os.walk(blog_path / 'content'):
        # print(dirs)
        for filename in files:
            if filename.endswith('.md'):
                stats['num_markdown_files'] += 1
                num_chars, num_words, num_lines = get_file_stats(Path(root) / filename)
                stats['num_chars'] += num_chars
                stats['num_words'] += num_words
                stats['num_lines'] += num_lines
            elif filename.endswith('.adoc'):
                stats['num_asciidoc_files'] += 1
                num_chars, num_words, num_lines = get_file_stats(Path(root) / filename)
                stats['num_chars'] += num_chars
                stats['num_words'] += num_words
                stats['num_lines'] += num_lines
            elif filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', '.svg')):
                stats['num_images'] += 1
            elif filename.endswith('.odg'):
                stats['num_diagrams'] += 1
            else:
                stats['other_files'].append(filename)


    print(stats)

def get_file_stats(file_path):
    num_words = 0
    num_chars = 0
    num_lines = 0

    with file_path.open(encoding='utf8') as file:
        for line in file:
            wordlist = line.split()
            num_lines += 1
            num_words += len(wordlist)
            num_chars += len(line)

    return num_chars, num_words, num_lines

if __name__ == '__main__':
    main()
