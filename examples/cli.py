"""App entry"""
# pylint: disable=import-error,wrong-import-position
import sys
import pathlib

import click

sys.path.append(str(pathlib.Path("..").resolve()))
from pcg.cli import plugins_cli_factory


@click.command(cls=plugins_cli_factory(pathlib.Path().resolve()))
@click.option("--conf", default="dev", help="config")
@click.pass_context
def cli(ctx, conf):
    click.echo("hello")
    click.echo(conf)


if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter
