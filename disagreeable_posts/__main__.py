from loguru import logger
from mastodon import Mastodon, StreamListener
from dotenv import load_dotenv
import trio
from pathlib import Path
import os
from sys import stderr
import json

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
    mastodon.status_post("Hello, Mastodon API!", idempotency_key='Hello, Mastodon API!')
    logger.info("Posted to Mastodon API")
    # Testing hashtags now
    mastodon.status_post("Hello, Mastodon API! #test", idempotency_key='Hello, Mastodon API! #test') # noqa E501

    # Stream public timeline asynchronously
    # logger.info("Starting public stream")
    # public = mastodon.stream_public(TheStreamListener())
    # logger.info("Started public stream")
    # # Now we need to run the stream
    # try:
    #     trio.run(public.stream, trio_token="public")
    # except KeyboardInterrupt:
    #     logger.info("Stopping public stream")
    #     public.close()
    #     logger.info("Stopped public stream")
    # Stream user timeline asynchronously
    logger.info("Starting user stream")
    user = mastodon.stream_user(TheStreamListener())
    logger.info("Started user stream")
    # Now we need to run the stream
    try:
        trio.run(user.stream, trio_token="user")
    except KeyboardInterrupt:
        logger.info("Stopping user stream")
        user.close()
        logger.info("Stopped user stream")

class TheStreamListener(StreamListener):
    def on_update(self, status):
        logger.info(f"Got update: {status['content']}") 
        # https://docs.joinmastodon.org/entities/Status/
        # https://docs.joinmastodon.org/entities/Notification/
    def on_notification(self, notification):
        if notification['type'] == 'mention':
            logger.info(f"Got <blue>mention</blue> from {notification['account']['username']}")  # noqa E501
            logger.info(f"Content: {notification['status']['content']}")
            logger.info(f"ID: {notification['status']['id']}")
            logger.info(f"URL: {notification['status']['url']}")
            logger.info(f"Visibility: {notification['status']['visibility']}")
            logger.info(f"Sensitive: {notification['status']['sensitive']}")
        if notification['type'] == 'favourite':
            logger.info(f"Got <yellow>favourite</yellow> from {notification['account']['username']}")  # noqa E501
            logger.info(f"Content: {notification['status']['content']}")
            logger.info(f"ID: {notification['status']['id']}")
            logger.info(f"URL: {notification['status']['url']}")
            logger.info(f"Visibility: {notification['status']['visibility']}")
            logger.info(f"Sensitive: {notification['status']['sensitive']}")
        else: 
            logger.info(f"Got {notification['type']} from {notification['account']['username']}")  # noqa E501



def set_primary_logger(log_level):
    logger.remove()
    # ^10 is a formatting directive to center with a padding of 10
    logger_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> |<level>{level: ^10}</level>| <level>{message}</level>"  # noqa E501
    logger.add(stderr, format=logger_format, colorize=True, level=log_level)

main()