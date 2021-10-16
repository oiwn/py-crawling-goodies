"""Test command line interface helpers"""
import click
from click.testing import CliRunner
from pcg.cli import CommandLineInterface


COMMAND_FILE = """
import click


@click.group()
def cmd():
    '''Test file'''


@cmd.command()
@click.pass_context
def say_hello(ctx):
    return "Hello"
"""


def test_cli(tmp_path):
    """Test command line interface subcommands helper"""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=str(tmp_path)):
        command_dir = tmp_path / "commands"
        command_dir.mkdir()
        cmd_file = command_dir / "cmd_test.py"
        cmd_file.write_text(COMMAND_FILE)
        init_file = command_dir / "__init__.py"
        init_file.write_text("")

        class TestCommandLineInterface(CommandLineInterface):
            """Test cli"""

            def get_commands_folder(self, ctx):
                return str(command_dir)

        @click.command(cls=TestCommandLineInterface)
        @click.option("--conf", default="dev", help="config")
        def cli(conf):
            """Command line interface entry point"""
            assert conf == "dev"

        result = runner.invoke(cli)

    assert "Test file" in result.output
    assert result.exit_code == 0
