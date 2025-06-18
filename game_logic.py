import pickle
import random
# import time # Unused import removed
import google.generativeai as genai

# Consider configuring genai once at the application's start if possible,
# rather than in every Game instance. For this exercise, current placement is kept.
# try:
#     genai.configure(api_key="AIzaSyB-VF5G5nbrTDzrdfLsIEyk3JRlnUsndIo")
# except Exception as e:
#     print(f"Error configuring genai at module level: {e}. API calls may fail.")


class User:
    def __init__(self, uid, name, password, gender, age, score=0, lvl=1, iq=10):
        if name == "":
            raise ValueError("Name cannot be empty.")
        if password == "" or len(password) < 6:
            raise ValueError("Password must be at least 6 characters long.")
        if not (5 <= age <= 65):
            raise ValueError("Age must be between 5 and 65.")
        if not gender.lower() in ["male", "female"]:
            raise ValueError("Gender must be 'male' or 'female'.")
        self.uid = uid
        self.name = name
        self.password = password
        self.gender = gender
        self.age = age
        self.lvl = lvl
        self.iq = iq
        self.score = score

    def save(self):
        # Save credentials
        with open("user_data.bin", "ab") as f:
            pickle.dump({"UID": self.uid, "Pass": self.password}, f)
        # Save progress
        with open("progress.bin", "ab") as f:
            pickle.dump(
                {
                    "UID": self.uid,
                    "Name": self.name,
                    "Gender": self.gender,
                    "Score": self.score,
                    "Age": self.age,
                    "LVL": self.lvl,
                    "IQ": self.iq,
                },
                f,
            )

    @classmethod
    def register(cls, name, password, gender, age_str):
        try:
            age = int(age_str)
        except ValueError:
            raise ValueError("Age must be a numeric value.")

        if name == "":
            raise ValueError("Name cannot be empty.")
        if password == "" or len(password) < 6:
            raise ValueError("Password must be at least 6 characters long.")
        if not (5 <= age <= 65):
            raise ValueError("Age must be between 5 and 65.")
        if not gender.lower() in ["male", "female"]:
            raise ValueError("Gender must be 'male' or 'female'.")

        uid = cls._generate_uid()
        user = cls(uid, name, password, gender, age)
        user.save()

        try:
            with open("progress.bin", "rb") as f:
                all_users_data = []
                try:
                    while True:
                        all_users_data.append(pickle.load(f))
                except EOFError:
                    pass

                for user_data_entry in reversed(all_users_data):
                    if user_data_entry["UID"] == uid:
                        return user_data_entry
            # This part should ideally not be reached if save and readback are consistent.
            # However, if progress.bin was empty or user not found (shouldn't happen for new UID):
            return {"UID": uid, "Name": name, "Gender": gender, "Score": 0, "Age": age, "LVL": 1, "IQ": 10}
        except (EOFError, FileNotFoundError):
            # If progress.bin doesn't exist at all, return a basic dict for the new user
            return {"UID": uid, "Name": name, "Gender": gender, "Score": 0, "Age": age, "LVL": 1, "IQ": 10}


    @classmethod
    def login(cls, uid_str, password):
        try:
            uid = int(uid_str)
        except ValueError:
            raise ValueError("UID must be a numeric value.")

        try:
            with open("user_data.bin", "rb") as f:
                user_credentials = []
                try:
                    while True:
                        user_credentials.append(pickle.load(f))
                except EOFError:
                    pass

                for data in user_credentials:
                    if data["UID"] == uid:
                        if data["Pass"] == password:
                            try:
                                with open("progress.bin", "rb") as prog_f:
                                    progress_data_list = []
                                    try:
                                        while True:
                                            progress_data_list.append(pickle.load(prog_f))
                                    except EOFError:
                                        pass

                                    for prog_data in progress_data_list:
                                        if prog_data["UID"] == uid:
                                            return prog_data
                            except (EOFError, FileNotFoundError):
                                raise ValueError("User progress data not found. Please register properly.")
                        else:
                            raise ValueError("Wrong password.")
                raise ValueError("UID not found.")
        except (EOFError, FileNotFoundError):
            raise ValueError("User data file not found. Please register first.")

    @staticmethod
    def _generate_uid():
        uids = []
        try:
            with open("user_data.bin", "rb") as f:
                while True:
                    data = pickle.load(f)
                    uids.append(data["UID"])
        except (EOFError, FileNotFoundError):
            pass

        while True:
            new_uid = random.randint(10000000000, 99999999999)
            if new_uid not in uids:
                return new_uid

    @classmethod
    def level_up(cls, uid, score_increase): # Renamed 'score' to 'score_increase' for clarity
        users = []
        found_user = False
        target_user_data = None
        try:
            with open("progress.bin", "rb") as f:
                try:
                    while True:
                        users.append(pickle.load(f))
                except EOFError:
                    pass
        except FileNotFoundError:
            # If progress.bin doesn't exist, cannot level up.
            print(f"Error: progress.bin not found during level_up for UID {uid}.")
            return None

        for user_entry in users:
            if user_entry["UID"] == uid:
                user_entry["Score"] += score_increase
                user_entry["IQ"] = round(10 + (user_entry["Score"] * 5))
                user_entry["LVL"] = round(user_entry["IQ"] / 10)
                found_user = True
                target_user_data = user_entry
                break # Found and updated user, no need to iterate further

        if found_user:
            try:
                with open("progress.bin", "wb") as f_wb:
                    for user_data_to_save in users:
                        pickle.dump(user_data_to_save, f_wb)
                return target_user_data
            except Exception as e:
                print(f"Error writing progress.bin during level_up: {e}")
                return None # Indicate error during save
        else:
            print(f"Error: User UID {uid} not found in progress.bin for level_up.")
            return None # User not found


class Game:
    def __init__(self, user):
        self.user = user # This is the user dictionary
        self.age = user["Age"]
        self.uid = user["UID"]
        self.gender = user["Gender"]
        self.score = user["Score"]
        self.iq = user["IQ"]
        try:
            # Consider moving this to a one-time setup if application structure allows
            genai.configure(api_key="AIzaSyB-VF5G5nbrTDzrdfLsIEyk3JRlnUsndIo")
        except Exception as e:
            print(f"Error configuring genai in Game init: {e}. API calls may fail.")
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def get_new_riddle(self):
        try:
            prompt = f"""
            Generate a riddle appropriate for a person with:
            - Age: {self.age}
            - Gender: {self.gender}
            - Difficulty level: {self.score} (higher score means more difficult; a score of 3+ should be very challenging).
            Ensure the riddle is unique and not repetitive.
            Provide exactly **four answer options**, one of which is correct.
            Return your response strictly in this format without any extra text or explanations:
            [Riddle, Correct_Answer, Option1, Option2, Option3, Option4]

            Example: [What has an eye, but cannot see?,A needle,A needle,A storm,A potato,A button]

            Constraints:
            - The Riddle must be a single string, and should not contain "[" or "]" characters itself.
            - Correct_Answer, Option1, Option2, Option3, Option4 must each be single strings and not contain "[" or "]" characters.
            - Correct_Answer must be identical to one of Option1, Option2, Option3, or Option4.
            """
            response = self.model.generate_content(prompt)
            text_response = response.text.strip()

            if not (text_response.startswith("[") and text_response.endswith("]")):
                print(f"Debug: Response format error - Not enclosed in brackets. Response: {text_response}")
                raise ValueError("Response format error: Not enclosed in brackets.")

            temp_parts = text_response[1:-1].split(',', 5)
            if len(temp_parts) != 6:
                print(f"Debug: Response format error - Expected 6 parts, got {len(temp_parts)}. Parts: {temp_parts}. Response: {text_response}")
                raise ValueError(f"Response format error: Expected 6 parts, got {len(temp_parts)}.")

            riddle_text = temp_parts[0].strip()
            correct_answer_text = temp_parts[1].strip()
            options_list = [opt.strip() for opt in temp_parts[2:]]

            if correct_answer_text not in options_list:
                print(f"Debug: Correct answer '{correct_answer_text}' not found in options {options_list}. LLM response: {text_response}")
                # Fallback: if LLM fails to include correct_answer in options, add it.
                # This might result in duplicate options if the LLM was close but not exact.
                # A robust solution might involve ensuring options are unique after this.
                if len(options_list) == 4: # If we have 4 options already
                    options_list[random.randrange(4)] = correct_answer_text # Replace a random one
                else: # If less than 4 options, just append
                    options_list.append(correct_answer_text)
                # Ensure we still have 4 options, padding if necessary (though LLM should provide 4)
                while len(options_list) < 4: options_list.append("Error: Missing option")
                options_list = options_list[:4] # Keep only 4

            shuffled_options = list(options_list)
            random.shuffle(shuffled_options)
            return riddle_text, shuffled_options, correct_answer_text
        except Exception as e:
            print(f"Error in get_new_riddle: {e}")
            return None, None, None

    def check_answer_and_update_score(self, submitted_answer_text, correct_answer_text):
        score_to_add = 0
        if submitted_answer_text == correct_answer_text:
            score_to_add = 0.1

        updated_stats = User.level_up(self.uid, score_to_add)

        if updated_stats:
            if submitted_answer_text == correct_answer_text: # Update game instance only if user data was successfully updated
                self.score = updated_stats["Score"]
                self.iq = updated_stats["IQ"]
                self.user = updated_stats # Keep the game's user dict in sync
            return submitted_answer_text == correct_answer_text, updated_stats
        else:
            # Failed to update user stats (e.g., user not found in progress.bin, file error)
            print(f"CRITICAL: User {self.uid} stats not updated in progress.bin during check_answer.")
            # Fallback to current game instance memory, but this indicates a data persistence problem.
            # The LVL might be stale if we don't re-calculate it here based on current self.score.
            # For simplicity, return the current game state, but this is a degraded state.
            current_lvl = round( (10 + (self.score * 5)) / 10) # Recalculate LVL based on current score
            fallback_stats = {"Score": self.score, "IQ": self.iq, "LVL": current_lvl, "UID": self.uid, "Name": self.user["Name"]}
            return submitted_answer_text == correct_answer_text, fallback_stats

    def play(self): # CLI mode
        print("Switched to CLI mode. Press Ctrl+C (or send EOF) to quit.")
        try:
            while True:
                # Fetch current LVL for display based on current score in game instance
                # User.level_up(uid, 0) will read file, this avoids it if game instance is source of truth
                current_lvl_in_game = round((10 + (self.score * 5)) / 10)

                print(f"\n--- New Riddle ---")
                print(f"Current Stats: Score {self.score:.1f}, IQ {self.iq}, LVL {current_lvl_in_game}")

                riddle_text, options, correct_answer = self.get_new_riddle()

                if not riddle_text or not options or not correct_answer:
                    print("Failed to get a new riddle. Check API key, connection or LLM response format. Exiting CLI mode.")
                    break

                print(f"\nRiddle: {riddle_text}")
                for i, opt in enumerate(options):
                    print(f"{i+1}. {opt}")

                try:
                    ans_idx_str = input(f"Choose The Correct Option (1-{len(options)}) -> ")
                except EOFError:
                    print("\nExiting game (EOF detected).")
                    break

                if not ans_idx_str.isdigit() or not (1 <= int(ans_idx_str) <= len(options)):
                    print("Invalid input. Skipping this riddle.")
                    continue

                selected_option_text = options[int(ans_idx_str) - 1]
                is_correct, new_stats = self.check_answer_and_update_score(selected_option_text, correct_answer)

                if new_stats:
                    if is_correct:
                        print(f"✅ Correct! Your new stats: Score {new_stats['Score']:.1f}, IQ {new_stats['IQ']}, LVL {new_stats['LVL']}")
                    else:
                        print(f"❌ Wrong Answer. The correct answer was: {correct_answer}")
                        print(f"Your stats remain: Score {new_stats['Score']:.1f}, IQ {new_stats['IQ']}, LVL {new_stats['LVL']}")
                else:
                    print("Error updating or fetching stats after answer.") # Should be rare with fallback in check_answer
        except KeyboardInterrupt:
            print("\nExiting game (Ctrl+C detected).")
        except Exception as e:
            print(f"\nAn unexpected error occurred in CLI mode: {e}")
            import traceback
            traceback.print_exc()
