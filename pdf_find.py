import csv
from urllib.parse import urlparse

from bs4 import BeautifulSoup
import requests
import os

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

def total_file_size(csv_input, timeout=10):
    total_size = 0
    with open(csv_input, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        urls = [row[0] for row in csv_reader]  # Assuming URLs are in the first column

    for url in urls:
        size = get_file_size(url, timeout=timeout)
        total_size += size
        print(f'Total size of all files: {total_size / (1024 * 1024):.2f} MB')

    return total_size


def download_files(csv_input):
    with open(csv_input, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        urls = [row[0] for row in csv_reader]  # Assuming URLs are in the first column

    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise HTTPError for bad responses

            # Extract filename from the URL
            filename = os.path.basename(urlparse(url).path)

            # Save the content to the file in the same location as the script
            with open(filename, 'wb') as file:
                file.write(response.content)

            print(f'Downloaded: {filename}')
        except requests.exceptions.RequestException as e:
            print(f'Error downloading {url}: {e}')


# Generate output CSV file
make_url_list(input_csv_filename)

# Calculate total file size sequentially
total_size = total_file_size(output_csv_filename, timeout=10)
print(f'Total size of all files: {total_size / (1024 * 1024):.2f} MB')
#download_files(output_csv_filename)  #test this last