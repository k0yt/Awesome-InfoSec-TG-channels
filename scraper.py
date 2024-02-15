# -*- coding: utf-8

from bs4 import BeautifulSoup
import requests
import re

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
        return '', 0, '', '', ''
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к {url}: {e}")
        return '', 0, '', '', ''

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        title = sanitize_title(soup.find('div', class_='tgme_page_title').text) \
            if soup.find('div', class_='tgme_page_title') else ''
        title = title.strip()

        subscribers_text = soup.find('div', class_='tgme_page_extra').text.strip() \
            if soup.find('div', class_='tgme_page_extra') else '0 subscribers'

        if "members" in subscribers_text:
            subscribers_for_sort = re.search(r'([\d\s]+) members', subscribers_text).group(1)
            subscribers_for_sort = ''.join(subscribers_for_sort.split())  
        else:
            subscribers_for_sort = int(re.sub(r'[^\d]', '', subscribers_text.split(' ')[0]))

        if "online" in subscribers_text:
            subscribers_number = subscribers_text
        else:
            subscribers_number = re.sub(r'[^0-9 ]', '', subscribers_text).strip() + " subscribers"

        description = soup.find('div', class_='tgme_page_description').text.strip().lower() \
            if soup.find('div', class_='tgme_page_description') else ''

        admin_info = admin_from_file  
        if not admin_info:  
            keywords_pattern = '|'.join([re.escape(keyword) for keyword in keywords])
            pattern = r'({})[^\w@]*(@[a-zA-Z0-9_]+)'.format(keywords_pattern)
            match = re.search(pattern, description)
            if match:
                admin_info = match.group(2)

        return title, subscribers_for_sort, subscribers_number, admin_info, description
    else:
        return '', 0, '', '', ''


def read_file_and_get_info(filename):
    channels = {}
    unique_tags = set()
    line_count = 0
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue  

            parts = line.split(' - ')
            url_tags = parts[0].split('@')
            url = url_tags[0].strip()
            has_additional_values = '@' in parts[0] or len(parts) > 1

            if url in channels and not has_additional_values:
                continue

            channels[url] = line
            
            line_count += 1
            if len(parts) > 1:
                tags_part = parts[1].split(',')
                for tag in tags_part:
                    unique_tags.add(tag.strip())

    # список без дубликатов
    for url, full_line in channels.items():
        parts = full_line.split(' - ')
        admin_from_file = '@' + parts[0].split('@')[1].strip() if '@' in parts[0] else ''
        tags = parts[1] if len(parts) > 1 else ''
        title, subscribers_for_sort, subscribers_display, admin_info, description = get_telegram_channel_info(url, admin_from_file)
        if title:
            channels[url] = (title, subscribers_for_sort, subscribers_display, admin_info, description, url, tags)

    sorted_channels = sorted(channels.values(), key=lambda x: x[1], reverse=True)

    with open('README.md', 'w', encoding='utf-8') as outfile:
        outfile.write("# Awesome-InfoSec-TG-channels \n\n")
        outfile.write(f"{line_count-1} channels, for the most part RUS \n")
        outfile.write(f"\n**{len(unique_tags)} Unique Tags:**\n")
        for tag in sorted(unique_tags):
            outfile.write(f" {tag}")
        outfile.write("\n\n**Adding new channels in file 'channels.txt'**\n")
        outfile.write("> Usage: <link> @<admin_name> - <tag_1>, <tag_2>\n\n")
        outfile.write("| No | Name | Num of subs | Author | Description | Thematics |\n")
        outfile.write("| --- | --- | --- | --- | --- | --- |\n")

        for index, channel in enumerate(sorted_channels, start=1):
            title, subscribers_for_sort, subscribers_display, admin_info, description, url, tags = channel
            admin_display = admin_info if admin_info else ''
            output_line = f"| {index} | [{title}]({url}) | {subscribers_display} | {admin_display} | {description} | {tags} \n"
            outfile.write(output_line)


read_file_and_get_info('channels.txt')
