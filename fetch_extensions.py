import requests
import csv


def request_pages(page_num, page_size=300):
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


def fetch_all_extensions():
    page_num = 1
    extensions_data = []

    while True:
        response = request_pages(page_num)
        page_extensions = response["results"][0]["extensions"]

        if not page_extensions:
            break

        extensions_data.extend(page_extensions)
        page_num += 1

    return extensions_data


csv_file_path = "extensions.csv"

extensions_data = fetch_all_extensions()

with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Extension Number", "Name", "Publisher", "Extension ID"])

    for i, extension in enumerate(extensions_data, start=1):
        writer.writerow([
            i,
            extension.get("displayName"),
            extension.get("publisher").get("displayName"),
            extension.get("extensionId"),
        ])

print(f"Total {len(extensions_data)
               } extension details written to {csv_file_path}")
