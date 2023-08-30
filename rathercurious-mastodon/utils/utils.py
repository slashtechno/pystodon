from bs4 import BeautifulSoup
import re

def return_raw_argument(status: dict):
    '''
    Return the raw arguments (everything after the hashtag) as a string. 
    Uses utils.parse_html() to parse the HTML, adding newlines after every <p> tag
    In many cases, if regex is being used anyway, it's better to use that instead
    '''
    content = parse_html(html_content=status['content'])
    # Match from the beginning of the string, a hashtag, a space, and then ANYTHING, including newlines # noqa E501
    # re.DOTALL is present so commands can span multiple lines
    if matches := re.search(
        r'^(?:@\w+\s+)(?:#\w+\s+)(.+)$', 
        # TODO: mke mention optional as the "@<account" will not be present if it's a reply
        content, 
        flags=re.IGNORECASE | re.DOTALL
        ):
        return matches.group(1)
    else:
        # Unsure if it should return None or an empty string
        return None

def parse_html(html_content:str):
    '''Return the raw post content, with newlines after every <p> tag'''

    content = BeautifulSoup(html_content, 'html.parser')
    for p in content.find_all('p'):
        p.insert_after('\n')
        # Perhaps don't insert a newline if it's the last <p> tag?
    raw_content = content.get_text(separator='')
    return raw_content