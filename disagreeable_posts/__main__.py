import json
from loguru import logger
from mastodon import Mastodon, StreamListener
from dotenv import load_dotenv
import trio
from pathlib import Path
import os
from sys import stderr
import datetime

def main():
    load_dotenv(dotenv_path=Path('.') / '.env')
    access_token = os.getenv("MASTODON_ACCESS_TOKEN")
    api_base_url = os.getenv("MASTODON_API_BASE_URL")

    set_primary_logger("DEBUG")

    # Now login 
    mastodon = Mastodon(
        access_token=access_token,
        api_base_url=api_base_url
    )
    # Now show the username
    logger.info(f"Logged in as {mastodon.account_verify_credentials()['username']}")
    # Hello, Mastodon API!
    mastodon.status_post("Hello, Mastodon API!", idempotency_key='test-hello')
    logger.info("Posted to Mastodon API")
    # Testing hashtags now
    mastodon.status_post("Hello, Mastodon API! #test", idempotency_key='test-hashtag') # noqa E501

   
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
        # Stop the stream, but exit immediately if control c is hit again

        
async def print_time():
        time = datetime.datetime.now().strftime("%H:%M:%S")
        logger.info(f"The time is now: {time}")


class TheStreamListener(StreamListener):
    def on_update(self, status):
        # An uodate is a post made by you
        logger.info(f"Got update: {status['content']}")  # noqa E501
        
        # `default` is a parameter which sets a function to be called for objects that can't otherwise be serialized.  # noqa E501
        # In this case, it will call str(x) for any object x that it can't serialize.  # noqa E501
        # logger.info(f"JSON: {json.dumps(status, indent=4, default=str)}")

        # https://docs.joinmastodon.org/entities/Status/
        # https://docs.joinmastodon.org/entities/Notification/
    def on_notification(self, notification):
        if notification['type'] == 'mention':
            logger.opt(colors=True).info(f"Got <blue>mention</blue> from {notification['account']['username']}") # noqa E501
        elif notification['type'] == 'favourite':
            logger.opt(colors=True).info(f"Got <yellow>favourite</yellow> from {notification['account']['username']}")  # noqa E501
        else: 
            logger.info(f"Got unknown notification: {notification['type']} from {notification['account']['username']}")  # noqa E501
        logger.info(f"Content: {notification['status']['content']}")
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

main()