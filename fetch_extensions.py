import requests
import csv
import json


def extract_github_repos(json_data):
    repositories = []
    data_dict = json.loads(json_data)
    versions = data_dict.get("versions", [])

    for version in versions:
        properties = version.get("properties", [])
        for prop in properties:
            if prop.get("key") == "Microsoft.VisualStudio.Services.Links.Getstarted":
                source = prop.get("value", "")
                if source.endswith(".git"):
                    repositories.append({"GitHub Repository": source})

    return repositories


def request_pages(page_num, page_size=20):
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

    response = requests.post(
        "https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery",
        json=json_data,
    )

    return response.json()


def fetch_first_100_extensions():
    extensions_data = []
    total_extensions = 0

    for page_num in range(1, 6):
        response = request_pages(page_num)
        page_extensions = response.get("results", [])[0].get("extensions", [])

        if not page_extensions:
            break

        for extension in page_extensions:
            publisher = extension.get(
                "publisher", {}).get("displayName", "N/A")
            display_name = extension.get("displayName", "N/A")
            repository = "N/A"
            stats = extension.get("statistics", [])[0].get("value", "N/A")

            repository_data = extract_github_repos(json.dumps(extension))
            if repository_data:
                repository = repository_data[0]["GitHub Repository"]

            extensions_data.append({
                "Extension Number": total_extensions + 1,
                "Name": display_name,
                "Publisher": publisher,
                "Extension ID": extension.get("extensionId", "N/A"),
                # "Downloads": stats,
                "Source Code": repository,
            })

            total_extensions += 1

            if total_extensions >= 100:
                break

    return extensions_data


csv_file_path = "extensions.csv"

extensions_data = fetch_first_100_extensions()

with open(csv_file_path, mode='w', newline='') as file:
    fieldnames = ["Extension Number", "Name",
                  "Publisher", "Extension ID", "Source Code"]
    writer = csv.DictWriter(file, fieldnames=fieldnames)

    writer.writeheader()
    for extension in extensions_data:
        writer.writerow(extension)

print(f"Total {len(extensions_data)
               } extension details written to {csv_file_path}")
