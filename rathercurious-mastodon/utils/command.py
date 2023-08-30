import re
from . import utils



class Command:
    '''
    Functions and stuff related to adding and commands to Mastodon.py so that a reply will be made to "@<bot> #<command> <arguments>".
    '''
    def __init__(self, hashtag, function: callable, help_arguments: dict = {}, *args, **kwargs): # noqa E501
        self.hashtag = hashtag
        self.function = function
        self.function_args = args
        self.function_kwargs = kwargs
        self.help_arguments = help_arguments
    
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
    def function_args(self):
        '''Get the function arguments'''
        return self._function_args
    @function_args.setter
    def function_args(self, function_args):
        '''Set the function arguments'''
        self._function_args = function_args
    @property
    def function_kwargs(self):
        '''Get the function keyword arguments'''
        return self._function_kwargs
    @function_kwargs.setter
    def function_kwargs(self, function_kwargs):
        '''Set the function keyword arguments'''
        self._function_kwargs = function_kwargs



    @property
    def help_arguments(self):
        '''Get the arguments'''
        return self._help_arguments
    @help_arguments.setter
    def help_arguments(self, help_arguments):
        '''
        Set arguments and their help text.
        This is used for the help command

        Please note, these arguments are not passed to the function, for that, use *args and **kwargs # noqa E501
        '''
        if isinstance(help_arguments, dict):
            self._help_arguments = help_arguments
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
        Parse the status dict and call the appropriate command
        It passes the status dict, as well as any args and kwargs.
        Please note that the status dict is passed as the first argument.
        If no command matches, return None. 
        '''
        # TODO: Also pass args

    
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
                for argument, help_text in command.help_arguments.items():
                    content += f'#{command.hashtag} {argument}: {help_text}\n'
            return content
        else:
            for command in commands:
                if hashtag == command.hashtag:
                    # "*" unpacks the list of arguments, while "**" unpacks the dictionary of keyword arguments # noqa E501
                    return command.function(status, *command.function_args, **command.function_kwargs)
            # Return None if no command matches
            return None
