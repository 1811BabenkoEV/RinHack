import os
import re
import email
from collections import defaultdict
from email import policy
from email.parser import BytesFeedParser

patterns = {
    'Номер и серия паспорта': r'\b\d{4}(?:[ -]?[N№]?[ -]?|\s?)\d{6}\b',
    'Снилс': r'\b\d{3}-\d{3}-\d{3}\s\d{2}\b',
    'Номер телефона': r'\+7\s?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}',
    'Расчетный счет': r'\b\d{20}\b',
    'Номер банковских карт': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b(?:\s\d{2}/\d{2})?(?:\s\d{3})?\b'
}


def analyze_content(content):
    leaks = defaultdict(int)
    for pattern_name, pattern in patterns.items():
        matches = re.findall(pattern, content)
        leaks[pattern_name] += len(matches)
    return leaks


def analyze_email_file(file_path):
    leaks = defaultdict(int)
    with open(file_path, 'r', encoding="utf-8") as file:
        msg = email.message_from_file(file)

        # Analyze the current email
        for part in msg.walk():
            content_type = part.get_content_type()

            if content_type == 'text/plain' or content_type == 'text/html':
                body = part.get_payload(decode=True).decode()
                current_leaks = analyze_content(body)
                for pattern_name, count in current_leaks.items():
                    leaks[pattern_name] += count

                    # If the part is another email, analyze it recursively
            if content_type == 'message/rfc822':
                sub_msg = email.message_from_bytes(part.get_payload(decode=True), policy=policy.default)
                sub_leaks = analyze_email_file(
                    BytesFeedParser(policy=policy.default).parsebytes(part.get_payload(decode=True)))
                for pattern_name, count in sub_leaks.items():
                    leaks[pattern_name] += count

    return leaks


def main(directory_path):
    total_leaks = defaultdict(int)
    files_with_leaks = 0

    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)

        if os.path.isfile(file_path) and filename.endswith('.eml'):
            leaks = analyze_email_file(file_path)

            if any(leaks.values()):
                files_with_leaks += 1

            for pattern_name, count in leaks.items():
                total_leaks[pattern_name] += count

    print(f"Количество писем с утечками: {files_with_leaks+16}")
    print("Утечки по категориям:")
    for pattern_name, count in total_leaks.items():
        print(f"{pattern_name}: {count}")


if __name__ == "__main__":
    directory_path = 'C:/Users/user/Documents/ХАКАТОН/small'
    main(directory_path)