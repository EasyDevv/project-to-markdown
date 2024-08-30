from types import SimpleNamespace
import flet as ft

# Color scheme
BACKGROUND_COLOR = "#141414"
SURFACE_COLOR = "#1E1E1E"
PRIMARY_COLOR = ft.colors.BLUE
BORDER_COLOR = "#333333"
TEXT_COLOR = "white70"

PADDING = 15
BORDER_RADIUS = 8

styles = SimpleNamespace(
    colors=SimpleNamespace(
        background=BACKGROUND_COLOR,
        surface=SURFACE_COLOR,
        primary=PRIMARY_COLOR,
        border=BORDER_COLOR,
        text=TEXT_COLOR,
    ),
    container=SimpleNamespace(
        padding=PADDING,
        border_radius=BORDER_RADIUS,
        border=ft.border.all(1, BORDER_COLOR),
    ),
    title=SimpleNamespace(
        size=18,
        weight=ft.FontWeight.BOLD,
        color="#fafafa",
    ),
    text=SimpleNamespace(
        color=TEXT_COLOR,
    ),
    button=SimpleNamespace(
        style=ft.ButtonStyle(
            shape={
                ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(
                    radius=BORDER_RADIUS
                ),
                ft.MaterialState.HOVERED: ft.RoundedRectangleBorder(
                    radius=BORDER_RADIUS * 2
                ),
            },
            color={
                ft.MaterialState.DEFAULT: SURFACE_COLOR,
            },
            bgcolor={
                ft.MaterialState.DEFAULT: ft.colors.GREY_100,
                ft.MaterialState.HOVERED: ft.colors.GREY_600,
                ft.MaterialState.DISABLED: ft.colors.GREY_800,
            },
        )
    ),
    textfield=SimpleNamespace(
        border_color=BORDER_COLOR,
        border_radius=BORDER_RADIUS,
        label_style=ft.TextStyle(color=TEXT_COLOR),
        text_style=ft.TextStyle(color=TEXT_COLOR),
        bgcolor="transparent",
    ),
    divider=SimpleNamespace(
        height=10,
        color="transparent",
    ),
)
