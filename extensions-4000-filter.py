import csv
import json
import os

# Path to the folder where the JSON files are stored
json_folder_path = 'snyk_test_results'

try:
    # Open the source CSV file to read data
    with open('extensions-filtered.csv', mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        # Open the new CSV file to write data
        with open('updated-4000-csv-for-excel.csv', mode='w', newline='', encoding='utf-8') as new_csvfile:
            fieldnames = ['Extension Number', 'Name', 'Publisher', 'Extension ID', 'Source Code',
                          'Downloads', 'ok', 'critical', 'high', 'medium', 'low', 'total vul', 'vulnerabilities']
            writer = csv.DictWriter(new_csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                extension_number = int(row['Extension Number'])
                if 1 <= extension_number <= 4000:
                    print(f"Processing Extension Number: {extension_number}")

                    # Construct the JSON file path using the Extension ID
                    json_file_path = os.path.join(
                        json_folder_path, f"{row['Extension ID']}.json")

                    # Initialize the data to write to the CSV
                    csv_row_data = row.copy()
                    csv_row_data.update({'ok': '', 'critical': 0, 'high': 0,
                                         'medium': 0, 'low': 0, 'total vul': 0, 'vulnerabilities': ''})

                    # If the JSON file exists, process it
                    if os.path.exists(json_file_path):
                        with open(json_file_path, 'r', encoding='utf-8') as jsonfile:
                            try:
                                data = json.load(jsonfile)
                                ok = data.get('ok', False)
                                csv_row_data['ok'] = ok

                                if not ok:
                                    vulnerabilities = data.get(
                                        'vulnerabilities', [])
                                    vulnerability_titles = []

                                    for v in vulnerabilities:
                                        severity = v.get(
                                            'severity', '').capitalize()
                                        title = f"{severity}: {
                                            v.get('title', 'Unknown')}"
                                        vulnerability_titles.append(title)

                                    severity_map = data.get('severityMap', {})

                                    critical = severity_map.get('critical', 0)
                                    high = severity_map.get('high', 0)
                                    medium = severity_map.get('medium', 0)
                                    low = severity_map.get('low', 0)

                                    total_vul = sum(severity_map.values())

                                    csv_row_data.update({
                                        'critical': critical,
                                        'high': high,
                                        'medium': medium,
                                        'low': low,
                                        'total vul': total_vul,
                                        'vulnerabilities': "; ".join(vulnerability_titles)
                                    })
                            except json.JSONDecodeError as e:
                                print(f"Error decoding JSON for Extension ID {
                                      row['Extension ID']}: {e}")

                    # Write the processed data to the new CSV file
                    writer.writerow(csv_row_data)

    print("Finished processing all extensions.")
except Exception as e:
    print(f"An error occurred: {e}")
