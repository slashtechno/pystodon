from loguru import logger
from mastodon import Mastodon
from dotenv import load_dotenv
import httpx
from pathlib import Path
import os
from sys import stderr
from . import commands
from peewee import PostgresqlDatabase


from rathercurious_mastodon.utils.command import Command, CheckThis
from rathercurious_mastodon.utils import utils

# Global variables
mastodon = Mastodon
posts_to_delete = []
DELETE_WHEN_DONE = None
weather_api_key = None
ALWAYS_MENTION = None


def main():
    global mastodon
    global DELETE_WHEN_DONE
    global ALWAYS_MENTION

    load_dotenv(dotenv_path=Path(".") / ".env")
    mastodon_access_token = os.getenv("RC_MASTODON_ACCESS_TOKEN")
    mastodon_api_base_url = os.getenv("RC_MASTODON_API_BASE_URL")
    weather_api_key = os.getenv("RC_WEATHER_API_KEY")

    DELETE_WHEN_DONE = os.getenv("RC_DELETE_POSTS_AFTER_RUN", "False").lower() == "true"  # noqa E501
    ALWAYS_MENTION = os.getenv("RC_ALWAYS_MENTION", "False").lower() == "true"
    pg_db = PostgresqlDatabase(
        os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_DB_HOST"),
        port=os.getenv("POSTGRES_DB_PORT"),
    )
    commands.peewee_proxy.initialize(pg_db)
    

    set_primary_logger("DEBUG")

    logger.info("RC_ALWAYS_MENTION: " + str(ALWAYS_MENTION))
    logger.info("RC_DELETE_POSTS_AFTER_RUN: " + str(DELETE_WHEN_DONE))

    # Setup config
    try:
        set_weather_key(weather_api_key)
    except ValueError as e:
        if str(e) == "Invalid API key":
            logger.error("Invalid API key")
            exit(1)
        else:
            raise e

    # Setup checks
    CheckThis.add_check(
        CheckThis(
            function=lambda: logger.info("Test check"),
            # description="Check 1",
            interval=5,
        )
    )

    # Setup commands
    # Test command that returns "test"
    Command.add_command(Command(hashtag="test", function=lambda status: "test", help_arguments={}))
    Command.add_command(
        Command(
            hashtag="remindme",
            function=commands.RemindMe.remind_me_in,
            help_arguments= commands.RemindMe.help_arguments
        )
    )
    # Weather command
    Command.add_command(
        Command(
            hashtag="weather",
            function=commands.weather,
            help_arguments={
                "Latitude, Longitude": "The latitude and longitude to get the weather for. For example, 51.5074, 0.1278"  # noqa E501
            },
            # Pass this kwarg 
            weather_api_key=weather_api_key,
        )
    )

    # Timezone command
    Command.add_command(
        Command(
            hashtag="timezone",
            function=commands.timezone,
            help_arguments={
                "timezone": "The timezone to get the time in. For a list of timezones, see https://en.wikipedia.org/wiki/List_of_tz_database_time_zones"  # noqa E501
            },
        )
    )

    stream_listener = utils.stream_listener(
        mastodon_access_token=mastodon_access_token,
        mastodon_api_base_url=mastodon_api_base_url,
        delete_when_done=DELETE_WHEN_DONE,
        always_mention=ALWAYS_MENTION,
    )
    stream_listener.stream()



def set_primary_logger(log_level):
    global logger
    logger.remove()
    # ^10 is a formatting directive to center witzh a padding of 10
    logger_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> |<level>{level: ^10}</level>| <level>{message}</level>"  # noqa E501
    logger.add(stderr, format=logger_format, colorize=True, level=log_level)
    # logger = logger.opt(ansi=True)# noqa F841


def set_weather_key(key: str):
    global weather_api_key

    """If an API key works, set the class API key."""
    # Test API key to make sure it works
    params = {"key": key, "aqi": "no", "q": "London"}
    url = "https://api.weatherapi.com/v1/current.json"
    response = httpx.get(url=url, params=params)
    if response.status_code == 200:
        weather_api_key = key
    elif response.status_code == 403:
        raise ValueError("Invalid API key")
    else:
        response.raise_for_status()


main()
