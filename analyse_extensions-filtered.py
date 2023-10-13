import csv
import os
import json


def run_snyk_test(csv_file, start_index=11, end_index=100):
    print("Running Snyk test and updating CSV...")
    error_count = 0  # Counter for "Failed to get vulns" errors

    # Existing results
    existing_results = {}
    for filename in os.listdir('snyk_test_results'):
        if filename.endswith('.json'):
            extension_id = os.path.splitext(filename)[0]
            with open(f'snyk_test_results/{filename}') as result_file:
                snyk_test_result = json.load(result_file)
                existing_results[extension_id] = snyk_test_result

    with open(csv_file, mode='r') as file:
        csv_reader = csv.DictReader(file)
        fieldnames = csv_reader.fieldnames + ['Snyk Test Result']

        with open('extensions-filtered-updated.csv', mode='a', newline='') as updated_file:
            writer = csv.DictWriter(updated_file, fieldnames=fieldnames)

            rows = list(csv_reader)
            num_entries = len(rows)
            if num_entries < end_index:
                end_index = num_entries

            print(f"Processing entries from {start_index} to {end_index}")

            for i in range(start_index - 1, end_index):
                row = rows[i]
                print(f"Processing entry {
                      i+1} for extension ID {row['Extension ID']}")

                extension_id = row['Extension ID']

                if extension_id in existing_results:
                    snyk_test_result = existing_results[extension_id]
                    print(f"Using existing Snyk test result for extension {
                          extension_id}")
                else:
                    print(f"No existing Snyk test result found for extension {
                          extension_id}")
                    continue

                if snyk_test_result.get('ok', True) is False and snyk_test_result.get('error', '') == "Failed to get vulns":
                    print(f"Retesting repository for extension {
                          extension_id} due to 'Failed to get vulns'")
                    source_code = row['Source Code']
                    os.system(
                        f'snyk test {source_code} --json > snyk_test_results/{extension_id}.json')

                    with open(f'snyk_test_results/{extension_id}.json') as result_file:
                        snyk_test_result = json.load(result_file)

                    error_count += 1  # Increment the error count

                row['Snyk Test Result'] = json.dumps(snyk_test_result)
                writer.writerow(row)
                print(f"Updated Snyk test result for extension {extension_id}")

    print(f"Snyk test and CSV update completed. Encountered {
          error_count} 'Failed to get vulns' errors.")


run_snyk_test('extensions-filtered.csv', start_index=11, end_index=100)
