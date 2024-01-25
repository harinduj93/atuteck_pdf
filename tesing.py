import csv
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests
import os
from tqdm import tqdm

input_csv_filename = 'input.csv'
output_csv_filename = 'output.csv'
temp = 0

# Write to a csv
def write_csv(file_name, url):
    with open(file_name, 'a', newline='', encoding='utf-8') as csv_file_w:
        csv_writer = csv.writer(csv_file_w)
        csv_writer.writerow([url])

# Function to extract and print URLs from HTML content
def get_urls(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    # Find all 'a' tags (links)
    link_elements = soup.find_all('a')
    # Extract and write the URLs to the output CSV file
    for link in link_elements:
        url = link.get('href')
        if url:
            write_csv(output_csv_filename, url)

# Read HTML content from CSV file and call get_urls function
def make_url_list(inputfile):
    with open(inputfile, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            html_content = row[0]  # Assuming HTML content is in the first column (column index 0)
            get_urls(html_content)

def get_file_size(url, timeout=10):
    try:
        response = requests.head(url, timeout=timeout)
        response.raise_for_status()  # Raise HTTPError for bad responses
        # Extract Content-Length from the response headers
        size = int(response.headers.get('Content-Length', 0))
        print(f'Size of file: {size / (1024 * 1024):.2f} MB')
        return size
    except requests.exceptions.RequestException as e:
        print(f'Error getting size for {url}: {e}')
        return 0

def download_files(url):
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses

        # Extract filename from the URL
        filename = os.path.basename(urlparse(url).path)

        # Ensure the filename is not empty
        if not filename:
            raise ValueError("Empty filename")

        # Save the content to the file in the same location as the script with tqdm progress bar
        bar_format = "{desc}{percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}]"
        with tqdm.wrapattr(open(filename, 'wb'), "write", miniters=1, desc=filename, total=int(response.headers.get('content-length', 0)), unit='B', unit_scale=True, bar_format=bar_format, colour='green') as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)

        print(f'Downloaded: {filename}')
    except requests.exceptions.RequestException as e:
        print(f'Error downloading {url}: {e}')
    except ValueError as ve:
        print(f'Error extracting filename for {url}: {ve}')

# Generate output CSV file
make_url_list(input_csv_filename)

# Get the list of URLs from output CSV file
with open(output_csv_filename, 'r', encoding='utf-8') as csv_file:
    csv_reader = csv.reader(csv_file)
    urls = [row[0] for row in csv_reader]  # Assuming URLs are in the first column

# Download files sequentially (one after another)
for url in urls:
    download_files(url)
