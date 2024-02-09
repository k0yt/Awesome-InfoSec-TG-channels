# -*- coding: utf-8

import requests
from bs4 import BeautifulSoup
import re

# TODO: fix problems with chat without link @

keywords = [
    "администратор", "админ", "admin", "owner", "модератор", "moderator", "mod",
    "организатор", "organizer", "основатель", "founder", "владелец", "куратор",
    "curator", "главный", "chief", "head", "редактор", "editor", "создатель",
    "creator", "управляющий", "manager", "лидер", "leader", "ceo", "связь", "сотрудничество", "поддержка"
]


def sanitize_title(title):
    sanitized_title = re.sub(r'[^\w\s\-\_\(\)\[\]\{\}\,\.]', '', title)
    return sanitized_title


def get_telegram_channel_info(url, admin_from_file=''):

    try:
        response = requests.get(url, timeout=30)
    except requests.exceptions.ConnectTimeout:
        print(f"Timeout при подключении к {url}")
        return '', 0, '', ''
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к {url}: {e}")
        return '', 0, '', ''

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        title = sanitize_title(soup.find('div', class_='tgme_page_title').text) \
            if soup.find('div', class_='tgme_page_title') else ''
        title = title.strip()

        subscribers = soup.find('div', class_='tgme_page_extra').text \
            if soup.find('div', class_='tgme_page_extra') else '0'
        subscribers_number = int(re.sub(r'\D', '', subscribers)) \
            if re.sub(r'\D', '', subscribers).isdigit() else 0

        description = soup.find('div', class_='tgme_page_description').text.strip().lower() \
            if soup.find('div', class_='tgme_page_description') else ''

        admin_info = admin_from_file  # Используем значение из файла, если оно передано
        if not admin_info:  # Ищем в описании, только если значение из файла не задано
            keywords_pattern = '|'.join([re.escape(keyword) for keyword in keywords])
            pattern = r'({})[^\w@]*(@[a-zA-Z0-9_]+)'.format(keywords_pattern)
            match = re.search(pattern, description)
            if match:
                admin_info = match.group(2)

        return title, subscribers_number, admin_info, description
    else:
        return '', 0, '', ''


def read_file_and_get_info(filename):
    channels = []
    line_count = 0
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            line_count += 1
            parts = line.strip().split(' - ')
            url_tags = parts[0].split('@')
            url = url_tags[0].strip()
            admin_from_file = '@' + url_tags[1].strip() if len(url_tags) > 1 else ''
            tags = parts[1] if len(parts) > 1 else ''
            title, subscribers, admin_info, description = get_telegram_channel_info(url, admin_from_file)

            if title:
                channels.append((title, subscribers, admin_info, description, url, tags))

    sorted_channels = sorted(channels, key=lambda x: x[1], reverse=True)

    with open('README.md', 'w', encoding='utf-8') as outfile:
        outfile.write("# Awesome-InfoSec-TG-channels \n\n")
        outfile.write(f"{line_count} channels \n for the most part RUS \n\n")
        outfile.write("Usage: <link> @<admin_name> - <tag_1>, <tag_2>\n")
        outfile.write("Adding new in file channels.txt\n\n")
        outfile.write("| No | Name | Num of subs | Author | Description | Thematics |\n")
        outfile.write("| --- | --- | --- | --- | --- | --- |\n")

        for index, channel in enumerate(sorted_channels, start=1):
            title, subscribers, admin_info, description, url, tags = channel
            admin_display = admin_info if admin_info else ''
            output_line = f"| {index} | [{title}]({url}) |{subscribers} | {admin_display} | {description} | {tags} \n"
            outfile.write(output_line)


read_file_and_get_info('channels.txt')
