import logging
from pathlib import Path
from typing import Callable

from src.core.file_merger import FileMerger
from src.utils.logging_config import get_logger, setup_logging


class Backend:
    def __init__(self, log_callback: Callable[[str], None]):
        self.project_path = None
        self.merge_onefile = False
        self.enable_timestamp = False
        self.enable_folder_structure = True
        self.log_callback = log_callback
        self.setup_logger()

    def setup_logger(self):
        setup_logging(console_level=logging.INFO)
        self.logger = get_logger(__name__)
        self.logger.addHandler(CallbackHandler(self.log_callback))

    def set_project_path(self, path: Path):
        self.project_path = path
        self.logger.info(f"Selected directory: {self.project_path}")

    def set_merge_onefile(self, value: bool):
        self.merge_onefile = value
        self.logger.info(f"Merge into one file set to: {value}")

    def set_enable_timestamp(self, value: bool):
        self.enable_timestamp = value
        self.logger.info(f"Enable timestamp set to: {value}")

    def set_enable_folder_structure(self, value: bool):
        self.enable_folder_structure = value
        self.logger.info(f"Generate folder structure set to: {value}")

    async def merge_files(self):
        if not self.project_path:
            raise ValueError("Project path not set")

        self.logger.info("Starting file merge process")
        merger = FileMerger(
            project_path=self.project_path,
            merge_onefile=self.merge_onefile,
            enable_timestamp=self.enable_timestamp,
            enable_folder_structure=self.enable_folder_structure,
            logger=self.logger,
        )

        try:
            output_files = await merger.merge_files()
            self.logger.info(
                f"Merged project files into {len(output_files)} markdown file(s)."
            )
            return output_files
        except Exception as ex:
            self.logger.error(f"Error during file merge: {str(ex)}")
            raise


class CallbackHandler(logging.Handler):
    def __init__(self, callback: Callable[[str], None]):
        super().__init__()
        self.callback = callback

    def emit(self, record):
        log_entry = self.format(record)
        self.callback(log_entry)
