# rathercurious-mastodon  
A hybrid between a framework for building Mastodon bots and a standalone bot  

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
- Configuration is handled through environment variables and optionally a `.env` file  
- To see an example configuration, see `.env.example`  
- This can be copied to `.env` and edited to suit your needs  
### Poetry  
#### Specific Prerequisites  
- Python 3.11 (other versions may work, but are not tested)  
    - [pyenv](https://github.com/pyenv/pyenv) assists with installing and managing multiple versions of Python and may be helpful if you have a different version of Python installed  
        - If on Windows, [pyenv-win](https://github.com/pyenv-win/pyenv-win) is recommended
- Poetry  
    - [Poetry](https://python-poetry.org/docs/#installation) is a package manager for Python that manages dependencies and virtual environments  
#### Installation
1. Clone the repository  
    - `git clone https://github.com/slashtechno/rathercurious-mastodon`  
2. Change directory into the repository  
    - `cd rathercurious-mastodon`  
3. Install dependencies  
    - `poetry install`  
#### Running  
1. Confirm the bot has been configured correctly  
2. `poetry run python -m rathercurious_mastodon`  