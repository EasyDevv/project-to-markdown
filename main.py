import flet as ft

from src.ui import App


def main():
    app = App()
    ft.app(target=app.main, assets_dir="assets")


if __name__ == "__main__":
    main()
