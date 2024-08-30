import logging
from pathlib import Path
from typing import Optional, Tuple

import aiofiles


class FileProcessor:
    @staticmethod
    def get_file_extension(filename: Path) -> str:
        return filename.suffix[1:]

    @staticmethod
    async def read_file_content(file_path: Path) -> Optional[str]:
        try:
            async with aiofiles.open(file_path, "r") as f:
                return await f.read()
        except UnicodeDecodeError:
            logging.warning(f"Unable to read {file_path} as UTF-8. Skipping.")
        except PermissionError:
            logging.error(f"Permission denied: Unable to read {file_path}")
        except Exception as e:
            logging.error(f"Unexpected error reading {file_path}: {str(e)}")
        return None

    async def process_file(
        self, file_path: Path, project_path: Path
    ) -> Tuple[Path, str, Optional[str]]:
        relative_path = file_path.relative_to(project_path)
        extension = self.get_file_extension(file_path)
        content = await self.read_file_content(file_path)
        return relative_path, extension, content
