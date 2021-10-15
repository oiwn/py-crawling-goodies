"""Command-line-interface related helper to organize subcommands into
separated files"""
# pylint: disable=no-self-use
import os
import pathlib
import importlib

import click


class CommandLineInterface(click.MultiCommand):
    """Backend command line interface util.
    This class used to 'inject' modules into `get_commands_folder()` folder as a
    plugins implementing set of sub-commands for each cli top-level command.
    """

    _default_command_prefix = "cmd_"

    def get_root_folder(self, ctx):
        """Return current app root, redefine to change"""
        root_folder = ctx.meta.get(
            "project_root_folder", pathlib.Path().resolve()
        )
        return root_folder

    def get_commands_folder(self, ctx):
        """Return commands folder, redefine this in subclass to change
        default: "/commands"."""
        return os.path.join(self.get_root_folder(ctx), "commands")

    def get_command_prefix(self):
        """By default each file should be named with prefix `cmd_`
        redefine this to change
        """
        return self._default_command_prefix

    def list_commands(self, ctx):
        """Iterate throuth the commands folder and collect all files
        with `cmd_` prefix and `.py` extension
        """
        commands = []
        cmd_prefix = self.get_command_prefix()
        for filename in os.listdir(self.get_commands_folder(ctx)):
            if filename.endswith(".py") and filename.startswith(cmd_prefix):
                commands.append(filename[len(cmd_prefix) : -len(".py")])
        commands.sort()
        print(commands)
        return commands

    def get_command(self, ctx, cmd_name):
        """Import module with command implementation

        NOTE: Try to avoid to import modules on top of the file,
        it greatly increase time required to load module command.

        I.e. move required imports inside the function with
        command implementation.
        """
        print(self.get_commands_folder(ctx))
        namespace = {}
        command_file_name = os.path.join(
            self.get_commands_folder(ctx), cmd_name + ".py"
        )
        with open(command_file_name) as command_file:
            code = compile(command_file.read(), command_file, "exec")
            eval(code, namespace, namespace)  # pylint: disable=eval-used
        return namespace["cli"]
        #  mod = importlib.import_module(f"{self.get_commands_folder}.cmd_{name}")
        #  mod = __import__(
        #      f"{self.get_commands_folder()}.cmd_{name}", None, None, ["cmd"]
        #  )
        #  return mod.cmd
