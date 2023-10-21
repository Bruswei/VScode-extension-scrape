import csv
import os
import json


def load_existing_results():
    existing_results = {}
    for filename in os.listdir('snyk_test_results'):
        if filename.endswith('.json'):
            extension_id = os.path.splitext(filename)[0]
            with open(f'snyk_test_results/{filename}') as result_file:
                try:
                    snyk_test_result = json.load(result_file)
                    existing_results[extension_id] = snyk_test_result
                except json.JSONDecodeError:
                    print(f"Failed to decode JSON for {
                          extension_id}. Skipping.")
    return existing_results


def run_snyk_test_for_repository(source_code, extension_id):
    os.system(
        f'snyk test {source_code} --json > snyk_test_results/{extension_id}.json')


def update_csv_with_test_result(row, snyk_test_result):
    row['Snyk Test Result'] = json.dumps(snyk_test_result)


def run_snyk_test(csv_file, start_index, end_index):
    while True:
        print("Running Snyk test and updating CSV...")
        error_count = 0  # Counter for "Failed to get vulns" errors

        existing_results = load_existing_results()

        with open(csv_file, mode='r') as file:
            csv_reader = csv.DictReader(file)
            fieldnames = csv_reader.fieldnames + ['Snyk Test Result']

            rows = list(csv_reader)
            num_entries = len(rows)
            if num_entries < end_index:
                end_index = num_entries

            print(f"Processing entries from {start_index} to {end_index}")

            updated_rows = []  # Store updated rows with test results

            for i in range(start_index - 1, end_index):
                row = rows[i]
                print(f"Processing entry {
                      i+1} for extension ID {row['Extension ID']}")

                extension_id = row['Extension ID']

                if extension_id in existing_results:
                    snyk_test_result = existing_results[extension_id]
                    print(f"Using existing Snyk test result for extension {
                          extension_id}")
                    if snyk_test_result.get('ok', True) is False and snyk_test_result.get('error', '') == "Failed to get vulns":
                        print(f"Retesting repository for extension {
                              extension_id} due to 'Failed to get vulns'")
                        source_code = row['Source Code']
                        run_snyk_test_for_repository(source_code, extension_id)
                        with open(f'snyk_test_results/{extension_id}.json') as result_file:
                            snyk_test_result = json.load(result_file)
                        error_count += 1  # Increment the error count
                else:
                    print(f"No existing Snyk test result found for extension {
                          extension_id}")
                    source_code = row['Source Code']
                    run_snyk_test_for_repository(source_code, extension_id)
                    with open(f'snyk_test_results/{extension_id}.json') as result_file:
                        try:
                            snyk_test_result = json.load(result_file)
                            if snyk_test_result.get('ok', True) is False and snyk_test_result.get('error', '') == "Failed to get vulns":
                                print(f"Retesting repository for extension {
                                      extension_id} due to 'Failed to get vulns'")
                                source_code = row['Source Code']
                                run_snyk_test_for_repository(
                                    source_code, extension_id)
                                with open(f'snyk_test_results/{extension_id}.json') as result_file:
                                    snyk_test_result = json.load(result_file)
                                error_count += 1  # Increment the error count
                        except json.JSONDecodeError:
                            print(f"Failed to decode JSON for {
                                  extension_id}. Skipping.")

                update_csv_with_test_result(row, snyk_test_result)
                updated_rows.append(row)
                print(f"Updated Snyk test result for extension {extension_id}")

        # Update the results in extensions-filtered-updated.csv
        with open('extensions-filtered-updated.csv', mode='a', newline='') as updated_file:
            writer = csv.DictWriter(updated_file, fieldnames=fieldnames)
            for updated_row in updated_rows:
                writer.writerow(updated_row)

        print(f"Snyk test and CSV update completed. Encountered {
              error_count} 'Failed to get vulns' errors.")
        if error_count == 0:
            break


# run_snyk_test('extensions-filtered.csv', start_index=2501, end_index=3000)
run_snyk_test('extensions-filtered.csv', start_index=1568, end_index=1570)
