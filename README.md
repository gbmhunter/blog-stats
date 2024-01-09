## Running

Update the `years` List in `main.py` with the years you want to grab fresh data for. You don't have to do this if the data is already in `stats-cache.yaml`.

Make sure to add the Google analytics data for all years you want graphed, if it is missing those years will also be missing from all graphs.

## Stats Explanation

All stats are cumulative, i.e. cumulative total number at the end of year, including all years prior. Take differences between years to work out how many per year.

```yaml
- num_asciidoc_files: 0
  num_chars: 2713807 # 
  num_commits: 141 # Total number of commits at end of year (cumulative, not just for this year)
  num_content_files: 925
  num_diagrams: 0 # This is a subset of the num. of images
  num_images: 10862
  num_lines: 71251
  num_markdown_files: 925
  num_words: 379641
  other_files: []
  year: 2018
  ```