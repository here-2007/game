from game_logic import User, Game
# import pickle # No longer directly used in quiz.py main
# import random # No longer directly used in quiz.py main
# import time # No longer directly used in quiz.py main
# import google.generativeai as genai # No longer directly used in quiz.py main
import tkinter as tk
from tkinter import messagebox

# Global variable to store the currently logged-in user's data
current_user = None

def show_register_window(parent):
    register_window = tk.Toplevel(parent)
    register_window.title("Register New User")
    register_window.geometry("350x250")
    register_window.grab_set() # Make modal

    tk.Label(register_window, text="Name:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    name_entry = tk.Entry(register_window, width=30)
    name_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(register_window, text="Password:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    password_entry = tk.Entry(register_window, show="*", width=30)
    password_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(register_window, text="Gender (Male/Female):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
    gender_entry = tk.Entry(register_window, width=30)
    gender_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(register_window, text="Age:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
    age_entry = tk.Entry(register_window, width=30)
    age_entry.grid(row=3, column=1, padx=10, pady=5)

    def handle_register():
        name = name_entry.get()
        password = password_entry.get()
        gender = gender_entry.get()
        age = age_entry.get()

        try:
            user_data = User.register(name, password, gender, age)
            if user_data:
                messagebox.showinfo("Success", f"Registration successful!\nUID: {user_data['UID']}\nPlease login.", parent=register_window)
                register_window.destroy()
            else:
                # This case should ideally be handled by User.register raising an exception
                messagebox.showerror("Error", "Registration failed. Please try again.", parent=register_window)
        except ValueError as e:
            messagebox.showerror("Input Error", str(e), parent=register_window)
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=register_window)

    register_btn = tk.Button(register_window, text="Register", command=handle_register)
    register_btn.grid(row=4, column=0, columnspan=2, pady=10)

# Updated signature to accept button references from main window
def show_login_window(parent, main_register_button, main_login_button, main_start_game_button):
    global current_user
    login_window = tk.Toplevel(parent)
    login_window.title("Login")
    login_window.geometry("300x150")
    login_window.grab_set() # Make modal

    tk.Label(login_window, text="UID:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    uid_entry = tk.Entry(login_window, width=25)
    uid_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(login_window, text="Password:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    password_entry = tk.Entry(login_window, show="*", width=25)
    password_entry.grid(row=1, column=1, padx=10, pady=5)

    # Need to access buttons from parent (main window) to change their state
    # We assume parent is the root window and has these buttons defined as attributes or easily accessible
    # This is a simplification; a more robust way is to pass button references directly or use a class structure.
    def handle_login(main_register_button, main_login_button, main_start_game_button):
        global current_user
        uid = uid_entry.get()
        password = password_entry.get()

        try:
            user_data = User.login(uid, password)
            if user_data:
                current_user = user_data
                messagebox.showinfo("Success", f"Login successful!\nWelcome, {current_user['Name']}!", parent=login_window)
                login_window.destroy()

                # Update main window buttons
                if main_start_game_button:
                    main_start_game_button.config(state=tk.NORMAL)
                if main_register_button:
                    main_register_button.config(state=tk.DISABLED)
                if main_login_button:
                    main_login_button.config(state=tk.DISABLED)
                print(f"User {current_user['Name']} logged in. UID: {current_user['UID']}")
            else:
                messagebox.showerror("Error", "Login failed. Invalid UID or password.", parent=login_window)
        except ValueError as e:
            messagebox.showerror("Login Error", str(e), parent=login_window)
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=login_window)

    # Pass references to main window buttons to handle_login
    # This requires main_register_button, main_login_button, main_start_game_button to be defined in main()
    # and accessible here. This is tricky with current structure.
    # A common way is if main() passes its button references to show_login_window.
    # For now, let's assume these buttons are accessible via parent.children or specific names.
    # This is a bit of a hack for simplicity:
    # We'll fetch them in main and pass them to show_login_window.

    # The command for login_btn is now set here, using the passed button references
    login_btn = tk.Button(login_window, text="Login", command=lambda: handle_login(main_register_button, main_login_button, main_start_game_button))
    login_btn.grid(row=2, column=0, columnspan=2, pady=10)
    # This was the missing piece: login_btn needs to call handle_login with the button args.

def show_game_window(parent):
    global current_user
    if not current_user:
        messagebox.showerror("Error", "You must be logged in to start the game.", parent=parent)
        return

    game_window = tk.Toplevel(parent)
    game_window.title("Quiz Game - In Progress")
    game_window.geometry("500x400")
    game_window.grab_set() # Make window modal

    game_instance = Game(current_user)
    # Store the correct answer for the current riddle to check against submission
    # This needs to be part of the game_window's state or accessible to handle_submit_answer
    # Making it a list to use pass-by-reference semantics for nested functions
    current_riddle_data = {"correct_answer_text": None}


    # --- StringVars for dynamic labels ---
    score_var = tk.StringVar(value=f"Score: {current_user.get('Score', 0)}")
    level_var = tk.StringVar(value=f"Level: {current_user.get('LVL', 0)}") # LVL from user_data
    iq_var = tk.StringVar(value=f"IQ: {current_user.get('IQ', 0)}")
    riddle_text_var = tk.StringVar(value="Loading riddle...")
    selected_option_var = tk.StringVar() # For Radiobuttons

    # --- UI Elements ---
    stats_frame = tk.Frame(game_window)
    stats_frame.pack(pady=10)
    tk.Label(stats_frame, textvariable=score_var).pack(side=tk.LEFT, padx=10)
    tk.Label(stats_frame, textvariable=level_var).pack(side=tk.LEFT, padx=10)
    tk.Label(stats_frame, textvariable=iq_var).pack(side=tk.LEFT, padx=10)

    tk.Label(game_window, textvariable=riddle_text_var, wraplength=480, justify=tk.CENTER).pack(pady=20)

    options_frame = tk.Frame(game_window)
    options_frame.pack(pady=10)

    radio_buttons = []
    radio_option_vars = [tk.StringVar() for _ in range(4)] # Text for each radio button label
    for i in range(4):
        rb = tk.Radiobutton(options_frame, textvariable=radio_option_vars[i], variable=selected_option_var, value=f"option_{i}")
        rb.pack(anchor=tk.W)
        radio_buttons.append(rb)

    # --- Helper Functions ---
    def update_stats_labels(stats_dict):
        score_var.set(f"Score: {stats_dict.get('Score', 0):.1f}") # Assuming score can be float
        level_var.set(f"Level: {stats_dict.get('LVL', 0)}")
        iq_var.set(f"IQ: {stats_dict.get('IQ', 0)}")

    def load_new_riddle_ui():
        riddle_text, options, correct_answer = game_instance.get_new_riddle()
        if riddle_text and options and correct_answer:
            riddle_text_var.set(riddle_text)
            current_riddle_data["correct_answer_text"] = correct_answer

            selected_option_var.set(None) # Deselect previous answer

            for i, opt_text in enumerate(options):
                if i < len(radio_option_vars):
                    radio_option_vars[i].set(opt_text)
                    # Set the value of radio button to the actual option text for easier checking
                    radio_buttons[i].config(value=opt_text)

            # Initial stats update from game_instance (which got it from current_user)
            update_stats_labels({"Score": game_instance.score, "LVL": User.level_up(game_instance.uid,0)['LVL'], "IQ": game_instance.iq})

        else:
            messagebox.showerror("Game Error", "Failed to load a new riddle. The API might be unavailable or returned an unexpected format.", parent=game_window)
            # Consider disabling submit button or closing game window
            submit_button.config(state=tk.DISABLED)

    def handle_submit_answer():
        submitted_text = selected_option_var.get()
        if not submitted_text or not current_riddle_data["correct_answer_text"]:
            messagebox.showwarning("No Answer", "Please select an answer.", parent=game_window)
            return

        is_correct, new_stats = game_instance.check_answer_and_update_score(submitted_text, current_riddle_data["correct_answer_text"])

        if is_correct:
            messagebox.showinfo("Correct!", "Well done! Your stats have been updated.", parent=game_window)
        else:
            messagebox.showerror("Incorrect", f"Sorry, that's not right. The correct answer was: {current_riddle_data['correct_answer_text']}", parent=game_window)

        update_stats_labels(new_stats)
        load_new_riddle_ui() # Load next riddle

    submit_button = tk.Button(game_window, text="Submit Answer", command=handle_submit_answer)
    submit_button.pack(pady=20)

    # --- Initial Load ---
    load_new_riddle_ui()


def main():
    root = tk.Tk()
    root.title("Quiz Game")
    root.geometry("300x250") # Increased height for new button

    # Define buttons here so they can be passed to show_login_window's handler
    register_button = tk.Button(root, text="Register", command=lambda: show_register_window(root))
    login_button = tk.Button(root, text="Login") # Command will be set later
    start_game_button = tk.Button(root, text="Start Game", state=tk.DISABLED, command=lambda: show_game_window(root))
    quit_button = tk.Button(root, text="Quit", command=root.destroy)

    # Now set the login_button command, passing other buttons for state change
    # This lambda captures the button variables from main's scope.
    login_button.config(command=lambda: show_login_window(root, register_button, login_button, start_game_button))

    # Layout buttons
    register_button.pack(pady=10)
    login_button.pack(pady=10)
    start_game_button.pack(pady=10)
    quit_button.pack(pady=10)

    root.mainloop()

    # The old command-line input logic is now removed/commented out.
    # r = input(
    #     "Welcme Back\n1.) REGISTER(YOU'RE NEW)\n2.) LOGIN(IF ALREADY REGISTERED)\nChoose From Above Options(ONLY '1' Or '2') ->"
    # )
    # if r == "1":
    #     user = User.register()
    #     a = input('START THE GAME??("Y" or "N") ->')
    #     if a.lower() == "y":
    #         game = Game(user)
    #         game.play()
    #     elif a.lower == "n":
    #         print("QUITING......\nDONE")
    #     else:
    #         print("Invalid Input....")
    #         raise ValueError
    # elif r == "2":
    #     user = User.login(
    #         int(input("ENTER THE UID ->")), input("ENTER THE PASSWORD ->")
    #     )
    #     while True:
    #         try:
    #             a = input('START THE GAME??("Y" or "N") ->')
    #             if a.lower() == "y":
    #                 game = Game(user)
    #                 game.play()
    #                 break
    #             elif a.lower == "n":
    #                 print("QUITING......\nDONE")
    #                 break
    #             else:
    #                 print("Invalid Input....")
    #                 raise ValueError
    #         except:
    #             continue
    # else:
    #     print("Invalid Input...")
    #     raise ValueError


if __name__ == "__main__":
    main()
