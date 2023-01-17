"""ChapterUp

Usage:
    chapterup <dir_path> <album_name> [--access-token=<token>] [--public]
    chapterup [--help | --version | --show-config-path]

Parameters:
    <dir_path>                  The path to the directory containing the test_images.
    <album_name>                The name of the album to create.

Options:
    -a --access-token=<token>   The access token to use for Imgur.
    -p --public                 Make the album public. They're private by default.
    -c --show-config-path            Show the path to the configuration file.
    -h --help                   Show this screen.
    -v --version                Show version.
"""


import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

from docopt import magic_docopt
from imgur_python import Imgur
from natsort import natsorted
from tqdm import tqdm
from xdg import XDG_CONFIG_HOME

from chapterup import __version__


def get_config_path() -> Path:
    """
    Get the path to the configuration file for Linux.
    """
    return Path(XDG_CONFIG_HOME, "chapterup" + "rc")


@dataclass
class Config:
    imgur_access_token: str = ""

    @classmethod
    def from_json_file(cls, path: Path):
        with path.open() as f:
            data = json.load(f)
        return cls(**data)

    def to_json_file(self, path: Path):
        with path.open("w") as f:
            json.dump(asdict(self), f)


def load_config() -> Config:
    """
    Load the configuration file.
    """
    config_path = get_config_path()
    if config_path.exists():
        try:
            return Config.from_json_file(config_path)
        except (json.JSONDecodeError, OSError) as e:
            print("Error: Could not read configuration file.")
            print(e)
            sys.exit(1)
    else:
        return Config()


def get_confirmation(prompt: str, default: bool | None = None) -> bool:
    """
    Get confirmation from the user.
    Repeat if the input wasn't valid.

    :param prompt: The prompt to display to the user.
    :param default: The default value to return if the user doesn't input anything.
    :return: The user's confirmation.
    """
    match default:
        case None:
            prompt += " [y/n]"
        case True:
            prompt += " [Y/n]"
        case False:
            prompt += " [y/N]"

    prompt += " > "

    while True:
        user_input = input(prompt)
        if user_input.lower().strip().startswith("y"):
            return True
        elif user_input.lower().strip().startswith("n"):
            return False
        elif user_input == "" and default is not None:
            return default
        else:
            print("Invalid input. Please try again.")


def get_image_paths(dir_path: Path) -> list[Path]:
    """
    Get all the image paths from the given directory.
    Sort them in a natural order.
    """
    paths = natsorted(dir_path.iterdir())
    return [path for path in paths if path.suffix.lower() in [".jpg", ".jpeg", ".png", ".gif"]]


def imgur_upload(image_paths: list[Path], config: Config, album_name: str, public: bool):

    imgur_client = Imgur({"access_token": config.imgur_access_token})

    image_ids = []
    for image_path in tqdm(image_paths):
        if image_path.is_file():
            image = imgur_client.image_upload(
                str(image_path.absolute()), image_path.stem, image_path.stem
            )
            image_id = image["response"]["data"]["id"]
            image_ids.append(image_id)

    album = imgur_client.album_create(
        image_ids, title=album_name, description="", privacy="hidden" if not public else "public"
    )
    album_id = album["response"]["data"]["id"]
    print("-" * 50)
    print(f"Album created with id: {album_id}")
    print(f"Access the album here: https://imgur.com/a/{album_id}")


def main():
    args = magic_docopt(docstring=__doc__, version=f"ChapterUp {__version__}")

    if args.show_config_path:
        print(get_config_path())
        return

    config = load_config()
    if args.access_token:
        config.imgur_access_token = args.access_token
        config.to_json_file(get_config_path())

    dir_path = Path(args.dir_path)
    if not dir_path.is_dir():
        print("Error: The given path is not a directory.")
        sys.exit(1)

    image_paths = get_image_paths(dir_path)
    if not image_paths:
        print("Error: The given directory does not contain any test_images.")
        sys.exit(1)

    # Show the paths and ask for confirmation before uploading.
    print("The following test_images will be uploaded in order:")
    for path in image_paths:
        print(path.name)
    print(f"\nFound {len(image_paths)} test_images.")
    if not get_confirmation("Do you want to continue?", default=False):
        print("Aborting.")
        sys.exit(0)

    imgur_upload(image_paths, config, args.album_name, args.public)


if __name__ == "__main__":
    main()
