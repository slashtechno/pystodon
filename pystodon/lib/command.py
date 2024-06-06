# https://adamj.eu/tech/2021/05/15/python-type-hints-future-annotations/
from __future__ import annotations
import re
from datetime import datetime
from pystodon.lib import utils


class CheckThis:
    """
    Every x seconds run function y.
    """

    checks = []

    def __init__(self, function: callable, interval: int, *args, **kwargs):
        self.function = function
        self.interval = interval
        self.function_args = args
        self.function_kwargs = kwargs
        self.last_ran = None

    def add_check(self):
        """
        Add a check to the list of checks.
        """
        CheckThis.checks.append(self)

    @classmethod
    def run_checks(cls):
        """
        Run all the checks.
        """
        for check in cls.checks:
            if (
                check.last_ran is None
                or (datetime.now() - check.last_ran).seconds >= check.interval
            ):
                check.function(*check.function_args, **check.function_kwargs)
                check.last_ran = datetime.now()

    # Setters/Getters

    @property
    def interval(self):
        """Get the interval"""
        return self._interval

    @interval.setter
    def interval(self, interval):
        """Set the interval if it is a positive integer"""
        if not ((interval > 0) and isinstance(interval, int)):
            raise ValueError("Interval must be a positive integer")
        self._interval = interval

    @property
    def function(self):
        """Get the function"""
        return self._function

    @function.setter
    def function(self, function):
        """
        Set the function if it is callable.
        This function will be passed one argument, the complete status object
        This function should return a string to be posted as a reply
        """
        if callable(function):
            self._function = function
        else:
            raise TypeError("Function must be callable")

    @property
    def function_kwargs(self):
        """Get the function keyword arguments"""
        return self._function_kwargs

    @function_kwargs.setter
    def function_kwargs(self, function_kwargs):
        """Set the function keyword arguments"""
        self._function_kwargs = function_kwargs

    @property
    def function_args(self):
        """Get the function arguments"""
        return self._function_args

    @function_args.setter
    def function_args(self, function_args):
        """Set the function arguments"""
        self._function_args = function_args

    @property
    def commands(self):
        """Get the commands (read-only)"""
        return self._commands


class Command:
    """
    Functions and stuff related to adding and commands to Mastodon.py
    Intended to parse commands such as "@<bot> #<command> <arguments>".
    """

    def __init__(self, command, function: callable, help_text: str, *args, **kwargs):
        self.command = command
        self.function = function
        self.function_args = args
        self.function_kwargs = kwargs
        self.help_text = help_text

    # Setters/Getters
    @property
    def command(self):
        """Get the command"""
        return self._command

    @command.setter
    def command(self, command):
        """Set the command if it is a single sequence of non-whitespace characters, such as \"/command\". Otherwise, raise a ValueError."""
        if re.search(r"^(?:\S)+$", command):
            self._command = command
        else:
            raise ValueError("Command must match regex: ^(?:\\S)+$")

    @property
    def function(self):
        """Get the function"""
        return self._function

    @function.setter
    def function(self, function):
        """
        Set the function if it is callable.
        This function will be passed one argument, the complete status object
        This function should return a string to be posted as a reply
        """
        if callable(function):
            self._function = function
        else:
            raise TypeError("Function must be callable")

    @property
    def function_args(self):
        """Get the function arguments"""
        return self._function_args

    @function_args.setter
    def function_args(self, function_args):
        """Set the function arguments"""
        self._function_args = function_args

    @property
    def function_kwargs(self):
        """Get the function keyword arguments"""
        return self._function_kwargs

    @function_kwargs.setter
    def function_kwargs(self, function_kwargs):
        """Set the function keyword arguments"""
        self._function_kwargs = function_kwargs

    @property
    def help_text(self):
        """Get the arguments"""
        return self._help_text

    @help_text.setter
    def help_text(self, help_text: str):
        """
        Set the help text
        """
        self._help_text = help_text

    # Methods and stuff
    def __str__(self):
        return self.command

    # class variables
    _commands = []

    # classmethods

    @classmethod
    def add_command(cls, command: Command):
        """
        Add a command to the list of commands.
        """
        if isinstance(command, Command) and command not in cls._commands:
            cls._commands.append(command)
        else:
            raise TypeError("Argument must be a Command")

    @classmethod
    def delete_command(cls, command: "Command"):
        """
        Delete a command from the list of commands.
        """
        if isinstance(command, Command):
            cls._commands.remove(command)
        else:
            raise TypeError("Argument must be a Command")

    @staticmethod
    def parse_status(status: dict, always_mention: bool, commands: list = None):
        """
        Parse the status dict and call the appropriate command
        It passes the status dict, as well as any args and kwargs.
        Please note that the status dict is passed as the first argument.

        You can provide a custom list of commands, but if you don't, it will use the class variable
        The class variable is updated with Command.add_command() and Command.delete_command()

        If the account sends a DM with the command, the bot will send a DM back.
        But if there isn't a mention, the account won't be able to see it
        Setting always_mention will prepend the content with "@author" and a newline

        If no command matches, return None.
        """

        if commands is None:
            commands = Command._commands

        # Get the command (the first word in the content)
        if matches := re.search(
            r"(?:(?:@\S+@?\S+)\s+)?(\S+)(?:\s?.*)", utils.parse_html(status["content"])
        ):
            command = matches.group(1)
        else:
            return None

        #    Run the command
        if command == "help":
            content = Command.help_command(status, commands)
            if always_mention:
                # The Mastodon client Elk will seemingly not show the mention if it's on the first like
                return f"@{status['account']['acct']}\n{content}"
            else:
                return content
        else:
            for c in commands:
                if command == c.command:
                    # "*" unpacks the list of arguments, while "**" unpacks the dictionary of keyword arguments
                    content = c.function(
                        status, *c.function_args, **c.function_kwargs
                    )
                    if always_mention:
                        # The Mastodon client Elk will seemingly not show the mention if it's on the first like
                        return f"@{status['account']['acct']}\n{content}"
                    else:
                        return content
            # Return None if no command matches
            return None

    @staticmethod
    def help_command(status: dict, commands: list = None) -> str:
        """
        If an argument is provided, return the help text for that command.
        Otherwise, return a list of commands.
        """
        if commands is None:
            commands = Command.commands
        if not utils.return_raw_argument(status=status):
            content = "Commands:\n"
            for c in commands:
                content += f"\n{c.command}\n"
            content += '\n\nUse "help <command>" to get help for a specific command'
            return content
        else:
            for c in commands:
                if utils.return_raw_argument(status=status) == c.command:
                    content = f"Help text for {c.command}:\n{c.help_text}"
                    return content
            return "Command not found"
