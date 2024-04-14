import re
import os
import email
from collections import defaultdict
from email import policy
from email.parser import BytesFeedParser

def code_3(directory_path,filter_name,example_data):

    def create_custom_filter():

        # Function to determine the type and length of example data and search for similar data
        def custom_filter(text):
            data_type = None
            data_length = None

            # Determine the data type of the example data
            if example_data.isdigit():
                data_type = 'digits'
            elif example_data.isalpha():
                data_type = 'alphabetic'
            else:
                data_type = 'alphanumeric'

            # Determine the length of the example data
            data_length = len(example_data)

            # Search for data of similar type and length in the text
            pattern = r'\b\w{%d}\b' % data_length
            found_data = re.findall(pattern, text)

            filtered_data = [data for data in found_data if data.isdigit() == example_data.isdigit() and len(data) == data_length]

            return filtered_data

        return filter_name, custom_filter

    def analyze_email_file(file_path, selected_patterns, custom_filters):
        leaks = defaultdict(int)

        with open(file_path, 'r', encoding="utf-8") as file:
            msg = email.message_from_file(file)
            body = ''

            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain' or content_type == 'text/html':
                    body += part.get_payload(decode=True).decode()

            for pattern_name in selected_patterns:
                if pattern_name in custom_filters:
                    leaks[pattern_name] += len(custom_filters[pattern_name](body))

        return dict(leaks)


    custom_filters = {}
    total_leaks = defaultdict(int)
    files_with_leaks = 0
    total_files = 0
    files_with_selected_leaks = []

    filter_name, custom_filter = create_custom_filter()
    custom_filters[filter_name] = custom_filter
    results = defaultdict(list)
    all_patterns = list(custom_filters.keys())

    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)

        if os.path.isfile(file_path) and filename.endswith('.eml'):
            leaks = analyze_email_file(file_path, all_patterns, custom_filters)
            total_files += 1

            if any(leaks.values()):
                files_with_leaks += 1
                files_with_selected_leaks.append((filename, leaks))

            for pattern_name, count in leaks.items():
                total_leaks[pattern_name] += count

    print(f"Total files processed: {total_files}")
    print(f"Total files with leaks: {files_with_leaks}")
    for pattern_name, count in total_leaks.items():
        print(f"{pattern_name}: {count}")

    print("\nFiles with selected leaks:")
    for filename, leaks in files_with_selected_leaks:
        print(f"{filename}: {leaks}")
        results[filename] = leaks

    results["total_files"] = total_files
    results["total_leaks"] = dict(total_leaks)
    results["files_with_leaks"] = files_with_leaks
    results["files_with_selected_leaks"] = files_with_selected_leaks
    
    return results