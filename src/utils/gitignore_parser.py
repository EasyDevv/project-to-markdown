import fnmatch
import logging
from pathlib import Path
from typing import List

import aiofiles


class GitIgnoreParser:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.ignore_patterns = []
        logging.basicConfig(level=logging.DEBUG)

    async def initialize(self):
        self.ignore_patterns = await self._parse_gitignore()

    async def _parse_gitignore(self) -> List[str]:
        gitignore_path = self.base_dir / ".gitignore"
        if not gitignore_path.exists():
            logging.warning(f"No .gitignore file found in {self.base_dir}")
            return []

        try:
            async with aiofiles.open(gitignore_path, "r") as f:
                content = await f.read()
                patterns = [
                    line.strip()
                    for line in content.splitlines()
                    if line.strip() and not line.startswith("#")
                ]
            logging.debug(f"Parsed {len(patterns)} patterns from .gitignore")
            return patterns
        except Exception as e:
            logging.error(f"Error reading .gitignore file: {str(e)}")
            return []

    async def is_ignored(self, path: Path) -> bool:
        relative_path = path.relative_to(self.base_dir)
        str_path = str(relative_path).replace("\\", "/")  # Normalize path separators

        for pattern in self.ignore_patterns:
            if self._match_pattern(str_path, pattern):
                logging.debug(f"File {path} matched pattern {pattern}")
                return True

        logging.debug(f"File {path} is not ignored")
        return False

    def _match_pattern(self, path: str, pattern: str) -> bool:
        if pattern.startswith("*"):
            return fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(
                path.split("/")[-1], pattern
            )
        elif pattern.startswith("/"):
            return fnmatch.fnmatch(path, pattern[1:]) or fnmatch.fnmatch(
                path, "*/" + pattern[1:]
            )
        elif pattern.endswith("/"):
            return fnmatch.fnmatch(path + "/", pattern) or fnmatch.fnmatch(
                path, pattern + "*"
            )
        else:
            return fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(
                path, "*/" + pattern
            )
