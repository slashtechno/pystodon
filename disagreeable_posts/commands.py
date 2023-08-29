import re
import trafilatura 
import pytz 
import datetime

def timezone(status):
    '''
    Return the time in a timezone.
    ''' 
    # Get the timezone
    # if matches := re.search(r'#timezone\s([\w|\s|,]+)')
    if matches := re.search(r'#timezone\s(\w+\/\w+)', trafilatura.extract(status['content'])):
        timezone = matches.group(1)
    else:
        return None
    if timezone not in pytz.all_timezones:
        return "Invalid timezone. For more information, see https://en.wikipedia.org/wiki/List_of_tz_database_time_zones"
    
    # Get the time  
    now = datetime.datetime.now(pytz.timezone(timezone))
    return f"The time in {timezone} is {now.strftime('%H:%M:%S')}"