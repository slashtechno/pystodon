# Pystodon  
<!-- Someone on the Python Discord (with the username briskettaco at the time) pitched the name since I was looking to move away from the name "rathercurious-mastodon" for this project. -->
A hybrid between a framework for building Mastodon bots and a standalone bot. You can see this bot in action on [Mastodon](https://botsin.space/@rathercurious) (not always running).

## Usage  
### Prerequisites  
- A Mastodon account  
    - Preferably a bot account, but a normal account will work as well  
- A Mastodon application  
    1. Log into your Mastodon account on the respective instance's web interface  
    2. Navigate to Preferences > Development > Your applications  
    3. Click "New application"  
    4. Set an application name (e.g. "Rather Curious Bot")  
    5. For basic usage, allow the application to read and write to your account  
        - You can also try specifying more granular permissions but this is not tested (yet)  
    6. Click "Submit"  
    7. Make sure you are in the respective application's details page  
    8. Copy "Your access token"  
        - This is your bot's access token  
        - You will need this later  
        - Do not share this token as it allows access to your account  

### Basic Configuration  
- Configuration is handled through environment variables, a `.env` file, or command-line arguments (`--help` for more information)  
- To see an example configuration, see `.env.example`  
- This can be copied to `.env` and edited to suit your needs  


### Poetry  
#### Specific Prerequisites  
- Python (3.11+)
    - [pyenv](https://github.com/pyenv/pyenv) assists with installing and managing multiple versions of Python and may be helpful if you have an incompatible version of Python installed  
        - If on Windows, [pyenv-win](https://github.com/pyenv-win/pyenv-win) is recommended
- Poetry  
    - [Poetry](https://python-poetry.org/docs/#installation) is a package manager for Python that manages dependencies and virtual environments  
#### Installation
1. Clone the repository  
    - `git clone https://github.com/slashtechno/pystodon`  
2. Change directory into the repository  
    - `cd pystodon`  
3. Install dependencies  
    - `poetry install`  
#### Running  
1. Confirm the bot has been configured correctly  
2. `poetry run python -m pystodon`  

### Docker  
Recommended, especially if you want to use commands that depend on a database (e.g. `#remindme`)  
#### Specific Prerequisites
- Docker  
    - [Docker](https://docs.docker.com/get-docker/) is a platform for developing, shipping, and running applications in containers  
- Docker Compose  
    - [Docker Compose](https://docs.docker.com/compose/install/) is a tool for defining and running multi-container Docker applications  
#### Running  
1. Clone the repository  
    - `git clone https://github.com/slashtechno/pystodon`
2. Change directory into the repository
    - `cd pystodon`
3. Confirm the bot has been configured correctly  
4. `docker-compose up -d`  
    - The `-d` flag runs the containers in the background  
#### Specific Prerequisites
- Python (3.11+)
    - See the Poetry section for more information  

### PyPi
Not recommended as you can't modify the commands  
#### Requirements
- Python (3.11+)
    - Read the Poetry section for more information
#### Installation
1. `pip install pystodon`
    - You may need to use `pip3` instead of `pip` depending on your system
    - In addition, you may want to try `python -m pip install pystodon` or `python3 -m pip install pystodon` if the above commands do not work  
#### Running  
- Assuming programs installed by `pip` are in your PATH, you can run the bot with `pystodon`  


### Usage  
- By default, the bot will use the commands configured in `pystodon/commands.py`
    - Commands include `#remindme`, `#timezone`, `#weather`, and `/test`
    - The command `help` (note the lack of a prefix) will list all available commands and can be used to get more information on a specific command  
    - These commands can be modified, removed, or added to suit your needs
        - Look in `pystodon/__main__.py` to see how commands are added  
        - When running with Docker, run `docker compose --build` to rebuild the image with the new commands
- The syntax for commands is `@bot_username@example.com command [arguments]`
    - For example, `@rathercurious #remindme in 1h30m` 
    - The bot will match the visibility of the command to the visibility of the message it is replying to
        - If the message is public, the bot will reply with a public message  
        - If the message is unlisted, the bot will reply with an unlisted message  
        - If the message is direct, the bot will reply with a direct message  
        - It's recommended to set `RC_ALWAYS_MENTION` to `True` in the `.env` (or use `--always-mention`) to ensure the user is mentioned in the reply  
