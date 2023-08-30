from loguru import logger
from mastodon import Mastodon, StreamListener
from dotenv import load_dotenv
import trio
import httpx
from pathlib import Path
import os
from sys import stderr
import datetime
from . import commands

from .utils.command import Command

# Global variables
mastodon = Mastodon
posts_to_delete = []
delete_when_done = None
WEATHER_API_KEY = None

def main():
    global mastodon
    global delete_when_done
    load_dotenv(dotenv_path=Path(".") / ".env")
    mastodon_access_token = os.getenv("RC_MASTODON_ACCESS_TOKEN")
    mastodon_api_base_url = os.getenv("RC_MASTODON_API_BASE_URL")
    WEATHER_API_KEY = os.getenv("RC_WEATHER_API_KEY")

    delete_when_done = os.getenv("RC_DELETE_POSTS_AFTER_RUN", "False").lower() == "true"  # noqa E501

    set_primary_logger("DEBUG")

    logger.info("RC_DELETE_POSTS_AFTER_RUN: " + str(delete_when_done))

    # Setup config
    try:
        set_weather_key(WEATHER_API_KEY)
    except ValueError as e:
        if str(e) == "Invalid API key":
            logger.error("Invalid API key")
            exit(1)
        else:
            raise e

        
    # Setup commands
    # Test command that returns "test"
    Command.add_command(
        Command(
            hashtag="test",
            function = lambda status: "test",
            help_arguments={}
        )
    )

    # Weather command
    Command.add_command(
        Command(
            hashtag="weather",
            function = commands.weather,
            help_arguments={
                "Latitude, Longitude": "The latitude and longitude to get the weather for. For example, 51.5074, 0.1278"  # noqa E501
            },
            weather_api_key=WEATHER_API_KEY
        )
    )

    # Timezone command
    Command.add_command(
        Command(
            hashtag="timezone",
            function = commands.timezone,
            help_arguments={
                "timezone": "The timezone to get the time in. For a list of timezones, see https://en.wikipedia.org/wiki/List_of_tz_database_time_zones"  # noqa E501
            }
        )
    )


    # Now login
    mastodon = Mastodon(access_token=mastodon_access_token, api_base_url=mastodon_api_base_url)
    # Now show the username
    logger.info(f"Logged in as {mastodon.account_verify_credentials()['username']}")
    
    # Hello, Mastodon API!
    # mastodon.status_post("Hello, Mastodon API!", idempotency_key="test-hello")
    # logger.info("Posted to Mastodon API")
    # Testing hashtags now
    # mastodon.status_post(
        # "Hello, Mastodon API! #test", idempotency_key="test-hashtag"
    # ) 

    logger.info("Starting user stream")
    stream = mastodon.stream_user(TheStreamListener(), run_async=True)
    logger.info("Started user stream")
    trio.run(sleep_or_not, stream)


async def sleep_or_not(stream):
    # Experimenting with running other code while the stream is running
    try:
        async with trio.open_nursery() as nursery:
            nursery.start_soon(trio.sleep_forever)
            nursery.start_soon(print_time)
    except KeyboardInterrupt:
        logger.info("Stopping user stream")
        logger.debug(delete_when_done)
        if delete_when_done:
            logger.info("Deleting posts")
            for post in posts_to_delete:
                mastodon.status_delete(post)
    

async def print_time():
    time = datetime.datetime.now().strftime("%H:%M:%S")
    logger.info(f"The time is now: {time}")


class TheStreamListener(StreamListener):
    def on_update(self, status):
        # As far as I can tell, an update caused when you reblog or when an account you follow posts something  # noqa E501
        logger.info(f"Got update: {status['content']}")  # noqa E501

        # `default` is a parameter which sets a function to be called for objects that can't otherwise be serialized.  # noqa E501
        # In this case, it will call str(x) for any object x that it can't serialize.  # noqa E501
        # logger.info(f"JSON: {json.dumps(status, indent=4, default=str)}")

        # https://docs.joinmastodon.org/entities/Status/
        # https://docs.joinmastodon.org/entities/Notification/

    def on_notification(self, notification):
        if notification["type"] == "mention":
            logger.opt(colors=True).info(
                f"Got <blue>mention</blue> from {notification['account']['username']}"
            )
            content = Command.parse_status(notification["status"])
            post = mastodon.status_post(
                content,
                in_reply_to_id=notification["status"]["id"],
            )
            # TODO: If the incoming message is a DM, send a DM back, not a public reply
            posts_to_delete.append(post["id"])

        elif notification["type"] == "favourite":
            logger.opt(colors=True).info(
                f"Got <yellow>favourite</yellow> from {notification['account']['username']}"  # noqa E501
            )
        else:
            logger.info(
                f"Got unknown notification: {notification['type']} from {notification['account']['username']}"  # noqa E501
            )
        logger.debug(f"Content: {notification['status']['content']}")
        # logger.info(f"Text content: {content}")
        logger.info(f"ID: {notification['status']['id']}")
        logger.info(f"URL: {notification['status']['url']}")
        logger.info(f"Visibility: {notification['status']['visibility']}")
        logger.info(f"Sensitive: {notification['status']['sensitive']}")


def set_primary_logger(log_level):
    global logger
    logger.remove()
    # ^10 is a formatting directive to center witzh a padding of 10
    logger_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> |<level>{level: ^10}</level>| <level>{message}</level>"  # noqa E501
    logger.add(stderr, format=logger_format, colorize=True, level=log_level)
    # logger = logger.opt(ansi=True)# noqa F841

def set_weather_key(key: str):
    """If an API key works, set the class API key."""
    # Test API key to make sure it works
    params = {"key": key, "aqi": "no", "q": "London"}
    url = "https://api.weatherapi.com/v1/current.json"
    response = httpx.get(url=url, params=params)
    if response.status_code == 200:
        WEATHER_API_KEY = key
    elif response.status_code == 403:
        raise ValueError("Invalid API key")
    else:
        response.raise_for_status()
    

main()
