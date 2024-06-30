import curses
import random
import sys
import time
import os
       
def intro_menu(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    stdscr.refresh()

    menu_options = ["Start", "Bedienung", "Exit"]
    current_option = 0
    spacing = 2  # Abstand zwischen den Menüoptionen

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        
        for idx, option in enumerate(menu_options):
            x = width // 2 - len(option) // 2
            y = height // 2 - (len(menu_options) * spacing) // 2 + idx * spacing
            if idx == current_option:
                stdscr.addstr(y, x, option, curses.A_REVERSE)
            else:
                stdscr.addstr(y, x, option)

        key = stdscr.getch()

        if key == curses.KEY_UP and current_option > 0:
            current_option -= 1
        elif key == curses.KEY_DOWN and current_option < len(menu_options) - 1:
            current_option += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_option == 0:
                return "start"
            elif current_option == 1:
                show_instructions(stdscr)
            elif current_option == 2:
                return "exit"

def show_instructions(stdscr):
    instructions = [
        "Willkommen zum Bingo-Spiel!",
        "Bedienung:",
        "  - Verwenden Sie die Pfeiltasten, um sich auf dem Spielfeld zu bewegen.",
        "  - Drücken Sie die Eingabetaste, um ein Feld auszuwählen oder zu deaktivieren.",
        "  - Drücken Sie die 'Bingo'-Taste, wenn Sie ein Bingo haben.",
        "Drücken Sie eine beliebige Taste, um zum Menü zurückzukehren."
    ]
    
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    for idx, line in enumerate(instructions):
        x = width // 2 - len(line) // 2
        y = height // 2 - len(instructions) // 2 + idx
        stdscr.addstr(y, x, line)

    stdscr.refresh()
    stdscr.getch()
    
    
class Button:
    def __init__(self, label, selected=False):
        self.label = label
        self.selected = selected
        self.pressed = False

    def toggle_pressed(self):
        self.pressed = not self.pressed
        print(f"Button {self.label} pressed: {self.pressed}")
        
    def set_pressed(self, pressed):
        self.pressed = pressed

class ButtonGridApp:
    def __init__(self, stdscr, player_name, zeilen, spalten, roundfile):
        self.stdscr = stdscr
        self.rows = zeilen
        self.columns = spalten
        self.button_width = 35
        self.button_height = 5
        self.buttons = []
        self.selected_button_index = 0
        self.player_name = player_name
        self.roundfile = roundfile
        self.game_state = None
        self.bingo_reached = False
        self.initialize_buttons()
    
    def handle_resize(self):
        curses.endwin()
        self.stdscr.refresh()
        self.stdscr.clear()
        self.draw_buttons()
        
    def draw_player_name(self):
        player_label = f"Spieler: {self.player_name}"
        start_y = 0  # Zeile direkt über dem Buttonfeld
        start_x = (curses.COLS - len(player_label)) // 2  # Zentriert über die Breite des Terminals
        self.stdscr.addstr(start_y, start_x, player_label, curses.A_BOLD)
        self.stdscr.refresh()
        
    def toggle_button_pressed(self, index):
        button = self.buttons[index]
        # Umkehrung des pressed-Status
        button.set_pressed(not button.pressed)
        row, col = divmod(index, self.columns)
    
    def resize(self):
        curses.endwin()
        self.stdscr.refresh()
        self.draw_buttons()
        
    def handle_resize(signum, frame, app):
        app.resize()
    
    def get_game_state(self):
        # Return a dictionary representing the current game state
        return {
            'buttons': [(button.label, button.pressed) for button in self.buttons],
            'selected_button_index': self.selected_button_index
        }
        
    def restore_game_state(self, game_state):
        # Restore the game state from the given dictionary
        for i, (label, pressed) in enumerate(game_state['buttons']):
            self.buttons[i].label = label
            self.buttons[i].pressed = pressed
        self.selected_button_index = game_state['selected_button_index']

    def initialize_buttons(self):
        with open(self.roundfile, 'r') as f:
            words = [line.strip() for line in f.readlines()]

        if len(words) < self.rows * self.columns:
            print(f"Not enough words in roundfile ({len(words)}) to fill the grid ({self.rows}x{self.columns}).")
            sys.exit(1)

        button_labels = random.sample(words, self.rows * self.columns)
        for label in button_labels:
            button = Button(label)
            self.buttons.append(button)
            
        self.bingo_button = Button("Bingo")
        self.buttons.append(self.bingo_button)

    def run(self, stdscr):
            self.stdscr = stdscr
            curses.curs_set(0)
            curses.start_color()
            curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
            curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_GREEN)
            curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)

            self.draw_player_name()
            self.buttons[self.selected_button_index].selected = True
            self.draw_buttons()
            while True:
                key = self.stdscr.getch()
                if key == curses.KEY_RESIZE:
                    self.handle_resize()
                elif key == curses.KEY_UP and self.selected_button_index >= self.columns:
                    self.update_selected_button(self.selected_button_index - self.columns)
                elif key == curses.KEY_DOWN and self.selected_button_index < len(self.buttons) - self.columns:
                    self.update_selected_button(self.selected_button_index + self.columns)
                elif key == curses.KEY_LEFT and self.selected_button_index % self.columns > 0:
                    self.update_selected_button(self.selected_button_index - 1)
                elif key == curses.KEY_RIGHT and self.selected_button_index % self.columns < self.columns - 1:
                    self.update_selected_button(self.selected_button_index + 1)
                elif key == 10:  # Enter key
                    if self.selected_button_index == len(self.buttons) - 1:  # BINGO button
                        if self.check_for_win():
                            self.broadcast_win()
                            self.gewonnen_animation(self.player_name)
                            return
                    else:
                        self.toggle_button_pressed(self.selected_button_index)

                self.draw_buttons()

    def toggle_button_pressed(self, index):
        button = self.buttons[index]
        button.toggle_pressed()
        row, col = divmod(index, self.columns)

    def draw_buttons(self):
        self.stdscr.clear()  # Clear the entire screen
        try:
            self.draw_player_name()  # Draw the player name label first

            max_y, max_x = self.stdscr.getmaxyx()
            button_area_height = self.rows * (self.button_height + 1) + 2
            button_area_width = self.columns * (self.button_width + 2) + 1

            if button_area_height > max_y or button_area_width > max_x:
                error_message = "Terminal window is too small. Please resize to at least {button_area_width}x{button_area_height}."
                self.stdscr.addstr(0, 0, error_message)
                self.stdscr.refresh()
                return

            for r in range(self.rows):
                for c in range(self.columns):
                    index = r * self.columns + c
                    button = self.buttons[index]

                    # Calculate position
                    start_y = r * (self.button_height + 1) + 2  # Add 2 to account for the label height
                    start_x = c * (self.button_width + 2) + 1

                    if start_y >= max_y or start_x + self.button_width >= max_x:
                        continue  # Skip drawing if the button exceeds terminal bounds

                    if button.selected:
                        if button.pressed:
                            self.stdscr.addstr(start_y, start_x, f"> [{button.label}] <", curses.color_pair(2))
                        else:
                            self.stdscr.addstr(start_y, start_x, f"> {button.label} <", curses.color_pair(1))
                    else:
                        if button.pressed:
                            self.stdscr.addstr(start_y, start_x, f"[{button.label}]", curses.color_pair(2))
                        else:
                            self.stdscr.addstr(start_y, start_x, button.label)

            # Highlight the "Bingo" button when it is selected
            bingo_start_y = self.rows * (self.button_height + 1) + 2
            bingo_start_x = 1
            if bingo_start_y < max_y and bingo_start_x + len("Bingo") < max_x:
                if self.selected_button_index == len(self.buttons) - 1:
                    self.stdscr.addstr(bingo_start_y, bingo_start_x, "Bingo", curses.A_BOLD | curses.color_pair(1))
                else:
                    self.stdscr.addstr(bingo_start_y, bingo_start_x, "Bingo", curses.A_BOLD | curses.color_pair(3))

        except curses.error as e:
            print(f"Error drawing buttons: {e}")
        
        self.stdscr.refresh()  # Refresh the screen to apply changes

    def check_for_win_and_register(self):
        if self.check_for_win():
            self.broadcast_win()
            
    def update_selected_button(self, new_index):
        self.buttons[self.selected_button_index].selected = False
        self.selected_button_index = new_index
        self.buttons[self.selected_button_index].selected = True

    def check_for_win(self):
        # Check for horizontal wins
        for r in range(self.rows):
            row_buttons = self.buttons[r * self.columns:(r + 1) * self.columns]
            if all(button.pressed for button in row_buttons):
                self.bingo_reached = True
                return True
    
        # Check for vertical wins
        for c in range(self.columns):
            col_buttons = [self.buttons[r * self.columns + c] for r in range(self.rows)]
            if all(button.pressed for button in col_buttons):
                self.bingo_reached = True
                return True
    
        # Check for diagonal wins
        diagonal_buttons = [self.buttons[i * self.columns + i] for i in range(self.rows)]
        if all(button.pressed for button in diagonal_buttons):
            self.bingo_reached = True
            return True
    
        diagonal_buttons = [self.buttons[i * self.columns + self.columns - i - 1] for i in range(self.rows)]
        if all(button.pressed for button in diagonal_buttons):
            self.bingo_reached = True
            return True
    
        return False
    
    if __name__ == "__main__":
        if len(sys.argv) != 2:
            print(f"Usage: {sys.argv[0]} <player_name>")
            sys.exit(1)
        player_name = sys.argv[1]
