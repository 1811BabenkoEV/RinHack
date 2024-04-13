import re
import os
import email
from collections import defaultdict

from email import policy
from email.parser import BytesFeedParser


def extract_account_numbers(text):
    pattern = r'\b\d{20}\b'
    account_numbers = re.findall(pattern, text)
    return account_numbers


def extract_card_numbers(text):
    pattern = r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b(?:\s\d{2}/\d{2})?(?:\s\d{3})?\b'
    card_numbers = re.findall(pattern, text)
    return card_numbers


def extract_passport_data(text):
    pattern = r'\b\d{4}(?:[ -]?[N№]?[ -]?|\s?)\d{6}\b'
    passport_data = re.findall(pattern, text)
    return passport_data


def extract_phone_numbers(text):
    pattern = r'\+7\s?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}'
    phone_numbers = re.findall(pattern, text)
    return phone_numbers


def extract_snils_numbers(text):
    pattern = r'\b\d{3}-\d{3}-\d{3}\s\d{2}\b'
    snils_numbers = re.findall(pattern, text)
    return snils_numbers


def extract_email_addresses(text):
    pattern = r'\b[\w.-]+@[a-zA-Z\d.-]+\.[a-zA-Z]{2,}\b'
    email_addresses = re.findall(pattern, text)
    return email_addresses


def analyze_email_file(file_path, selected_patterns):
    leaks = defaultdict(int)

    with open(file_path, 'r', encoding="utf-8") as file:
        msg = email.message_from_file(file)
        body = ''

        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == 'text/plain' or content_type == 'text/html':
                body += part.get_payload(decode=True).decode()

        for pattern_name in selected_patterns:
            if pattern_name == 'passport':
                leaks['passport'] += len(extract_passport_data(body))
            elif pattern_name == 'snils':
                leaks['snils'] += len(extract_snils_numbers(body))
            elif pattern_name == 'phone':
                leaks['phone'] += len(extract_phone_numbers(body))
            elif pattern_name == 'account':
                leaks['account'] += len(extract_account_numbers(body))
            elif pattern_name == 'card':
                leaks['card'] += len(extract_card_numbers(body))

    return dict(leaks)


def main(directory_path, selected_patterns):
    total_leaks = defaultdict(int)
    files_with_leaks = 0
    total_files = 0
    files_with_selected_leaks = []

    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)

        if os.path.isfile(file_path) and filename.endswith('.eml'):
            leaks = analyze_email_file(file_path, selected_patterns)
            total_files += 1

            if any(leaks.values()):
                files_with_leaks += 1
                files_with_selected_leaks.append((filename, leaks))

            for pattern_name, count in leaks.items():
                total_leaks[pattern_name] += count

    print(f"Число обработанных файлов: {total_files}")
    print(f"Число файлов с утечками: {files_with_leaks}")
    for pattern_name, count in total_leaks.items():
        print(f"{pattern_name}: {count}")

    print("\nСписок файлов с утечка:")
    for filename, leaks in files_with_selected_leaks:
        print(f"{filename}: {leaks}")


if __name__ == "__main__":
    directory_path = 'C:/Users/user/Documents/ХАКАТОН/small'

    print("Select the types of data leaks you want to find (comma-separated or 'all' for all):")
    print("Options: passport, snils, phone, account, card")
    selected_patterns_input = input().strip().lower()

    if selected_patterns_input == 'all':
        selected_patterns = ['passport', 'snils', 'phone', 'account', 'card']
    else:
        selected_patterns = selected_patterns_input.split()

    main(directory_path, selected_patterns)