import json
import random
import sys
import time

import pystray
from PIL import Image, ImageDraw
from pynput import keyboard

with open("abbreviations.json", "r", encoding="utf-8") as f:
    abbreviations = json.load(f)


class AbbreviationExpander:
    def __init__(self, abbreviations, selected_indexes):
        self.abbreviations = abbreviations
        self.typed_text = ""
        self.controller = keyboard.Controller()
        self.expansion_active = True
        self.last_expansion_time = 0
        self.cooldown_period = 0.05
        self.MAX_TYPED_TEXT_LENGTH = 100
        self.selected_indexes = selected_indexes
        self.ctrl_pressed = False
        self.tray_icon = None
        self.reset_timeout = 0.35
        self.last_key_time = 0

    def toggle_expansion(self):
        self.expansion_active = not self.expansion_active
        self.typed_text = ""
        self.update_tray_icon()

    def update_tray_icon(self):
        if self.tray_icon:
            self.tray_icon.icon = create_icon(self.expansion_active)
            self.tray_icon.title = (
                "Abbreviation Expander: ON"
                if self.expansion_active
                else "Abbreviation Expander: OFF"
            )

    def expand_abbreviation(self, abbr):
        possible_expansions = [
            self.abbreviations[abbr][i]
            for i in self.selected_indexes
            if i < len(self.abbreviations[abbr])
        ]
        if possible_expansions:
            full_text = random.choice(possible_expansions)

            for _ in range(len(abbr)):
                self.controller.press(keyboard.Key.backspace)
                self.controller.release(keyboard.Key.backspace)

            for char in full_text:
                self.controller.press(char)
                self.controller.release(char)

            self.controller.press(keyboard.Key.enter)
            self.controller.release(keyboard.Key.enter)

    def on_press(self, key):
        try:
            current_time = time.time()

            if current_time - self.last_key_time > self.reset_timeout:
                self.typed_text = ""

            self.last_key_time = current_time

            if key == keyboard.Key.insert or key == keyboard.Key.f2:
                self.toggle_expansion()
                return

            if not self.expansion_active:
                return

            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.ctrl_pressed = True

            if hasattr(key, "char") and key.char:
                if key.char.isalnum():
                    self.typed_text += key.char

                    current_time = time.time()
                    if (
                        self.typed_text.split()[-1] in self.abbreviations
                        and current_time - self.last_expansion_time
                        > self.cooldown_period
                    ):
                        self.last_expansion_time = current_time
                        self.expand_abbreviation(self.typed_text.split()[-1])

            elif key == keyboard.Key.space:
                self.typed_text += " "

            elif key == keyboard.Key.backspace:
                if self.ctrl_pressed:
                    self.typed_text = ""
                else:
                    self.typed_text = self.typed_text[:-1]

            elif key == keyboard.Key.enter:
                self.typed_text = ""

        except Exception:
            pass

        if len(self.typed_text) > self.MAX_TYPED_TEXT_LENGTH:
            self.typed_text = ""

    def on_release(self, key):
        if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            self.ctrl_pressed = False


def create_icon(active):
    color = "#22c55e" if active else "#ef4444"

    image = Image.new("RGB", (64, 64), "#222222")
    draw = ImageDraw.Draw(image)

    draw.ellipse((8, 8, 56, 56), fill=color)

    return image


def parse_language_options(options):
    language_options = {
        "1": [0],
        "2": [1],
        "3": [2],
        "4": [3],
        "5": [4],
        "6": [5],
        "7": [0, 1, 2, 3, 4, 5],
    }
    selected_indexes = []
    for option in options:
        if option in language_options:
            selected_indexes.extend(language_options[option])
    return selected_indexes


def main():
    selected_indexes = parse_language_options(sys.argv[1])

    expander = AbbreviationExpander(abbreviations, selected_indexes)

    listener = keyboard.Listener(
        on_press=expander.on_press, on_release=expander.on_release
    )

    listener.start()

    menu = pystray.Menu(
        pystray.MenuItem("Enable", lambda icon, item: set_enabled(expander, True)),
        pystray.MenuItem("Disable", lambda icon, item: set_enabled(expander, False)),
        pystray.MenuItem("Quit", lambda icon, item: quit_app(icon, listener)),
    )

    icon = pystray.Icon(
        "Abbreviation Expander", create_icon(True), "Abbreviation Expander: ON", menu
    )

    expander.tray_icon = icon

    icon.run()


def set_enabled(expander, enabled):
    expander.expansion_active = enabled
    expander.typed_text = ""
    expander.update_tray_icon()


def quit_app(icon, listener):
    listener.stop()
    icon.stop()


if __name__ == "__main__":
    main()
