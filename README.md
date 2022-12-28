# Web scraper for emails and phone numbers

## Used libraries
In this project I used multiple libraries.

* **BeautifulSoup** for parsing the web pages
* **csv** for writing the extracted data
* **email_validator** to validate the emails
* **re** for using regular expressions to extract desired data and to remove unwanted data
* **requests** for obtaining the web pages

## Data preprocessing
To filter out the unwanted data from the web pages such as styles, scripts, head, title and meta I created two functions.

**tag_visible** is used to check if an element is inside style, script, head, title, meta or is a comment in which case it returns False, otherwise returns True.

```python
def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True
```

**text_from_html** parses the page code and filters the data using the tag_visible function.

```python
def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)
```

After the page text is extracted, I used two regular expressions to remove the links as they might contain sequences that resamble phone numbers and to remove scripts that might be present inside the body.

```python
page_text = re.sub(r'http\S+', '', page_text)
page_text = re.sub(r'<script[\s\S]+?/script>', "", page_text)
```

## Regular expressions
To extract the phone numbers and the emails from the page text I created two regular expressions, one that matches different phone number formats and another one that matches emails.

```python

# Create phone number regular expression
phone_regex = re.compile(
    r"(([+]\d{2})?(\d{3}|\(\d{3,4}\))?(\s|-|\.)?(\d{3,4})(\s|-|\.)?(\d{4,7})(\s*(ext|x|ext.)\s*(\d{2,5}))?)", re.VERBOSE)

# Create email id regular expression
email_regex = re.compile(
    r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+(\.[a-zA-Z]{2,4}))", re.VERBOSE)
```

## Implementation
The next step was to read the urls from sample-websites.csv and to add 'http://www.' at the beginning so that the requests library can access them.

For each page I used the preprocessing described previously and used the regular expressions for phones and emails to extract the desired data and used the email_validator library to validate the emails.

```python
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
```

After extracting the data I removed the duplicate phone numbers and emails and added them to the lists of all phone numbers and all emails, and after all the web pages were processed I wrote the emails in mails.csv and phones in phones.csv.

## Possible improvements
I tried using the **phonenumbers** library to validate the phone numbers, which provides all used phone number formats and can provide information about the number such as country code, carrier and geolocation info, but because in a lot of the pages the country code is not provided for the phone numbers it treated them as invalid.