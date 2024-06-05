import re
import pytz
import datetime
from rathercurious_mastodon.lib import utils
from rathercurious_mastodon.utils.logging import logger
from rathercurious_mastodon.utils.cli_args import args
import httpx
import dateparser
from mastodon import Mastodon

# https://docs.peewee-orm.com/en/latest/peewee/quickstart.html
# https://docs.peewee-orm.com/en/latest/peewee/models.html#field-types-table
import peewee
import json

# https://stackoverflow.com/a/45043715
# https://timlehr.com/2018/01/lazy-database-initialization-with-peewee-proxy-subclasses/
peewee_proxy = peewee.Proxy()


class RelativeReminder(peewee.Model):
    """
    A class to represent a reminder that stores a status dict and a datetime
    """

    status = peewee.TextField()
    datetime = peewee.DateTimeField()

    class Meta:
        database = peewee_proxy


class RemindMe:
    """Functions related to reminding the user of posts"""

    help_arguments = {
        "remind_me_in": 'Remind you of a post in a specified time. For example, writing "in 5 minutes" will remind you in 5 minutes. Whilst it may work without it, it is recommended to specify "in" before the time. Dateparser is used to parse the time, so it should be able to understand various formats. For more information, see https://dateparser.readthedocs.io/en/latest/',
    }

    @staticmethod
    def remind_me_in(status: dict):
        """
        Add the current status and the time to a database.
        """
        dt = dateparser.parse(utils.return_raw_argument(status))
        if dt is None:
            return "Invalid time. For more information, see https://dateparser.readthedocs.io/en/latest/"
        # Make it so the datetime only goes to the minute (no seconds or lower denominations)
        dt = dt.replace(second=0, microsecond=0)
        # Add the reminder to the database
        # If the table doesn't exist, create it)
        peewee_proxy.connect()
        if not RelativeReminder.table_exists():
            peewee_proxy.create_tables([RelativeReminder])
        RelativeReminder(status=json.dumps(status, default=str), datetime=dt).save()
        peewee_proxy.close()
        return f"Reminder set for {dt.strftime('%Y-%m-%d %H:%M:%S')}"

    @staticmethod
    def list_reminders():
        """
        Check the database for reminders that are due.
        """
        # Check all reminders that match the current date (to the minute)
        now = datetime.datetime.now().replace(second=0, microsecond=0)
        peewee_proxy.connect()
        try:
            # Select all columns where the datetime is now
            for reminder in RelativeReminder.select().where(RelativeReminder.datetime == now):
                status = json.loads(reminder.status)
                # Return the status
                yield status
                # Delete the reminder
                reminder.delete_instance()
        except peewee.ProgrammingError as e:
            if "does not exist" in str(e):
                peewee_proxy.close()
                return
            else:
                raise e
        peewee_proxy.close()

    @classmethod
    def remind_user(cls, status: dict):
        """
        Remind the user of a post.
        """
        mastodon = Mastodon(access_token=cls.mastodon_access_token, api_base_url=cls.mastodon_api_base_url)
        content = f"@{status['account']['acct']}\nHere's your reminder!"
        mastodon.status_post(
            status=content,
            in_reply_to_id=status["id"],
            visibility=status["visibility"],
        )

    # Getters and setters for mastodon_api_base_url and mastodon_access_token
    @property
    def mastodon_api_base_url(cls):
        return cls._mastodon_api_base_url

    @mastodon_api_base_url.setter
    def mastodon_api_base_url(cls, value):
        cls._mastodon_api_base_url = value

    @property
    def mastodon_access_token(cls):
        return cls._mastodon_access_token

    @mastodon_access_token.setter
    def mastodon_access_token(cls, value):
        cls._mastodon_access_token = value


def remind():
    """
    Check the database for reminders that are due and remind the user.
    """
    for status in RemindMe.list_reminders():
        RemindMe.remind_user(status)


def timezone(status: dict):
    """
    Return the time in a timezone.
    """
    # Get the timezone
    # Since regex is being used anyway, no point in using utils.return_raw_argument()
    # "^$" isn't being used, so it's fine
    # This is looking for a string in the format "<one or more words>/<one or more words>"
    if matches := re.search(r"(\w+\/\w+)", utils.parse_html(status["content"])):  #
        timezone = matches.group(1)
    else:
        return "Seems like you didn't specify a timezone. For more information, see https://en.wikipedia.org/wiki/List_of_tz_database_time_zones"  # noqa E501
    if timezone not in pytz.all_timezones:
        return "Invalid timezone. For more information, see https://en.wikipedia.org/wiki/List_of_tz_database_time_zones"

    # Get the time
    now = datetime.datetime.now(pytz.timezone(timezone))
    return f"The time in {timezone} is {now.strftime('%H:%M:%S')}"


def weather(status: dict, weather_api_key: str):
    """
    Return the current weather for the location nearest to the specified coordinates.
    Uses the WeatherAPI API.
    """

    # Get the latitude and longitude
    # Regex for getting a float "((?:[+-]?)(?:[0-9]*)(?:[.][0-9]*)?)"
    # Again, since regex is being used anyway, no point in using utils.return_raw_argument()
    regex = r"((?:[+-]?)(?:[0-9]*)(?:[.][0-9]*)?)(?:\s*,\s*)((?:[+-]?)(?:[0-9]*)(?:[.][0-9]*)?)"  # noqa E501
    if matches := re.search(regex, utils.parse_html(status["content"])):
        latitude = matches.group(1)
        longitude = matches.group(2)
    else:
        return "Seems like you didn't specify a latitude and longitude. Please do so in the format <latitude>, <longitude>"  # noqa E501
    if not (-90 <= float(latitude) <= 90):
        return "Invalid latitude. Please specify a latitude between -90 and 90"
    if not (-180 <= float(longitude) <= 180):
        return "Invalid longitude. Please specify a longitude between -180 and 180"

    # Make the request
    params = {"key": weather_api_key, "aqi": "no", "q": f"{latitude},{longitude}"}
    url = "https://api.weatherapi.com/v1/current.json"
    response_dict = httpx.get(url=url, params=params).json()

    # Get the weather and location name (name, region, country)
    weather_c = response_dict["current"]["temp_c"]
    weather_f = response_dict["current"]["temp_f"]
    feelslike_c = response_dict["current"]["feelslike_c"]
    feelslike_f = response_dict["current"]["feelslike_f"]
    conditions = response_dict["current"]["condition"]["text"]

    # Get the location details
    location_name = response_dict["location"]["name"]
    # location_region = response_dict['location']['region']
    # location_country = response_dict['location']['country']
    # location_full = f"{location_name}, {location_region}, {location_country}"
    location_full = location_name

    # Construct the message
    lines = [
        f"Conditions in {location_full}: {conditions}",
        f"The temperature is {weather_c}°C ({weather_f}°F)",
        f"The temperature feels like {feelslike_c}°C ({feelslike_f}°F)",
    ]
    logger.warning("Always mentioning is disabled and the user will not be mentioned, even though this is a DM") if (args.always_mention is False) and (status["visibility"] == "direct") else None 
    return "\n".join(lines)
