import os
import pathlib
import subprocess
from pathlib import Path
import yaml

import matplotlib.pyplot as plt
import pandas as pd

def main():
    blog_path = Path('../blog/')
    script_path = Path(os.path.dirname(os.path.realpath(__file__)))
    stats_cache_path = script_path / 'stats-cache.yaml'
    google_analytics_path = script_path / 'google-analytics-data.yaml'

    if stats_cache_path.exists():
        # Read in existing stats
        print('Reading in existing stats...')
        with stats_cache_path.open('r') as file:
            stats_for_all_years = yaml.load(file, yaml.SafeLoader)
    else:
        stats_for_all_years = {}

    # Comment-out/add years here as applicable
    years = [
        # 2018, # 2018 is the earliest complete year we can gather stats for
        # 2019,
        # 2020,
        # 2021,
        # 2022,
    ]

    print(f'Updating stats for the following years: {years}')

    # cd to blog dir so git commands work
    os.chdir(blog_path)

    # Update stats for years listed above
    for year in years:
        stats = gather_stats(blog_path, year)
        stats_for_all_years[year] = stats
    print(stats_for_all_years)

    # Save stats back to file
    with stats_cache_path.open('w') as file:
        yaml.dump(stats_for_all_years, file)

    with stats_cache_path.open() as file:
        stats_for_all_years = yaml.load(file, yaml.SafeLoader)

    # Load Google analytics data
    with google_analytics_path.open() as file:
        google_analytics_data = yaml.load(file, yaml.SafeLoader)

    # Create graphs
    create_graphs(stats_for_all_years, google_analytics_data)

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

    # List of root paths that we will recursively scan to build up stats.
    # Make sure page content is included in these
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
                elif filename.endswith('.odg') or filename.endswith('.afdesign'):
                    stats['num_diagrams'] += 1
                else:
                    # stats['other_files'].append(filename)
                    pass
    
    return stats

def get_file_stats(file_path):
    """
    Run this on .md and .adoc files.
    """
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

def create_graphs(stats_for_all_years, google_analytics_data):
    fig, ax = plt.subplots()

    df_data = {}
    column_names = []
    for year in stats_for_all_years:
        values = []
        for (stat, value) in stats_for_all_years[year].items():
            values.append(value)
        df_data[year] = values
        # Re-assigns multiple times but this ok, we also assume the column names
        # are the same for every year
        column_names = list(stats_for_all_years[year].keys())

    df = pd.DataFrame.from_dict(df_data, orient='index', columns=column_names)
    # df = df.append(google_analytics_data, ignore_index=True)
    # df = df.transpose()
    print(df)

if __name__ == '__main__':
    main()
