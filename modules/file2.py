import re
import os
import email
from collections import defaultdict
from email import policy
from email.parser import BytesFeedParser

def code_2(directory_path, selected_patterns_input):
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

    if selected_patterns_input == 'all':
        selected_patterns = ['passport', 'snils', 'phone', 'account', 'card']
    else:
        selected_patterns = selected_patterns_input
    
    total_leaks = defaultdict(int)
    files_with_leaks = 0
    total_files = 0
    files_with_selected_leaks = []

    results = defaultdict(list)  # Создаем пустой словарь для хранения результатов

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

            # Добавляем результаты для текущего файла в общий словарь результатов
            results[filename] = leaks

    results["total_files"] = total_files
    results["total_leaks"] = dict(total_leaks)
    results["files_with_leaks"] = files_with_leaks
    results["files_with_selected_leaks"] = files_with_selected_leaks
    print(results)
    return results
