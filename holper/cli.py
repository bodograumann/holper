import typer

from holper import core


def main(file: str):
    session = core.open_session("sqlite:///" + file)


if __name__ == "__main__":
    typer.run(main)
