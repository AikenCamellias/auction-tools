import argparse
import pandas as pd
import re
from rapidfuzz import process, fuzz
import urllib.request
import urllib.parse
import traceback

BASE_URL = 'https://www.atlanticcoastcamelliasociety.org/Camelliae%20Floris%20Bibliotheca/images/'
BACKUP_BASE_URL = 'https://www.socalcamelliasociety.org/Camelliae%20Floris%20Bibliotheca/images/'
FILE_PATH = 'images/'

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Parse auction input file and match against camellia database')
parser.add_argument('filename', help='Input file containing list of camellia names')
args = parser.parse_args()

# Read and clean the raw list
with open(args.filename, 'r') as inFile:
    raw_lines = [line.rstrip() for line in inFile if line.strip()]

def clean_name(name):
    """Strip numbering (e.g., '1. ') and annotations like '(grafted plant)'"""
    name = re.sub(r'^\d+\.\s*', '', name)
    name = re.sub(r'\s*\([^)]*\)\s*$', '', name)
    return name.strip()

search_names = [clean_name(line) for line in raw_lines]

# Load database
db = pd.read_excel('ACCS - 2026.xlsx')
db_names = db['name'].dropna().tolist()

# Fuzzy match each search name
THRESHOLD = 85 
results = []
not_found = []
missing_images = []
match_list = []  # original name -> matched name mapping

for i, search_name in enumerate(search_names):
    print(f"Processing {search_name}")
    original_name = raw_lines[i]
    match = process.extractOne(search_name, db_names, scorer=fuzz.ratio)
    if match and match[1] >= THRESHOLD:
        matched_name = match[0]
        row = db[db['name'] == matched_name].iloc[0].to_dict()
        row['search_term'] = search_name
        row['match_score'] = match[1]
        match_list.append({'original': original_name, 'cleaned': search_name, 
			'matched_name': matched_name, 'score': match[1]})
        results.append(row)
        try:
            # Use urlretrieve to download the URL content and save it to a local file
            url = BASE_URL + urllib.parse.quote(matched_name + '.jpg', safe='')
            urllib.request.urlretrieve(url, FILE_PATH+str(row['id'])+'.jpg')
            print(f"Image successfully downloaded and saved to {FILE_PATH+str(row['id'])+'.jpg'}")
        except Exception as e:
            print(f"Primary URL failed for {matched_name}, trying backup...")
            try:
                backup_url = BACKUP_BASE_URL + urllib.parse.quote(matched_name + '.jpg', safe='')
                urllib.request.urlretrieve(backup_url, FILE_PATH+str(row['id'])+'.jpg')
                print(f"Image successfully downloaded from backup to {FILE_PATH+str(row['id'])+'.jpg'}")
            except Exception as e2:
                print(f"An error occurred when downloading {matched_name}:\n{e2}") 
                print(f"URL: {url}")
                print(f"Backup URL: {backup_url}")
                missing_images.append((matched_name, url))
                #print(traceback.print_exc())
    else:
        not_found.append((search_name, match))
        best_guess = match[0] if match else ''
        best_score = match[1] if match else 0
        match_list.append({'original': original_name, 'cleaned': search_name, 
			'matched_name': best_guess, 'score': best_score})

# Output results
output_df = pd.DataFrame(results)
output_df.to_csv('auction.csv', index=False)

# Output match list (original -> matched name mapping)
match_df = pd.DataFrame(match_list)
match_df.to_csv('match_list.csv', index=False)

print(f"Found {len(results)} matches")

print(f"\nNot found ({len(not_found)}):")
for name, best_match in not_found:
    if best_match:
        print(f"  {name} -> best guess: {best_match[0]} (score: {best_match[1]})")

print(f"\nMissing images ({len(missing_images)}):")
for name, url in missing_images:
    print(f"  {name} -> {url}")