import re
from . import utils

class Command:
    '''
    Functions and stuff related to adding and commands to Mastodon.py so that a reply will be made to "@<bot> #<command> <arguments>".
    '''
    def __init__(self, hashtag, function: callable, arguments: dict = {}):
        self.hashtag = hashtag
        self.function = function
        self.arguments = arguments
    
    # Setters/Getters
    @property
    def hashtag(self):
        '''Get the hashtag'''
        return self._hashtag
    @hashtag.setter
    def hashtag(self, hashtag):
        '''Set the hashtag if it is just word characters. Does not include the #'''
        if re.search(r'^\w+$', hashtag):
            self._hashtag = hashtag
        else:
            raise ValueError('Hashtag must match regex: ^\w+$')

    @property
    def function(self):
        '''Get the function'''
        return self._function
    @function.setter
    def function(self, function):
        '''
        Set the function if it is callable.
        This function will be passed one argument, the complete status object   
        This function should return a string to be posted as a reply
        '''
        if callable(function):
            self._function = function
        else:
            raise TypeError('Function must be callable')
    
    @property
    def arguments(self):
        '''Get the arguments'''
        return self._arguments
    @arguments.setter
    def arguments(self, arguments):
        '''
        Set arguments and their help text.
        # This is used for the help command as well.
        '''
        if isinstance(arguments, dict):
            self._arguments = arguments
        else:
            raise TypeError('Arguments must be a dictionary')
    
    # Methods and stuff
    def __str__(self):
        return self.hashtag 


    # class variables
    commands = []

    # classmethods

    @classmethod
    def add_command(cls, command: 'Command'):
        '''
        Add a command to the list of commands.
        '''
        if isinstance(command, Command) and command not in cls.commands:
            cls.commands.append(command)
        else:
            raise TypeError('Argument must be a Command')

    @classmethod
    def delete_command(cls, command: 'Command'):
        '''
        Delete a command from the list of commands.
        '''
        if isinstance(command, Command):
            cls.commands.remove(command)
        else:
            raise TypeError('Argument must be a Command')
    
    @staticmethod
    def parse_status(status, commands: list = commands):
        '''
        Parse the status dict and call the appropriate command, passing the status dict
        If no command matches, return None. 
        '''

    
        if commands == []:
            return None 
        
        # Get the hashtag
        if matches := re.search(r'#(\w+)', utils.parse_html(status['content'])):
            hashtag = matches.group(1)
        else:
            return None
        
    #    Run the command
        if hashtag == 'help':
            content = 'Commands:\n'
            for command in commands:
                content += f'\n#{command.hashtag}\n'
                for argument, help_text in command.arguments.items():
                    content += f'#{command.hashtag} {argument}: {help_text}\n'
            return content
        else:
            for command in commands:
                if hashtag == command.hashtag:
                    return command.function(status)
            # Return None if no command matches
            return None
