import pickle
import random
import time
import google.generativeai as genai
from dotenv import load_dotenv
import os


class User:
    def __init__(self, uid, name, password, gender, age, score=0, lvl=1, iq=10):
        if name == "":
            raise ValueError
        if password == "" or len(password) < 6:
            raise ValueError
        if not (5 <= age <= 65):
            raise ValueError
        if not gender.lower() in ["male", "female"]:
            raise ValueError
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
    def register(cls):
        while True:
            try:
                name = input("Name -> ")
                password = input("Password(must be atleast 6 char long) -> ")
                gender = input("Gender(Male or Female) -> ")
                age = int(input("Age(Should be Numeric between 5 and 65) -> "))
                uid = cls._generate_uid()

                user = cls(uid, name, password, gender, age)
                user.save()

                print(
                    f"\n✅ Registration Successful!\nUID ->{uid}\nPassword -> {password}"
                )
                try:
                    with open("progress.bin", "rb") as f:
                        while True:
                            data = pickle.load(f)
                            if data["UID"] == uid:
                                return data
                except EOFError:
                    print("❌ Progress not found.")
                    return None
            except (ValueError, EOFError) as e:
                print(f"❌ ERROR: {str(e) or 'Enter correct values.'}\n")
                continue

    @classmethod
    def login(cls, uid, password):
        # Check UID and password match
        try:
            with open("user_data.bin", "rb") as f:
                while True:
                    data = pickle.load(f)
                    if data["UID"] == uid:
                        if data["Pass"] == password:
                            # Load full user progress
                            try:
                                with open("progress.bin", "rb") as f:
                                    while True:
                                        data = pickle.load(f)
                                        if data["UID"] == uid:
                                            print("✅ Login successful.")
                                            print(
                                                f"✅ UID-> {data['UID']}\nLVL -> {data['LVL']}\nCurrent IQ->{data['IQ']}\n\n"
                                            )
                                            return data
                            except EOFError:
                                print("❌ Progress not found.")
                                return None
                        else:
                            print("❌ WRONG PASSWORD.")
                            return None
        except:
            print("❌ UID not found. Please register.")
            return None

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
    def level_up(cls, uid, score):
        users = []
        with open("progress.bin", "rb") as f:
            try:
                while True:
                    user = pickle.load(f)
                    users.append(user)
            except EOFError:
                pass
        for user in users:
            if user["UID"] == uid:
                user["Score"] += score
                iq = round(10 + (user["Score"] * 5))
                user["IQ"] = iq
                user["LVL"] = round(iq / 10)
                # print(f"✅ UID-> {uid}\nLVL -> {user['LVL']}\nIQ->{user['IQ']}\n\n")
                with open("progress.bin", "wb") as f:
                    for user in users:
                        pickle.dump(user, f)
                return user


class Game:
    def __init__(self, user):
        self.user = user
        self.age = user["Age"]
        self.uid = user["UID"]
        self.gender = user["Gender"]
        self.score = user["Score"]
        self.iq = user["IQ"]
        load_dotenv()
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def play(self):
        print("Press Ctrl+D To Quit.")
        while True:
            try:
                self.quiz()
            except:
                print()
                break

    def quiz(self):
        response = self.model.generate_content(
            f"""
        Generate a riddle appropriate for a person with:
        - Age: {self.age}
        - Gender: {self.gender}
        - Difficulty level: {self.score} as high the score make the riddles more dificilut a score of 3 means you need to make riddles very very difivult and unique also as high it increases make it more dificult even a genius can't solve it.
            Don't repeat the same riddle again and again bring something new..
        Provide exactly **four answer options**, one of which is correct.
        Return your response strictly in this format:
        [Riddle, Correct_Answer, Option1, Option2, Option3, Option4]

        Make sure the correct answer is one of the four options. The riddle should be creative and appropriate for the given age and difficulty.
        """
        )
        raw = (
            response.text.lstrip()
            .rstrip()
            .replace("[", "")
            .replace("]", "")
            .split(",")[::-1]
        )
        riddle = ""
        for i in raw[len(raw) : 3 : -1]:
            riddle += i
        st = time.time()
        # print(raw)
        # print(riddle)
        z = [raw[0], raw[1], raw[2], raw[3]]
        a = random.choice(z)
        z.remove(a)
        b = random.choice(z)
        z.remove(b)
        c = random.choice(z)
        z.remove(c)
        k = False
        while True:
            ans = input(
                f'{riddle.replace('\'','').replace('\"','')}\nOptions->\n1.) {a}\n2.) {b}\n3.) {c}\n4.) {z[0]}\nChoose The Correct Option(Type 1,2,3,4 Only) -> '
            )
            if ans in ["1", "2", "3", "4"]:
                if ans == "1":
                    if a == raw[3]:
                        k = True
                elif ans == "2":
                    if b == raw[3]:
                        k = True
                elif ans == "3":
                    if c == raw[3]:
                        k = True
                else:
                    if z[0] == raw[3]:
                        k = True
                break
            else:
                print("Invalid Input....\nEnter Again.")
        et = time.time()
        tt = et - st
        if k:
            users = []
            with open("progress.bin", "rb") as f:
                try:
                    while True:
                        user = pickle.load(f)
                        users.append(user)
                except EOFError:
                    pass
            for user in users:
                if user["UID"] == self.uid:
                    user["Score"] += 0.1
                    n = User.level_up(self.uid, user["Score"])
                    print(
                        f"✅Correct Answer In {tt} Seconds\nUID-> {self.uid}\nLVL -> {n['LVL']}\nIQ->{n['IQ']}\n\n"
                    )
                    break
        else:
            print(f"Wrong Answer.. \nCorrect answer Was ->{raw[3]}")


def main():
    r = input(
        "Welcme Back\n1.) REGISTER(YOU'RE NEW)\n2.) LOGIN(IF ALREADY REGISTERED)\nChoose From Above Options(ONLY '1' Or '2') ->"
    )
    if r == "1":
        user = User.register()
        a = input('START THE GAME??("Y" or "N") ->')
        if a.lower() == "y":
            game = Game(user)
            game.play()
        elif a.lower() == "n":
            print("QUITING......\nDONE")
        else:
            print("Invalid Input....")
            raise ValueError
    elif r == "2":
        user = User.login(
            int(input("ENTER THE UID ->")), input("ENTER THE PASSWORD ->")
        )
        while True:
            try:
                a = input('START THE GAME??("Y" or "N") ->')
                if a.lower() == "y":
                    game = Game(user)
                    game.play()
                    break
                elif a.lower == "n":
                    print("QUITING......\nDONE")
                    break
                else:
                    print("Invalid Input....")
                    raise ValueError
            except:
                continue
    else:
        print("Invalid Input...")
        raise ValueError


if __name__ == "__main__":
    main()
