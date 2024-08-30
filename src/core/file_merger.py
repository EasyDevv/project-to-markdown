import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import aiofiles

from src.config import Config
from src.utils import GitIgnoreParser

from .doc_generator import (
    generate_content,
    generate_tree_structure,
    generate_onefile_content,
)
from .file_processor import FileProcessor


class MergeException(Exception):
    """Represents an exception that occurs during file merging."""


class FileMerger:
    """A class for merging project files."""

    def __init__(
        self,
        project_path: Path,
        merge_onefile: bool,
        enable_timestamp: bool,
        enable_folder_structure: bool,
        logger: logging.Logger,
    ):
        """Initialize the FileMerger class."""
        config = Config(logger=logger)

        self.project_path = project_path.resolve()
        self.exclude_types = set(config.exclude_types)
        self.onefile = merge_onefile
        self.enable_timestamp = enable_timestamp
        self.enable_folder_structure = enable_folder_structure
        self.logger = logger

        self.gitignore_parser = GitIgnoreParser(self.project_path)
        self.file_processor = FileProcessor()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.excluded_folders = set(config.exclude_folders)

        self.filtered_files: List[Path] = []

        self.output_dir = self.project_path / config.output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def initialize(self):
        """Initialize FileMerger. Initializes GitIgnoreParser."""
        await self.gitignore_parser.initialize()

    def _generate_onefile_filename(self) -> Path:
        """Generate the name for the single file."""
        output_filename = f"{self.project_path.name}_codes.md"
        return self.output_dir / output_filename

    def _generate_tree_structure_filename(self) -> Path:
        """Generate the name for the tree structure file."""
        output_filename = f"{self.project_path.name}_structure.md"
        return self.output_dir / output_filename

    def _generate_output_path(self, folder_path: Optional[Path] = None) -> Path:
        """Generate the path for the output file."""
        project_name = self.project_path.name

        folder_part = "root" if folder_path == Path(".") else str(folder_path)
        folder_part = folder_part.replace("/", "-").replace("\\", "-")
        output_filename = f"{project_name}_{folder_part}"

        if self.enable_timestamp:
            output_filename += f"-{self.timestamp}"

        output_filename += ".md"

        return self.output_dir / output_filename

    async def _filter_files(self):
        """Filter files within the project, excluding specified folders."""
        self.filtered_files = [
            file_path
            for file_path in self.project_path.rglob("*")
            if await self._should_process_file(file_path)
        ]
        self.logger.info(f"Filtered files count: {len(self.filtered_files)}")

    async def _should_process_file(self, file_path: Path) -> bool:
        """Check if the given file should be processed."""
        return (
            file_path.is_file()
            and file_path.suffix[1:] not in self.exclude_types
            and not await self.gitignore_parser.is_ignored(file_path)
            and not self._is_excluded_folder(file_path)
        )

    def _is_excluded_folder(self, path: Path) -> bool:
        """Check if the given path is in an excluded folder."""
        return any(excluded in path.parts for excluded in self.excluded_folders)

    async def _process_files(self) -> List[Tuple[Path, str, str]]:
        """Process all filtered files."""
        tasks = [
            self._process_file_wrapper(file_path) for file_path in self.filtered_files
        ]
        processed_files = [result for result in await asyncio.gather(*tasks) if result]
        self.logger.info(f"Processed: {len(processed_files)} files")
        return processed_files

    async def _process_file_wrapper(
        self, file_path: Path
    ) -> Optional[Tuple[Path, str, str]]:
        """A wrapper function for processing individual files."""
        try:
            result = await self.file_processor.process_file(
                file_path, self.project_path
            )
            self.logger.debug(
                f"Processed: {file_path}, content length: {len(result[2]) if result else 0}"
            )
            return result
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {str(e)}")
            return None

    async def _categorize_files(
        self, processed_files: List[Tuple[Path, str, str]]
    ) -> Dict[Path, List[Tuple[Path, str, str]]]:
        """Categorize processed files by folder asynchronously."""
        categorized = {}

        async def categorize_file(file_path: Path, extension: str, content: str):
            folder = file_path.parent
            if folder not in categorized:
                categorized[folder] = []
            categorized[folder].append((file_path, extension, content))

        await asyncio.gather(
            *(
                categorize_file(file_path, extension, content)
                for file_path, extension, content in processed_files
            )
        )

        return categorized

    async def _write_multiple_files(
        self, categorized_files: Dict[Path, List[Tuple[Path, str, str]]]
    ) -> List[Path]:
        """Write content to multiple files based on folder structure."""
        output_files = []
        for folder_path, files in categorized_files.items():
            try:
                output_file = self._generate_output_path(folder_path)

                content = await generate_content(folder_path, files)
                async with aiofiles.open(
                    output_file, "w", encoding="utf-8"
                ) as out_file:
                    await out_file.write(content)
                output_files.append(output_file)
                self.logger.info(f"Created file: {output_file}")
            except Exception as e:
                self.logger.error(f"Error processing folder {folder_path}: {str(e)}")
        return output_files

    async def _write_onefile(self, processed_files) -> Path:
        """Write the content to a single file."""
        output_file = self._generate_onefile_filename()

        folder_path = Path(".")
        content = await generate_onefile_content(folder_path, processed_files)
        # content = await generate_onefile_content(processed_files)

        async with aiofiles.open(output_file, "w", encoding="utf-8") as out_file:
            await out_file.write(content)
        self.logger.info(f"Created single file: {output_file}")
        return output_file

    async def _generate_tree_structure(self) -> Optional[Path]:
        """Generate and write the tree structure file if enabled."""
        if not self.enable_folder_structure:
            return None

        try:
            tree_structure = await generate_tree_structure(
                files=self.filtered_files, project_path=self.project_path
            )
            tree_output_file = self._generate_tree_structure_filename()
            async with aiofiles.open(
                tree_output_file, "w", encoding="utf-8"
            ) as tree_file:
                await tree_file.write(tree_structure)
            self.logger.info(f"Created structure file: {tree_output_file}")
            return tree_output_file
        except Exception as e:
            self.logger.error(f"Error generating structure: {str(e)}")
            return None

    async def merge_files(self) -> List[Path]:
        """
        Main function for merging files.

        :param progress_callback: Callback function to report progress
        :return: Paths of generated output files
        """
        try:
            await self.initialize()
            await self._filter_files()
            processed_files = await self._process_files()

            output_files = []

            if self.onefile:
                output_file = await self._write_onefile(processed_files)
                output_files.append(output_file)
            else:
                categorized_files = await self._categorize_files(processed_files)
                output_files.extend(await self._write_multiple_files(categorized_files))

            tree_structure_file = await self._generate_tree_structure()
            if tree_structure_file:
                output_files.append(tree_structure_file)

            return output_files

        except Exception as e:
            self.logger.error(f"Unexpected error during file merging: {str(e)}")
            raise MergeException(str(e))
