# auction-tools

This is a tool for processing camellia auction data. 

The parse.py script is designed to take a list of Camellia variety names and perform a best effort lookup against the Atlantic Coast Camellia Societies spreadsheet to pull the corresponding varieties information and picture. This tool will attempt to account for minor differences in spelling and character usage.   

## Requirements
This project requires a copy of the Atlantic Coast Camellia Society Excel Spreadsheet. Reach out to the [ACCS](https://www.atlanticcoastcamelliasociety.org/ACCS%20Officers%20-%20State%20Directors.html) to request a copy of the spreadsheet

For this utility to work properly, save the Excel spreadsheet to the root of the repo directory as `./ACCS.xlsx`

## Installation

### Install uv
uv is a python project manager used for this repo. Follow their installation instructions here: https://docs.astral.sh/uv/getting-started/installation/

### Run the parser
`uv run parse.py List-Example.txt`

## Output
Parsed info is written to the `./auction.csv` file
Images are saved to the local repos `./image` directory. Images are named after the variety's id
Details on matches are saved to `./match_list.csv`. This provides the original search name, parsed search term, the matched name, and the match ratio score.

