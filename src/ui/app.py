import flet as ft
from pathlib import Path
from queue import Queue
from threading import Thread
from .backend import Backend
from .styles import styles

# GitHub repository URL
GITHUB_URL = "https://github.com/easydevv/project-to-markdown"


class App:
    def __init__(self):
        self.backend = Backend(log_callback=self.log_callback)
        self.log_queue = Queue()
        self.log_thread = Thread(target=self.process_log_queue, daemon=True)
        self.log_thread.start()

    def log_callback(self, message):
        self.log_queue.put(message)

    def process_log_queue(self):
        while True:
            message = self.log_queue.get()
            if message == "STOP":
                break
            if hasattr(self, "log_view") and hasattr(self, "page"):
                self.log_view.controls.append(
                    ft.Text(message, color=styles.colors.text)
                )
                self.page.update()

    def main(self, page: ft.Page):
        self.page = page
        page.title = "Project To Markdown"
        page.padding = 20
        page.window.width = 700
        page.theme_mode = ft.ThemeMode.DARK

        def pick_directory_result(e: ft.FilePickerResultEvent):
            if e.path:
                self.backend.set_project_path(Path(e.path))
                project_path_text.value = str(self.backend.project_path)
                merge_button.disabled = False
            else:
                project_path_text.value = ""
                merge_button.disabled = True
            page.update()

        def on_project_path_change(e):
            path = e.control.value.strip()
            is_valid_path = path != "" and Path(path).exists() and Path(path).is_dir()
            merge_button.disabled = not is_valid_path
            if is_valid_path:
                self.backend.set_project_path(Path(path))
            page.update()

        pick_directory_dialog = ft.FilePicker(on_result=pick_directory_result)
        page.overlay.append(pick_directory_dialog)

        header = self.create_header()
        project_path_text = self.create_project_path_text(on_project_path_change)
        pick_directory_button = self.create_pick_directory_button(pick_directory_dialog)
        options = self.create_options()
        progress_bar = ft.ProgressBar(visible=False, color=styles.colors.primary)
        status_text = ft.Text(color=styles.colors.text)
        merge_button = self.create_merge_button(progress_bar, page)

        options_container = self.create_options_container(options)
        file_section = self.create_file_section(
            project_path_text,
            pick_directory_button,
            merge_button,
            progress_bar,
            status_text,
        )
        log_container = self.create_log_container()

        page.add(
            header,
            ft.Divider(height=styles.divider.height, color=styles.divider.color),
            ft.Row(
                [file_section, options_container],
                alignment=ft.MainAxisAlignment.START,
                expand=True,
                spacing=20,
            ),
            ft.Divider(height=styles.divider.height, color=styles.divider.color),
            log_container,
        )

    def create_header(self):
        github_icon = ft.Image(
            src="github.svg",
            width=28,
            height=28,
        )
        github_button = ft.Container(
            content=github_icon,
            on_click=lambda _: self.open_github_url(),
        )
        return ft.Row(
            [
                ft.Text(
                    "Project To Markdown",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=styles.title.color,
                ),
                github_button,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    def open_github_url(self):
        import webbrowser

        webbrowser.open(GITHUB_URL)

    def create_project_path_text(self, on_change):
        return ft.TextField(
            label="Project Path",
            on_change=on_change,
            prefix_icon=ft.icons.SEARCH,
            dense=True,
            multiline=True,
            expand=True,
            border_color=styles.colors.border,
            border_radius=styles.textfield.border_radius,
            label_style=styles.textfield.label_style,
            text_style=styles.textfield.text_style,
            bgcolor=styles.textfield.bgcolor,
        )

    def create_pick_directory_button(self, pick_directory_dialog):
        return ft.ElevatedButton(
            "Pick Directory",
            icon=ft.icons.FOLDER_OPEN,
            on_click=lambda _: pick_directory_dialog.get_directory_path(),
            style=styles.button.style,
        )

    def create_options(self):
        return ft.Column(
            [
                ft.Checkbox(
                    label="onefile",
                    tooltip="Merge into one markdown file",
                    value=self.backend.merge_onefile,
                    on_change=lambda e: self.backend.set_merge_onefile(e.control.value),
                ),
                ft.Checkbox(
                    label="timestamp",
                    tooltip="Add timestamp to each markdown filename",
                    value=self.backend.enable_timestamp,
                    on_change=lambda e: self.backend.set_enable_timestamp(
                        e.control.value
                    ),
                ),
                ft.Checkbox(
                    label="tree",
                    tooltip="Generate folder structure",
                    value=self.backend.enable_folder_structure,
                    on_change=lambda e: self.backend.set_enable_folder_structure(
                        e.control.value
                    ),
                ),
            ]
        )

    def create_merge_button(self, progress_bar, page):
        async def merge_files(e):
            if not self.backend.project_path:
                self.log_callback("Please select a project directory first.")
                page.update()
                return

            progress_bar.visible = True
            e.control.disabled = True
            page.update()

            try:
                await self.backend.merge_files()
            except Exception as ex:
                error_message = f"Error: {str(ex)}"
                self.log_callback(error_message)

            progress_bar.visible = False
            e.control.disabled = False
            page.update()

        merge_button = ft.ElevatedButton(
            "Merge Files",
            on_click=merge_files,
            disabled=True,
            style=styles.button.style,
        )

        return merge_button

    def create_options_container(self, options):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Options",
                        size=styles.title.size,
                        weight=styles.title.weight,
                        color=styles.title.color,
                    ),
                    options,
                ]
            ),
            padding=styles.container.padding,
            border_radius=styles.container.border_radius,
            border=styles.container.border,
        )

    def create_file_section(
        self,
        project_path_text,
        pick_directory_button,
        merge_button,
        progress_bar,
        status_text,
    ):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "File Selection",
                        size=styles.title.size,
                        weight=styles.title.weight,
                        color=styles.title.color,
                    ),
                    ft.Divider(height=5, color=styles.divider.color),
                    project_path_text,
                    ft.Row([pick_directory_button, merge_button]),
                    progress_bar,
                    status_text,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.START,
            ),
            expand=True,
            padding=styles.container.padding,
            border_radius=styles.container.border_radius,
            border=styles.container.border,
        )

    def create_log_container(self):
        self.log_view = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Log",
                        size=styles.title.size,
                        weight=styles.title.weight,
                        color=styles.title.color,
                    ),
                    ft.Container(
                        content=self.log_view,
                        height=200,
                        border=styles.container.border,
                        border_radius=styles.container.border_radius,
                        padding=10,
                    ),
                ]
            ),
            padding=styles.container.padding,
            border_radius=styles.container.border_radius,
            border=styles.container.border,
        )
