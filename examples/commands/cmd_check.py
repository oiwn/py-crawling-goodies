"""Commands module"""
import click


@click.group()
def cmd():
    """Checks"""


@cmd.command()
@click.pass_context
def checkhealth(ctx):
    """Check health"""
    print(ctx)
