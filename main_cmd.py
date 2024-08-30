import argparse
import asyncio
import logging
from pathlib import Path

from src.core import FileMerger
from src.utils import get_logger, setup_logging

setup_logging(console_level=logging.INFO)
logger = get_logger(__name__)


def get_project_path():
    while True:
        path = input("Enter the project folder path: ").strip()
        if path:
            return Path(path)
        print("Please enter a valid path.")


def main():
    parser = argparse.ArgumentParser(
        description="Merge project files into a single markdown file."
    )
    parser.add_argument(
        "project_path",
        type=Path,
        help="Path to the project folder",
    )
    parser.add_argument(
        "--onefile",
        action="store_true",
        help="Integrate all subdirectories into a single document.",
    )
    parser.add_argument(
        "--timestamp",
        action="store_true",
        help="Add a timestamp to the project file name.",
    )
    parser.add_argument(
        "--no-tree",
        action="store_false",
        help="Generate a project tree structure file.",
    )

    args = parser.parse_args()

    path = args.project_path or get_project_path()

    merger = FileMerger(
        project_path=path,
        merge_onefile=args.onefile,
        enable_timestamp=args.timestamp,
        enable_folder_structure=args.no_tree,
        logger=logger,
    )
    asyncio.run(merger.merge_files())


if __name__ == "__main__":
    main()
