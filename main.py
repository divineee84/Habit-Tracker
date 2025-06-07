import json
import sys
from datetime import datetime, date

DATA_FILE = "habits.json"
DATE_FORMAT = "%Y-%m-%d"

# ANSI colors for terminal (optional, remove if you want plain)
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def color_print(text, color):
    print(f"{color}{text}{Colors.ENDC}")

def load_data():
    """Load habit data from JSON, return empty dict if file missing/corrupted."""
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_data(data):
    """Save habit data as pretty JSON."""
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        color_print(f"Error saving data: {e}", Colors.FAIL)

def print_header(title):
    """Print formatted header with color."""
    print("\n" + "=" * 45)
    color_print(title.center(45), Colors.OKCYAN + Colors.BOLD)
    print("=" * 45)

def sanitize_habit_name(name):
    """Sanitize input habit name: lowercase, strip whitespace."""
    return name.strip().lower()

def get_validated_input(prompt, validator=lambda x: True, err_msg="Invalid input."):
    """Generic input prompt that validates user input with given validator function."""
    while True:
        user_input = input(prompt).strip()
        if validator(user_input):
            return user_input
        color_print(err_msg, Colors.WARNING)

def add_habit(data):
    print_header("ADD NEW HABIT")
    habit = get_validated_input(
        "Enter habit name: ",
        lambda x: bool(x.strip()),
        "Habit name cannot be empty."
    )
    habit = sanitize_habit_name(habit)
    if habit in data:
        color_print(f"Habit '{habit}' already exists.", Colors.WARNING)
    else:
        data[habit] = []
        color_print(f"Habit '{habit}' added successfully!", Colors.OKGREEN)

def select_habit(data):
    """Return habit key selected by user or None."""
    if not data:
        color_print("No habits to choose from. Add some first.", Colors.WARNING)
        return None
    habits = list(data.keys())
    for idx, habit in enumerate(habits, 1):
        print(f"{idx}. {habit}")
    def valid_choice(x):
        return x.isdigit() and 1 <= int(x) <= len(habits)
    choice = get_validated_input(
        f"Select habit number (1-{len(habits)}): ",
        valid_choice,
        "Enter a valid habit number."
    )
    return habits[int(choice) - 1]

def mark_done(data):
    print_header("MARK HABIT DONE")
    habit = select_habit(data)
    if not habit:
        return
    today_str = date.today().strftime(DATE_FORMAT)
    if today_str in data[habit]:
        color_print(f"'{habit}' already marked done for today.", Colors.WARNING)
    else:
        data[habit].append(today_str)
        color_print(f"Marked '{habit}' done for {today_str}!", Colors.OKGREEN)

def calculate_streak(dates):
    """
    Calculate current streak of consecutive days from the most recent date backwards.
    If last done day not yesterday or today, streak resets to 0.
    """
    if not dates:
        return 0
    date_objs = sorted(datetime.strptime(d, DATE_FORMAT).date() for d in dates)
    today = date.today()
    # If last done date > 1 day ago, streak reset
    if (today - date_objs[-1]).days > 1:
        return 0

    streak = 1
    for i in range(len(date_objs) - 1, 0, -1):
        delta = (date_objs[i] - date_objs[i-1]).days
        if delta == 1:
            streak += 1
        elif delta > 1:
            break
    return streak

def show_stats(data):
    print_header("HABIT STATISTICS")
    if not data:
        color_print("No habits tracked yet.", Colors.WARNING)
        return
    for habit, dates in data.items():
        total_done = len(dates)
        streak = calculate_streak(dates)
        color_print(f"Habit: {habit}", Colors.OKBLUE + Colors.BOLD)
        print(f"  Total days done: {total_done}")
        print(f"  Current streak:  {streak}")
        print("-" * 45)

def confirm_exit():
    """Confirm if user wants to quit."""
    choice = get_validated_input("Are you sure you want to quit? (y/n): ",
                                 lambda x: x.lower() in {"y", "n"},
                                 "Please enter y or n.")
    return choice.lower() == 'y'

def main():
    data = load_data()
    while True:
        print_header("DAILY HABIT TRACKER")
        print("1. Add habit")
        print("2. Mark habit done today")
        print("3. Show stats")
        print("4. Quit")

        choice = get_validated_input("Choose option (1-4): ",
                                     lambda x: x in {"1", "2", "3", "4"},
                                     "Choose a number between 1 and 4.")

        if choice == "1":
            add_habit(data)
            save_data(data)
        elif choice == "2":
            mark_done(data)
            save_data(data)
        elif choice == "3":
            show_stats(data)
        elif choice == "4":
            if confirm_exit():
                save_data(data)
                color_print("Peace out. Keep crushing it!", Colors.OKGREEN)
                sys.exit(0)
            else:
                continue

if __name__ == "__main__":
    main()
