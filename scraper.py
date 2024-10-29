# -*- coding: utf-8 -*- 

from bs4 import BeautifulSoup
import requests
import re
import time

keywords = [
    "администратор", "админ", "admin", "owner", "модератор", "moderator", "mod",
    "организатор", "organizer", "основатель", "founder", "владелец", "куратор",
    "curator", "главный", "chief", "head", "редактор", "editor", "создатель",
    "creator", "управляющий", "manager", "лидер", "leader", "ceo", "связь", 
    "сотрудничество", "поддержка", "contact", "связаться"
]

def sanitize_title(title):
    return re.sub(r'[^\w\s\-\_\(\)\[\]\{\}\,\.]', '', title)

def get_telegram_channel_info(url, admin_from_file=''):
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        description_element = soup.find('div', class_='tgme_page_description')
        description = description_element.text.strip().lower() if description_element else ''
        if "if you have telegram, you can contact" in description:
            return '', 0, '', '', '', True
    except requests.exceptions.RequestException as e:
        print('----------------------------------------------')
        print(f"Не удалось получить данные для {url}: {str(e)}")
        print('----------------------------------------------')
        return '', 0, '', '', '', True

    title_element = soup.find('div', class_='tgme_page_title')
    title = sanitize_title(title_element.text.strip()) if title_element else ''
    subscribers_text = soup.find('div', class_='tgme_page_extra').text if soup.find('div', class_='tgme_page_extra') else ''
    subscribers_text = subscribers_text.strip()
    subscribers_for_sort = 0
    match = re.search(r'([\d\s]+) (members|subscribers)', subscribers_text)
    if match:
        subscribers_for_sort = int(''.join(match.group(1).split()))
    subscribers_number = str(subscribers_for_sort) + " members" if subscribers_for_sort else '0 members'
    admin_info = admin_from_file
    keywords_pattern = '|'.join([re.escape(keyword) for keyword in keywords])
    pattern = r'({})[^\w@]*(@[a-zA-Z0-9_]+)'.format(keywords_pattern)
    match = re.search(pattern, description)
    admin_info = match.group(2) if match else ''
    return title, subscribers_for_sort, subscribers_number, admin_info, description, False

def read_file_and_get_info(filename):
    channels = {}
    unique_tags = set()
    line_count = 0
    it = 0
    with open(filename, 'r', encoding='utf-8') as file:
        print('Ссылки протухли и не используются: ')
        for line in file:
            line = line.strip()
            it += 1
            if not line:
                continue
            parts = line.split(' - ')
            url = parts[0].split('@')[0].strip()
            admin_from_file = '@' + parts[0].split('@')[1].strip() if '@' in parts[0] else ''
            tags = parts[1] if len(parts) > 1 else ''
            if (it % 250 == 0):
                time.sleep(20)
            title, subscribers_for_sort, subscribers_display, admin_info, description, is_deleted = get_telegram_channel_info(url, admin_from_file)
            if not is_deleted:
                channels[url] = (title, subscribers_for_sort, subscribers_display, admin_info, description, url, tags)
                unique_tags.update([tag.strip() for tag in tags.split(',')])
                line_count += 1
            else:
                print(f'line: {it} - {url}')

                
    sorted_channels = sorted(channels.values(), key=lambda x: x[1], reverse=True)
    with open('README.md', 'w', encoding='utf-8') as outfile:
        outfile.write("# Awesome-InfoSec-TG-channels \n\n")
        outfile.write(f"{len(sorted_channels)} channels, for the most part RUS \n")
        outfile.write(f"\n**{len(unique_tags)} Unique Tags:**\n")
        for tag in sorted(unique_tags):
            outfile.write(f" {tag}")
        outfile.write("\n\n**Adding new channels in file 'channels.txt'**\n")
        outfile.write("\nUsage: \n > https://t.me/link @admin_name - tag_1, tag_2\n\n")
        outfile.write("\n\n ### Channels \n")
        outfile.write("<details> \n")
        outfile.write("> | No | Name | Num of subs | Admin | Thematics | Description |\n")
        outfile.write("> | --- | --- | --- | --- | --- | --- |\n")
        for index, channel in enumerate(sorted_channels, start=1):
            title, subscribers_for_sort, subscribers_display, admin_info, description, url, tags = channel
            admin_display = admin_info if admin_info else ''
            output_line = f"> | {index} | [{title}]({url}) | {subscribers_display} | {admin_display} | {tags} | {description} \n"
            outfile.write(output_line)
        outfile.write("\n</details> \n")
        outfile.write("\n\n ### Useful Bot`s \n")
        outfile.write("<details> \n")
        outfile.write("> | No | Name | Channel | Thematics | Description |\n")
        outfile.write("> | --- | --- | --- | --- | --- |\n")
        outfile.write("> | 1 | Example | Example | Example | Example |\n")
        outfile.write("\n</details> \n")

read_file_and_get_info('channels.txt')
