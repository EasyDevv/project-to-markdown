import asyncio
from pathlib import Path
from typing import List, Tuple


async def generate_tree_structure(files: List[Path], project_path: Path) -> str:
    """
    Asynchronously generates a complete document content including the tree structure of given files with emojis.

    :param files: List of files to generate the tree structure for
    :param project_path: Root path of the project
    :return: Generated document content string
    """

    async def add_to_tree(current_path: Path, depth: int):
        items = sorted(current_path.iterdir(), key=lambda x: (x.is_file(), x.name))
        for i, item in enumerate(items):
            rel_path = item.relative_to(project_path)
            is_last = i == len(items) - 1
            prefix = "└── " if is_last else "├── "

            if item.is_file() and item in files:
                tree.append(f"{indent * depth}{prefix}📄 {rel_path.name}")
            elif item.is_dir():
                if any(file.is_relative_to(item) for file in files):
                    tree.append(f"{indent * depth}{prefix}📂 {rel_path.name}")
                    await add_to_tree(item, depth + 1)

    tree = ["📦 root"]
    indent = "    "
    await add_to_tree(project_path, 1)

    tree_str = "\n".join(tree)

    content = []

    content.append("# Project Structure")
    content.append(f"```\n{tree_str}\n```")

    return "\n".join(content)


async def generate_content(
    folder_path: Path, files: List[Tuple[Path, str, str]]
) -> str:
    """
    Asynchronously generates content for each folder.

    :param folder_path: Path of the folder
    :param files: List of files in the folder (file path, extension, file content)
    :param project_path: Root path of the project
    :return: Generated document content
    """
    folder_name = Path(folder_path)

    async def process_file(file_path: Path, extension: str, file_content: str) -> str:
        content = []
        content.append(f"## {folder_name / file_path.name}")
        content.append(f"```{extension}")
        content.append(file_content.strip())
        content.append("```\n")
        return "\n".join(content)

    content = [f"# {folder_name} Contents"]

    # Process each file asynchronously
    file_contents = await asyncio.gather(
        *[
            process_file(file_path, extension, file_content)
            for file_path, extension, file_content in sorted(files)
        ]
    )

    content.extend(file_contents)

    return "\n".join(content)


async def generate_onefile_content(
    folder_path: Path, files: List[Tuple[Path, str, str]]
) -> str:
    """Generate content for a single file containing all processed files asynchronously.

    :param folder_path: Path of the folder
    :param files: List of files in the folder (file path, extension, file content)
    :param project_path: Root path of the project
    :return: Generated document content
    """
    content = [f"# {folder_path.name} Project Contents"]

    async def process_file(file_path: Path, extension: str, file_content: str) -> str:
        relative_path = file_path.relative_to(folder_path)
        return f"## {relative_path}\n```{extension}\n{file_content.strip()}\n```\n"

    # Process each file asynchronously
    file_contents = await asyncio.gather(
        *[
            process_file(file_path, extension, file_content)
            for file_path, extension, file_content in sorted(files)
        ]
    )

    content.extend(file_contents)
    return "\n".join(content)
