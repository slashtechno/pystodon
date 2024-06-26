import httpx
from . import commands
from peewee import PostgresqlDatabase


from pystodon.lib.command import Command, CheckThis
from pystodon.lib import utils
from pystodon.utils.logging import logger
from pystodon.utils.cli_args import args

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
                    command="#weather",
                    function=commands.weather,
                    help_text="Get the weather for a location. Pass the latitude and longitude as arguments. For example, `@bot@example.com #weather 40.730610, -73.935242`",
                    # Pass this kwarg
                    weather_api_key=args.weather_api_key,
                )
            )
        else:
            logger.error("Weather API key is invalid; not adding weather command")
    # Check if the database args are set and add the command(s) that require the database
    # postgres_db, postgres_user, postgres_password, postgres_host, and postgres_port are set
    if (
        args.postgres_db
        and args.postgres_user
        and args.postgres_password
        and args.postgres_host
        and args.postgres_port
    ):
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
            Command(
                command="#remindme",
                function=commands.RemindMe.remind_me_in,
                help_text=commands.RemindMe.help_text,
            )
        )

    # Setup checks
    CheckThis.add_check(CheckThis(function=commands.remind, interval=5))

    # Setup commands
    # Test command that returns "test"
    Command.add_command(
        Command(
            command="/test", function=lambda status: "test", help_text="Test command"
        )
    )

    # Timezone command
    Command.add_command(
        Command(
            command="#timezone",
            function=commands.timezone,
            help_text="Get the time in a timezone. Pass the timezone (https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) as an argument. For example, `@bot@example.com #timezone America/New_York`",
        )
    )

    stream_listener = utils.stream_listener(
        mastodon_access_token=args.mastodon_access_token,
        mastodon_api_base_url=args.mastodon_api_base_url,
        delete_when_done=args.delete_posts_after_run,
        always_mention=args.always_mention,
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

if __name__ == "__main__":
    main()
