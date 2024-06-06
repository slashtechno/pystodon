import argparse
import os
import sys
from pathlib import Path

# Can't do from pystodon.utils import logger since that would cause a circular import
from pystodon.utils.logging import logger

import dotenv


def set_argparse() -> None:
    """
    Set up the argument parser and parse the arguments to args
    """
    global args

    if Path(".env").is_file():
        dotenv.load_dotenv()
        logger.info("Loaded .env file")
    else:
        logger.warning(".env file not found")
    argparser = argparse.ArgumentParser(description="A Mastodon bot that does things.")
    argparser.add_argument(
        "--mastodon-access-token",
        default=os.getenv("RC_MASTODON_ACCESS_TOKEN"),
        help="The access token for the Mastodon bot.",
    )
    argparser.add_argument(
        "--mastodon-api-base-url",
        default=os.getenv("RC_MASTODON_API_BASE_URL"),
        help="The base URL for the Mastodon API.",
    )
    argparser.add_argument(
        "--weather-api-key",
        default=os.getenv("RC_WEATHER_API_KEY"),
        help="The API key for the weather API.",
    )
    (
        argparser.add_argument(
            "--delete-posts-after-run",
            action="store_true",
            # A default (value when unset) needs to be set since .lower() will be called on it and it should be a string
            default=os.getenv("RC_DELETE_POSTS_AFTER_RUN", "False").lower() == "true",
            help="Delete posts when gracefully exiting the program.",
        ),
    )
    (
        argparser.add_argument(
            "--always-mention",
            action="store_true",
            default=os.getenv("RC_ALWAYS_MENTION", "False").lower() == "true",
            help="Always mention the user in the response.",
        ),
    )

    db = argparser.add_argument_group("Database options")
    db.add_argument(
        "--postgres-db",
        default=os.getenv("POSTGRES_DB"),
        help="The name of the Postgres database.",
    )
    db.add_argument(
        "--postgres-user",
        default=os.getenv("POSTGRES_USER"),
        help="The username for the Postgres database.",
    )
    db.add_argument(
        "--postgres-password",
        default=os.getenv("POSTGRES_PASSWORD"),
        help="The password for the Postgres database.",
    )
    db.add_argument(
        "--postgres-host",
        default=os.getenv("POSTGRES_HOST"),
        help="The host for the Postgres database.",
    )
    db.add_argument(
        "--postgres-port",
        default=os.getenv("POSTGRES_PORT"),
        help="The port for the Postgres database.",
    )

    debug = argparser.add_argument_group("Debugging options")
    debug.add_argument(
        "--log-level",
        default="DEBUG",
        help="The log level to use.",
    )
    check_required_args(["mastodon_access_token", "mastodon_api_base_url"], argparser)
    args = argparser.parse_args()


def check_required_args(required_args: list[str], argparser: argparse.ArgumentParser):
    """
    Check if required arguments are set
    Useful if using enviroment variables with argparse as default and required are mutually exclusive
    """
    for arg in required_args:
        args = argparser.parse_args()
        if getattr(args, arg) is None:
            # raise ValueError(f"{arg} is required")
            logger.critical(f"{arg} is required")
            sys.exit(1)


set_argparse()
