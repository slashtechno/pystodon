import re
import trafilatura 
import pytz 
import datetime
import airportsdata
from .utils import utils

def timezone(status: dict):
    '''
    Return the time in a timezone.
    ''' 
    # Get the timezone
    # Since regex is being used anyway, no point in using utils.return_raw_argument()
    # "^$" isn't being used, so it's fine
    if matches := re.search(r'(\w+\/\w+)', utils.parse_html(status['content'])): # 
        timezone = matches.group(1)
    else:
        return "Seems like you didn't specify a timezone. For more information, see https://en.wikipedia.org/wiki/List_of_tz_database_time_zones" # noqa E501
    if timezone not in pytz.all_timezones:
        return "Invalid timezone. For more information, see https://en.wikipedia.org/wiki/List_of_tz_database_time_zones"
    
    # Get the time  
    now = datetime.datetime.now(pytz.timezone(timezone))
    return f"The time in {timezone} is {now.strftime('%H:%M:%S')}"

def weather(status: dict):
    '''Return weather for a latitude and longitude'''

    # Get the latitude and longitude
    # Regex for getting a float "((?:[+-]?)(?:[0-9]*)(?:[.][0-9]*)?)"
    regex = r'((?:[+-]?)(?:[0-9]*)(?:[.][0-9]*)?)(?:\s*,\s*)((?:[+-]?)(?:[0-9]*)(?:[.][0-9]*)?)' # noqa E501
    if matches := re.search(regex, utils.parse_html(status['content'])):
        latitude = matches.group(1)
        longitude = matches.group(2)
    else: 
        return "Seems like you didn't specify a latitude and longitude. Please do so in the format <latitude>, <longitude>" # noqa E501
    if not (-90 <= float(latitude) <= 90):
        return "Invalid latitude. Please specify a latitude between -90 and 90"
    if not (-180 <= float(longitude) <= 180):
        return "Invalid longitude. Please specify a longitude between -180 and 180"
    
    # Get the weather
    # TODO: Get the weather