import typer

from .ui import start

app = typer.Typer()
app.command()(start)

if __name__ == '__main__':
    app()
