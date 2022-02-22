from dotenv import load_dotenv

from cognite.transformations_cli.commands.base import transformations_cli


def main() -> None:
    # support local .env file with environment-variables
    load_dotenv()

    transformations_cli()


if __name__ == "__main__":
    main()
