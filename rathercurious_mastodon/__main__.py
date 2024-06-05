import httpx
from . import commands
from peewee import PostgresqlDatabase


from rathercurious_mastodon.lib.command import Command, CheckThis
from rathercurious_mastodon.lib import utils
from rathercurious_mastodon.utils.logging import logger
from rathercurious_mastodon.utils.cli_args import args

# Global variables
posts_to_delete = []


def main():
    commands.RemindMe.mastodon_access_token = args.mastodon_access_token
    commands.RemindMe.mastodon_api_base_url = args.mastodon_api_base_url

    # If the weather API key is set, check if it's valid
    # If it's valid, add the weather command
    if args.weather_api_key:
        if check_if_weather_api_key_is_valid(args.weather_api_key):
            logger.info("Weather API key is valid; adding weather command")
            Command.add_command(
                Command(
                    hashtag="weather",
                    function=commands.weather,
                    help_arguments={
                        "Latitude, Longitude": "The latitude and longitude to get the weather for. For example, 51.5074, 0.1278"  # noqa E501
                    },
                    # Pass this kwarg
                    weather_api_key=args.weather_api_key,
                )
            )
        else:
            logger.error("Weather API key is invalid; not adding weather command")
    # Check if the database args are set and add the command(s) that require the database
    # postgres_db, postgres_user, postgres_password, postgres_host, and postgres_port are set
    if args.postgres_db and args.postgres_user and args.postgres_password and args.postgres_host and args.postgres_port:
        logger.info("Database args are set; adding commands that require the database")
        pg_db = PostgresqlDatabase(
            args.postgres_db,
            user=args.postgres_user,
            password=args.postgres_password,
            host=args.postgres_host,
            port=args.postgres_port,
        )
        commands.peewee_proxy.initialize(pg_db)
        Command.add_command(
            Command(hashtag="remindme", function=commands.RemindMe.remind_me_in, help_arguments=commands.RemindMe.help_arguments)
        )

    # Setup checks
    CheckThis.add_check(CheckThis(function=commands.remind, interval=5))

    # Setup commands
    # Test command that returns "test"
    # Command.add_command(Command(hashtag="test", function=lambda status: "test", help_arguments={}))

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
        mastodon_access_token=args.mastodon_access_token,
        mastodon_api_base_url=args.mastodon_api_base_url,
        delete_when_done=args.delete_posts_after_run,
        always_mention=args.always_mention
    )
    stream_listener.stream()



def check_if_weather_api_key_is_valid(key: str):

    """If an API key works, set the class API key."""
    # Test API key to make sure it works
    params = {"key": key, "aqi": "no", "q": "London"}
    url = "https://api.weatherapi.com/v1/current.json"
    response = httpx.get(url=url, params=params)
    if response.status_code == 200:
        return True
    elif response.status_code == 403:
        return False
    else:
        response.raise_for_status()


main()
