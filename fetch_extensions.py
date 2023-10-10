import requests
import csv
import json
import time

# Function to extract GitHub and GitLab repository URLs ending with ".git"


def extract_repository(json_data):
    repositories = []
    data_dict = json.loads(json_data)
    versions = data_dict.get("versions", [])

    for version in versions:
        properties = version.get("properties", [])
        for prop in properties:
            if prop.get("key") == "Microsoft.VisualStudio.Services.Links.Getstarted":
                source = prop.get("value", "")
                if source.endswith(".git"):
                    repositories.append({"Repository": source})

    return repositories

# Function to request extension pages with retries


def request_pages(page_num, page_size=20, max_retries=3, retry_delay=5):
    retries = 0
    while retries < max_retries:
        json_data = {
            "filters": [
                {
                    "criteria": [
                        {
                            "filterType": 8,
                            "value": "Microsoft.VisualStudio.Code"
                        },
                        {
                            "filterType": 10,
                            "value": "target:\"Microsoft.VisualStudio.Code\""
                        },
                        {
                            "filterType": 12,
                            "value": "37888"
                        }
                    ],
                    "direction": 2,
                    "pageSize": page_size,
                    "pageNumber": page_num,
                    "sortBy": 4,
                    "sortOrder": 0,
                    "pagingToken": None
                }
            ],
            "flags": 870,
        }

        try:
            response = requests.post(
                "https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery",
                json=json_data,
            )

            response.raise_for_status()  # Raise an exception for bad requests
            return response.json()
        except requests.exceptions.HTTPError as errh:
            print("HTTP Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print("Something went wrong:", err)

        retries += 1
        if retries < max_retries:
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        else:
            print(f"Max retries ({max_retries}) reached. Cannot continue.")
            return None

# Function to fetch extensions from GitHub or GitLab


def fetch_extensions():
    extensions_data = []
    total_extensions = 0
    page_num = 1

    while True:
        response = request_pages(page_num)

        if response is None:
            break

        page_extensions = response.get("results", [])[0].get("extensions", [])

        if not page_extensions:
            break

        for extension in page_extensions:
            publisher = extension.get(
                "publisher", {}).get("displayName", "N/A")
            display_name = extension.get("displayName", "N/A")
            repository_data = extract_repository(json.dumps(extension))

            if repository_data:
                repository = repository_data[0]["Repository"]
                statistics = extension.get("statistics", [])
                downloads = statistics[0]["value"] if statistics and statistics[0] else 0

                if (repository.endswith(".git") and "github" in repository) or (repository.endswith(".git") and "gitlab" in repository):
                    if downloads >= 50:
                        extensions_data.append({
                            "Extension Number": total_extensions + 1,
                            "Name": display_name,
                            "Publisher": publisher,
                            "Extension ID": extension.get("extensionId", "N/A"),
                            "Source Code": repository,
                            "Downloads": downloads
                        })
                        total_extensions += 1

        page_num += 1

    return extensions_data


# Specify the CSV file path
csv_file_path = 'extensions-filtered.csv'

# Fetch extensions from GitHub or GitLab with over 50 downloads
extensions_data = fetch_extensions()

# Write the data to CSV
with open(csv_file_path, mode='w', newline='') as file:
    fieldnames = ["Extension Number", "Name", "Publisher",
                  "Extension ID", "Source Code", "Downloads"]
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    for extension in extensions_data:
        writer.writerow(extension)

print(f'Total {len(extensions_data)
               } extension details written to {csv_file_path}')
