import json
import random
from pynput import keyboard
import time
import sys

with open('abbreviations.json', 'r', encoding='utf-8') as f:
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

    def toggle_expansion(self):
        self.expansion_active = not self.expansion_active
        self.typed_text = ""

    def expand_abbreviation(self, abbr):
        possible_expansions = [self.abbreviations[abbr][i] for i in self.selected_indexes if i < len(self.abbreviations[abbr])]
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
            if hasattr(key, 'char') and key.char == '\\':
                self.toggle_expansion()
                return

            if not self.expansion_active:
                return

            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.ctrl_pressed = True

            if hasattr(key, 'char') and key.char:
                if key.char.isalnum():
                    self.typed_text += key.char

                    current_time = time.time()
                    if self.typed_text.split()[-1] in self.abbreviations and current_time - self.last_expansion_time > self.cooldown_period:
                        self.last_expansion_time = current_time
                        self.expand_abbreviation(self.typed_text.split()[-1])

            elif key == keyboard.Key.space:
                self.typed_text += ' '

            elif key == keyboard.Key.backspace:
                if self.ctrl_pressed:
                    self.typed_text = ""
                else:
                    self.typed_text = self.typed_text[:-1]

            elif key == keyboard.Key.enter:
                self.typed_text = ""

        except Exception as e:
            pass

        if len(self.typed_text) > self.MAX_TYPED_TEXT_LENGTH:
            self.typed_text = ""

    def on_release(self, key):
        if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            self.ctrl_pressed = False

def parse_language_options(options):
    language_options = {
        "1": [0],
        "2": [1],
        "3": [2],
        "4": [3],
        "5": [4],
        "6": [5],
        "7": [0, 1, 2, 3, 4, 5]
    }
    selected_indexes = []
    for option in options:
        if option in language_options:
            selected_indexes.extend(language_options[option])
    return selected_indexes

def main():
    selected_indexes = parse_language_options(sys.argv[1])

    expander = AbbreviationExpander(abbreviations, selected_indexes)
    with keyboard.Listener(on_press=expander.on_press, on_release=expander.on_release) as listener:
        listener.join()

if __name__ == "__main__":
    main()