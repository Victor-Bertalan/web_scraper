from bs4 import BeautifulSoup
from bs4.element import Comment
import csv
from email_validator import validate_email
import re
import requests



# Get only elements from body
def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


# Filter page code to extract body text
def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)


# Create phone number regular expression
phone_regex = re.compile(
    r"(([+]\d{2})?(\d{3}|\(\d{3,4}\))?(\s|-|\.)?(\d{3,4})(\s|-|\.)?(\d{4,7})(\s*(ext|x|ext.)\s*(\d{2,5}))?)", re.VERBOSE)

# Create email id regular expression
email_regex = re.compile(
    r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+(\.[a-zA-Z]{2,4}))", re.VERBOSE)

all_phones = []
all_mails = []

with open("sample-websites.csv") as csv_file:
    urls = []
    for url in csv_file:
        url = url.strip()
        # Add http://www. to urls so they can be accesed using requests.get()
        page_url = ''.join(('http://www.', url))
        urls.append(page_url)
    
    # Remove sample-websites.csv header (domains)
    urls.pop(0)

    for page_url in urls:
        try:
            print("Opening URL:", page_url)
            
            # Get page code, transform into string and filter out unwanted sections like style, script, header etc
            page_data = requests.get(page_url)
            page_html = str(page_data.content)
            page_text = text_from_html(page_html)

            # Remove urls as they might contain numbers that resamble phone numbers
            page_text = re.sub(r'http\S+', '', page_text)
            # Remove scripts inside body
            page_text = re.sub(r'<script[\s\S]+?/script>', "", page_text)

            phones = []
            mails = []

            # Find phone numbers in page text using the phone_regex
            for groups in phone_regex.findall(page_text):
                phone_number = groups[0]
                phones.append(phone_number.strip())

            # Find emails in page text using the email_regex and validate them using the email_validator library
            for groups in email_regex.findall(page_text):
                try:
                    validator = validate_email(groups[0])
                    mail = validator['email']
                    mails.append(mail)
                except:
                    pass

            # Remove duplicate data from phones and emails
            phones = list(dict.fromkeys(phones))
            mails = list(dict.fromkeys(mails))
            all_phones.append(phones)
            all_mails.append(mails)

        except:
            print(page_url+' not found')

# Write phone numbers in phones.csv
with open('phones.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    for phones in all_phones:
        if phones:
            writer.writerow(phones)

# Write emails in emails.csv
with open('mails.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    for mails in all_mails:
        if mails:
            writer.writerow(mails)
