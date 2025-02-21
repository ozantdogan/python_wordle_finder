import json
from colorama import Fore, Style
import random
import os
from typing import List
from languages.strings import MESSAGES, KEYBOARDS
from languages import languages
from config.config import APP_SETTINGS

empty_row = "_ _ _ _ _"

# Dynamic keyboard status
key_status = {}

command_list = {
    "0": "give_up",
    "1": "show_answer"
}

def init_key_status(lang: str):
    """Initialize key statuses based on the selected language"""
    global key_status
    layout = "".join(KEYBOARDS.get(lang, KEYBOARDS["en"]))
    key_status = {char: "neutral" for char in layout}

def set_key(key_name: str, status: str):
    """Update the status of a key"""
    if key_name in key_status:
        if key_status[key_name] in ["neutral", "absent"]:
            key_status[key_name] = status
        elif key_status[key_name] == "incorrect" and status == "correct":
            key_status[key_name] = status

def print_keyboard(lang: str):
    """Print the keyboard with color coding"""
    layout = KEYBOARDS.get(lang, KEYBOARDS["en"])
    color_map = {
        "correct": Fore.GREEN,
        "incorrect": Fore.YELLOW,
        "absent": Fore.LIGHTBLACK_EX,
        "neutral": Fore.WHITE
    }

    for row in layout:
        for char in row:
            print(color_map[key_status[char]] + char.lower() + " " + Style.RESET_ALL, end="")
        print()

def initiliaze_board(board, attempts=6):
    """Initialize the board with empty rows"""
    return [empty_row] * attempts

def load_words(lang: str) -> list:
    """Load word list from JSON file"""
    file_name = f"languages/data/{lang}.json"
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            return list(json.load(file))
    except Exception as e:
        print(Fore.RED + f"Error loading JSON file: {e}" + Style.RESET_ALL)
        return []

def evaluate(user_input: str, answer: str):
    """Evaluate the user input and return the color-coded result"""
    evaluation = ["null"] * len(user_input)
    remaining_chars = list(answer)

    for i, char in enumerate(user_input):
        if answer[i] == char:
            evaluation[i] = "correct"
            remaining_chars.remove(char)
    
    for i, char in enumerate(user_input):
        if evaluation[i] == "null":
            if char in remaining_chars:
                evaluation[i] = "incorrect"
                remaining_chars.remove(char)
            else:
                evaluation[i] = "absent"
    
    return evaluation

def colorize_guess(user_input: List[str], evaluations, state="inprogress"):
    """Colorize the guessed word based on the evaluation"""
    result = ""
    if(state == "left"):
        for i, evaluation in enumerate(evaluations):
            result += Fore.MAGENTA + user_input[i].upper() + " " + Style.RESET_ALL
        return result

    for i, evaluation in enumerate(evaluations):
        if evaluation == "correct":
            result += Fore.GREEN + user_input[i].upper() + " " + Style.RESET_ALL
        elif evaluation == "incorrect":
            result += Fore.YELLOW + user_input[i].upper() + " " + Style.RESET_ALL
        else:
            result += Fore.LIGHTBLACK_EX + user_input[i].upper() + " " + Style.RESET_ALL 
    return result

def print_board(board: List[str]):
    """Print the current board state"""
    for row in board:
        print(row + "\n")

def print_commands(command_list: dict, lang="en"):
    for key, value in command_list.items():
        print(Fore.LIGHTBLACK_EX + f"{key}. {MESSAGES[lang][value]}" + Style.RESET_ALL)

def print_game_state(lang, board_state):
    os.system('cls' if os.name == 'nt' else 'clear')
    print_commands(command_list, lang)
    print("\n")
    print_board(board_state)
    print_keyboard(lang)

def launch(lang: str):

    state = "inprogress"
    init_key_status(lang)
    word_list = [word.lower() for word in languages.load(lang=lang)]
    attempts = 6

    random.shuffle(word_list)
    answer = random.choice(word_list)
    meaning = languages.get_meaning(answer, lang)
    board_state = initiliaze_board([], attempts)
    board_words = []

    print_game_state(lang, board_state)

    attempts = 6
    for i in range(attempts):
        while state == "inprogress":
            user_input = input("> ").lower().strip()

            if(user_input in board_words):
                print(Fore.RED + MESSAGES[lang]["word_already_exists"] + Style.RESET_ALL)
            elif(user_input == '/show'):
                print(Fore.MAGENTA + answer + Style.RESET_ALL)
            elif user_input in command_list:
                if user_input == "0":
                    user_input = answer
                    state = "left"
                elif user_input == "1":
                    print(Fore.MAGENTA + answer + Style.RESET_ALL)
                    continue
            elif user_input not in word_list and user_input != '0':
                if(len(user_input) != 5):
                    print(Fore.RED + MESSAGES[lang]["word_must_have_5_letters"] + Style.RESET_ALL)
                else:
                    print(Fore.RED + MESSAGES[lang]["word_not_found"] + Style.RESET_ALL)
            else:
                evaluation = evaluate(user_input, answer)
                
                # Update keyboard colors
                for j, char in enumerate(user_input):
                    set_key(char, evaluation[j])

                board_words.append(user_input)
                colorized_guess = colorize_guess(user_input, evaluation, state)
                board_state[i] = colorized_guess
                
                print_game_state(lang, board_state)

                if user_input == answer and state != "left":
                    state = "won"
                break


    if(state == "won"):
        print(Fore.GREEN + MESSAGES[lang]["you_won"] + Style.RESET_ALL)
    else:
        print(Fore.LIGHTBLACK_EX + MESSAGES[lang]["game_over"].format(answer=Fore.MAGENTA + answer + Style.RESET_ALL) + Style.RESET_ALL)

    if(meaning):
        print(meaning + "\n")

    return 

def main():
    lang = languages.select()

    while(True):
        launch(lang)
        print(Fore.CYAN + "1." + MESSAGES[lang]["play_again"] + Style.RESET_ALL)
        print(Fore.CYAN + "2." + MESSAGES[lang]["change_language"] + Style.RESET_ALL)
        user_input = input("> ").lower().strip()
        if(user_input == '1'):
            continue
        elif(user_input == '2'):
            os.system('cls' if os.name == 'nt' else 'clear')
            lang = languages.select()
        else:
            break

if __name__ == "__main__":
    main()
