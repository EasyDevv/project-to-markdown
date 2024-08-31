from pathlib import Path
import json
import logging


class Config:
    """
    A class for managing application settings.
    """

    def __init__(self, logger=logging.Logger, config_file: Path = Path("config.json")):
        """
        Initialize the Config class.

        :param config_file: Path to the configuration file
        """
        self.logger = logger
        self.config_file = config_file
        self.exclude_types = [
            "md",
            "log",
            "pyc",
            "pyo",
            "pyd",
            "dll",
            "so",
            "exe",
            "jpg",
            "jpeg",
            "png",
            "gif",
            "svg",
            "webp",
            "tiff",
            "tif",
            "psd",
        ]
        self.exclude_folders = [
            ".output-md",
            ".vscode",
            ".venv",
            "__pycache__",
            ".gitignore",
            "node_modules",
            ".git",
            "image",
            "images",
        ]

        self.output_dir = ".output-md"
        self.max_workers = 4

        self.load_config()

    def load_config(self):
        """
        Load settings from the configuration file.
        """
        if self.config_file.exists():
            with self.config_file.open("r", encoding="utf-8-sig") as f:
                data = json.load(f)
                self.exclude_types = data.get("exclude_types", self.exclude_types)
                self.exclude_folders = data.get("exclude_folders", self.exclude_folders)
                self.output_dir = data.get("output_folder", self.output_dir)
                self.max_workers = data.get("max_workers", self.max_workers)
            self.logger.info("Configuration loaded successfully")
        else:
            self.logger.warning("Configuration file not found, using default values")

    def save_config(self):
        """
        Save the current settings to the configuration file.
        """
        with self.config_file.open("w", encoding="utf-8-sig") as f:
            json.dump(
                {
                    "exclude_types": self.exclude_types,
                    "exclude_folders": self.exclude_folders,
                    "output_folder": self.output_dir,
                    "max_workers": self.max_workers,
                },
                f,
            )
        self.logger.info("Configuration saved successfully")
