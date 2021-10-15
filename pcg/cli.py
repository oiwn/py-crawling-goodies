"""Command-line-interface related helper to organize subcommands into
separated files"""
# pylint: disable=no-self-use
import os
import pathlib

import click


class CommandLineInterface(click.MultiCommand):
    """Backend command line interface util.
    This class used to 'inject' modules into `get_commands_folder()` folder as a
    plugins implementing set of sub-commands for each cli top-level command.
    """

    _default_command_prefix = "cmd_"
    _root_folder = pathlib.Path().resolve()

    def get_root_folder(self, ctx):
        """Return current app root, redefine to change"""
        root_folder = ctx.meta.get("project_root_folder", self._root_folder)
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
        print(self.get_root_folder(ctx))
        commands = []
        cmd_prefix = self.get_command_prefix()
        for filename in os.listdir(self.get_commands_folder(ctx)):
            if filename.endswith(".py") and filename.startswith(cmd_prefix):
                commands.append(filename[len(cmd_prefix) : -len(".py")])
        commands.sort()
        return commands

    def get_command(self, ctx, cmd_name):
        """Import module with command implementation

        NOTE: Try to avoid to import modules on top of the file,
        it greatly increase time required to load module command.

        I.e. move required imports inside the function with
        command implementation.
        """
        namespace = {}
        command_file_path = os.path.join(
            self.get_commands_folder(ctx),
            self.get_command_prefix() + cmd_name + ".py",
        )
        with open(command_file_path) as command_file:
            code = compile(command_file.read(), command_file_path, "exec")
            eval(code, namespace, namespace)  # pylint: disable=eval-used
        return namespace["cmd"]


def plugins_cli_factory(root_folder):
    """Create CLI class with root folder setted"""
    return type(
        "PluginCommandsCLI",
        (CommandLineInterface,),
        {"_root_folder": root_folder},
    )
