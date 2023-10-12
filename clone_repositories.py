import csv
import os

# Function to git clone the repositories


def git_clone_repositories(csv_file):
    with open(csv_file, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            source_code = row.get('Source Code')

            # Clone only if source_code is valid
            if source_code:
                # Generate a folder name from the repository name
                folder_name = row.get('Name').replace(' ', '_')

                # Check if it's a GitHub repository
                if 'github.com' in source_code:
                    # Replace the first occurrence of '/' with ':'
                    ssh_source_code = source_code.replace(
                        'https://github.com/', 'git@github.com:', 1)
                # Check if it's a GitLab repository
                elif 'gitlab.com' in source_code:
                    # Replace the first occurrence of '/' with ':'
                    ssh_source_code = source_code.replace(
                        'https://gitlab.com/', 'git@gitlab.com:', 1)

                # Print the git clone command
                print(f'git clone {ssh_source_code} repository/{folder_name}')

                # Clone into the generated folder
                os.system(
                    f'git clone {ssh_source_code} repository/{folder_name}')


# Specify the CSV file path
csv_file_path = 'extensions-filtered.csv'  # Update with your CSV file path

# Git clone repositories from the CSV
git_clone_repositories(csv_file_path)
