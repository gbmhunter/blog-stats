import os
import pathlib
import subprocess
from pathlib import Path
import yaml

def main():
    blog_path = Path('../blog/')
    script_path = Path(os.path.dirname(os.path.realpath(__file__)))
    stats_cache_path = script_path / 'stats-cache.yaml'

    if not stats_cache_path.exists():
        years = [            
            2018, # 2018 is the earliest complete year we can gather stats for
            2019,
            2020,
            2021,
        ]

        # cd to blog dir so git commands work
        os.chdir(blog_path)

        stats_for_all_years = []
        for year in years:
            stats = gather_stats(blog_path, year)
            stats_for_all_years.append(stats)
        print(stats_for_all_years)

        # Save stats

        with stats_cache_path.open('w') as file:
            yaml.dump(stats_for_all_years, file)
    else:
        print('stats-cache.yaml exists, not re-calculating stats.')

    with stats_cache_path.open() as file:
        stats_for_all_years = yaml.load(file, yaml.SafeLoader)

    print(stats_for_all_years)

def gather_stats(blog_path: str, year: int):
    """
    Calculates stats about the blog at the last commit for that year.
    """
    next_year_as_str = str(year + 1)
    cmd = f'git rev-list -1 --before="{next_year_as_str}-01-01" master'
    completed_proc = subprocess.run(cmd, capture_output=True)    
    last_commit_of_year = completed_proc.stdout.decode().strip('\n')
    if last_commit_of_year == '':
        raise RuntimeError(f'No commit exists before the start of {year}.')

    print(f'Checking out commit {last_commit_of_year} (last commit of year {year})')

    cmd = f'git checkout {last_commit_of_year}'
    completed_proc = subprocess.run(cmd, capture_output=True)


    # Now files are in state they were at year end
    stats = {}
    stats['year'] = year

    # Get number of commits in that year
    cmd = f'git log --oneline'
    completed_proc = subprocess.run(cmd, capture_output=True)    
    commits_one_per_line = completed_proc.stdout.decode()
    num_commits = commits_one_per_line.count('\n')
    stats['num_commits'] = num_commits

    root_paths_to_walk = [
        blog_path / 'content',
        blog_path / 'static' / 'images',
    ]

    stats['num_markdown_files'] = 0
    stats['num_asciidoc_files'] = 0
    stats['num_content_files'] = 0
    stats['num_images'] = 0
    stats['num_diagrams'] = 0
    stats['other_files'] = []
    stats['num_chars'] = 0
    stats['num_words'] = 0
    stats['num_lines'] = 0
    for root_path_to_walk in root_paths_to_walk:
        for root, dirs, files in os.walk(root_path_to_walk):
            # print(dirs)
            for filename in files:
                if filename.endswith('.md'):
                    stats['num_markdown_files'] += 1
                    stats['num_content_files'] += 1
                    num_chars, num_words, num_lines = get_file_stats(Path(root) / filename)
                    stats['num_chars'] += num_chars
                    stats['num_words'] += num_words
                    stats['num_lines'] += num_lines
                elif filename.endswith('.adoc'):
                    stats['num_asciidoc_files'] += 1
                    stats['num_content_files'] += 1
                    num_chars, num_words, num_lines = get_file_stats(Path(root) / filename)
                    stats['num_chars'] += num_chars
                    stats['num_words'] += num_words
                    stats['num_lines'] += num_lines
                elif filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', '.svg')):
                    stats['num_images'] += 1
                elif filename.endswith('.odg'):
                    stats['num_diagrams'] += 1
                else:
                    # stats['other_files'].append(filename)
                    pass
    
    return stats

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
