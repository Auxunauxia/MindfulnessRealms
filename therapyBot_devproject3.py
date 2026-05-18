import json
import os
import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


DISCLAIMER = (
    "Mindful Realms is a self-improvement game, not therapy or medical treatment. "
    "If you are in crisis, please use the Crisis Resources option."
)

CRISIS_RESOURCES = (
    "If you are in immediate danger, call your local emergency number.\n"
    "US/Canada: Call or text 988 (Suicide & Crisis Lifeline)\n"
    "US: Text HOME to 741741 (Crisis Text Line)\n"
    "International: Contact your local emergency or crisis services."
)


class SafetyMonitor:
    """Detects concerning language and offers support resources."""

    def __init__(self) -> None:
        self.keywords = [
            "suicide", "kill myself", "end my life", "self harm", "self-harm",
            "hurt myself", "i want to die", "can't go on", "hopeless",
            "no reason to live", "overdose", "goodbye forever",
        ]

    def detect(self, text: str) -> bool:
        lowered = text.lower()
        return any(word in lowered for word in self.keywords)

    def show_resources(self) -> None:
        print("\n⚠️  That sounds really heavy. You matter, and help is available right now.")
        print(CRISIS_RESOURCES)


@dataclass
class Character:
    name: str
    level: int = 1
    xp: int = 0
    resilience: int = 5   # general emotional fortitude
    clarity: int = 5      # critical thinking
    presence: int = 5     # mindfulness
    ease: int = 5         # relaxation / grounding
    hp: int = 20
    max_hp: int = 20

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "level": self.level,
            "xp": self.xp,
            "resilience": self.resilience,
            "clarity": self.clarity,
            "presence": self.presence,
            "ease": self.ease,
            "hp": self.hp,
            "max_hp": self.max_hp,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Character":
        return cls(**data)


@dataclass
class GameState:
    character: Character
    completed_exercises: List[str] = field(default_factory=list)
    unlocked_titles: List[str] = field(default_factory=list)
    journal_entries: List[Dict] = field(default_factory=list)
    mood_history: List[Dict] = field(default_factory=list)
    total_d6_rolls: int = 0
    total_xp_earned: int = 0
    sessions_played: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        return {
            "character": self.character.to_dict(),
            "completed_exercises": self.completed_exercises,
            "unlocked_titles": self.unlocked_titles,
            "journal_entries": self.journal_entries,
            "mood_history": self.mood_history,
            "total_d6_rolls": self.total_d6_rolls,
            "total_xp_earned": self.total_xp_earned,
            "sessions_played": self.sessions_played,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "GameState":
        return cls(
            character=Character.from_dict(data["character"]),
            completed_exercises=data.get("completed_exercises", []),
            unlocked_titles=data.get("unlocked_titles", []),
            journal_entries=data.get("journal_entries", []),
            mood_history=data.get("mood_history", []),
            total_d6_rolls=data.get("total_d6_rolls", 0),
            total_xp_earned=data.get("total_xp_earned", 0),
            sessions_played=data.get("sessions_played", 0),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
        )


class MindfulRealmsGame:
    def __init__(self, save_path: str = "mindful_realms_save.json") -> None:
        self.save_path = save_path
        self.monitor = SafetyMonitor()
        self.state: GameState | None = None

        # Categories: display name, stat key, [(exercise name, method_id), ...]
        self.exercises = {
            "1": ("Grounding Techniques", "ease", [
                ("5-4-3-2-1 Senses", "ground_54321"),
                ("Body Scan Mapping", "body_scan"),
                ("Cold Anchor Press", "cold_anchor"),
                ("Rooted Feet", "rooted_feet"),
            ]),
            "2": ("Critical Thinking", "clarity", [
                ("Evidence Check", "evidence_check"),
                ("Best / Worst / Likely", "scenario_plan"),
                ("Thought Reframe", "thought_reframe"),
                ("Pros & Cons List", "pros_cons"),
            ]),
            "3": ("Mindfulness Practice", "presence", [
                ("Breath Counting", "breath_count"),
                ("Mindful Observation", "mindful_obs"),
                ("Label & Watch", "label_watch"),
                ("Urge Surfing", "urge_surf"),
            ]),
            "4": ("Relaxation Techniques", "resilience", [
                ("Progressive Muscle Relax", "pmr"),
                ("Safe Place Visualize", "safe_place"),
                ("4-7-8 Breathing", "breathing_478"),
                ("Tension Release Scan", "tension_release"),
            ]),
        }

        self.level_titles = {
            2: "Beginner Groundskeeper",
            3: "Calm Seeker",
            4: "Thought Weaver",
            5: "Mindful Walker",
            6: "Resilience Keeper",
            8: "Guardian of the Realms",
        }

    # ----------------------------
    # Main Loop
    # ----------------------------
    def run(self) -> None:
        print("=" * 60)
        print("MINDFUL REALMS")
        print("Level up through practice. One breath, one thought, one step.")
        print("=" * 60)
        print(DISCLAIMER)

        while True:
            print("\nMain Menu")
            print("1) New Journey")
            print("2) Continue Journey")
            print("3) Delete Save")
            print("4) Crisis Resources")
            print("5) Exit")
            choice = self.safe_input("Choose: ")

            if choice == "1":
                self.new_game()
            elif choice == "2":
                self.load_game()
            elif choice == "3":
                self.delete_save()
            elif choice == "4":
                self.monitor.show_resources()
            elif choice == "5":
                print("Be well. Your practice matters.")
                break
            else:
                print("Please choose 1-5.")

    def game_hub(self) -> None:
        if not self.state:
            return

        while True:
            c = self.state.character
            print("\n" + "-" * 60)
            print(f"{c.name} | Level {c.level} | XP {c.xp}/{self.xp_needed(c.level)}")
            print(f"Resilience {c.resilience} | Clarity {c.clarity} | Presence {c.presence} | Ease {c.ease}")
            print(f"HP {c.hp}/{c.max_hp} | Titles: {len(self.state.unlocked_titles)}")
            print(f"Total XP earned: {self.state.total_xp_earned}  |  d6 rolls: {self.state.total_d6_rolls}")
            print("-" * 60)
            print("1) Practice Exercises")
            print("2) View Progress")
            print("3) Journal Entry")
            print("4) Save Journey")
            print("5) End Session")
            choice = self.safe_input("Choose: ")

            if choice == "1":
                self.exercise_menu()
            elif choice == "2":
                self.show_progress()
            elif choice == "3":
                self.journal_prompt()
            elif choice == "4":
                self.save_game()
            elif choice == "5":
                self.session_checkout()
                self.save_game()
                print("Session saved. Returning to main menu.")
                break
            else:
                print("Please choose 1-5.")

    # ----------------------------
    # Setup / Save / Load / Delete
    # ----------------------------
    def new_game(self) -> None:
        consent = self.safe_input("\nBegin a new journey? (yes/no): ").lower()
        if consent not in {"yes", "y"}:
            print("No problem.")
            return

        name = self.safe_input("Enter your name: ").strip()
        if not name:
            name = "Traveler"

        print("\nWelcome to Mindful Realms.")
        print("Strength grows slowly here. Each completed exercise earns 1d6 XP.")
        self.state = GameState(character=Character(name=name))
        self.state.sessions_played += 1
        self.session_checkin()
        print(f"\nGreetings, {name}. Your first power is the will to begin.")
        self.game_hub()

    def save_game(self) -> None:
        if not self.state:
            print("No active journey to save.")
            return
        self.state.updated_at = datetime.now().isoformat()
        try:
            with open(self.save_path, "w", encoding="utf-8") as f:
                json.dump(self.state.to_dict(), f, indent=2)
            print(f"Journey saved to {self.save_path}")
        except OSError as exc:
            print(f"Could not save: {exc}")

    def load_game(self) -> None:
        if not os.path.exists(self.save_path):
            print("No saved journey found.")
            return
        try:
            with open(self.save_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.state = GameState.from_dict(data)
        except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
            print(f"Could not load save: {exc}")
            return

        self.state.sessions_played += 1
        print(f"\nWelcome back, {self.state.character.name}.")
        print(f"You have rolled {self.state.total_d6_rolls} d6 dice so far.")
        self.session_checkin()
        self.game_hub()

    def delete_save(self) -> None:
        if not os.path.exists(self.save_path):
            print("No saved journey exists.")
            return
        confirm = self.safe_input("Type DELETE to erase your save: ")
        if confirm != "DELETE":
            print("Deletion canceled.")
            return
        try:
            os.remove(self.save_path)
            print("Save deleted.")
        except OSError as exc:
            print(f"Error deleting: {exc}")

    # ----------------------------
    # Mood Tracking
    # ----------------------------
    def session_checkin(self) -> None:
        if not self.state:
            return
        r = self.ask_mood("Pre-session mood (1-10): ")
        note = self.safe_input("One word for how you feel (optional): ")
        self.state.mood_history.append({
            "time": datetime.now().isoformat(),
            "type": "check_in",
            "rating": r,
            "note": note,
        })

    def session_checkout(self) -> None:
        if not self.state:
            return
        r = self.ask_mood("Post-session mood (1-10): ")
        note = self.safe_input("One word leaving this session (optional): ")
        self.state.mood_history.append({
            "time": datetime.now().isoformat(),
            "type": "check_out",
            "rating": r,
            "note": note,
        })

    def ask_mood(self, prompt: str) -> int:
        while True:
            raw = self.safe_input(prompt)
            try:
                val = int(raw)
                if 1 <= val <= 10:
                    return val
            except ValueError:
                pass
            print("Please enter a number from 1 to 10.")

    # ----------------------------
    # Exercise Core Loop
    # ----------------------------
    def exercise_menu(self) -> None:
        if not self.state:
            return

        print("\nChoose a practice category:")
        for k, (name, _, _) in self.exercises.items():
            print(f"{k}) {name}")
        print("5) Back")
        cat_choice = self.safe_input("Category: ")
        if cat_choice == "5":
            return
        if cat_choice not in self.exercises:
            print("Invalid choice.")
            return

        cat_name, stat_key, ex_list = self.exercises[cat_choice]
        print(f"\n{cat_name}")
        for i, (ex_name, ex_id) in enumerate(ex_list, start=1):
            tag = " ✓" if ex_id in self.state.completed_exercises else ""
            print(f"{i}) {ex_name}{tag}")
        print("5) Back")

        ex_pick = self.safe_input("Exercise: ")
        if ex_pick == "5":
            return
        try:
            idx = int(ex_pick) - 1
            if not (0 <= idx < len(ex_list)):
                print("Invalid choice.")
                return
        except ValueError:
            print("Invalid choice.")
            return

        ex_name, ex_id = ex_list[idx]
        method = getattr(self, f"do_{ex_id}", None)
        if not method:
            print("Exercise not yet implemented.")
            return

        print(f"\n{'='*60}")
        print(f"Exercise: {ex_name}")
        print(f"{'='*60}")
        method()

        # Award 1d6 XP
        roll = random.randint(1, 6)
        print(f"\n🎲 XP Roll (1d6): {roll}")
        self.award_xp(roll)

        # Track
        if ex_id not in self.state.completed_exercises:
            self.state.completed_exercises.append(ex_id)
            print("✅ First completion recorded.")

        self.state.total_d6_rolls += 1
        self.state.total_xp_earned += roll

        # Small thematic stat growth
        self._nudge_stat(stat_key)

        # Check for title unlocks
        self.check_titles()

    def _nudge_stat(self, stat_key: str) -> None:
        if not self.state:
            return
        c = self.state.character
        if stat_key == "ease":
            c.ease = min(100, c.ease + 1)
            print("Your Ease deepens.")
        elif stat_key == "clarity":
            c.clarity = min(100, c.clarity + 1)
            print("Your Clarity sharpens.")
        elif stat_key == "presence":
            c.presence = min(100, c.presence + 1)
            print("Your Presence steadies.")
        elif stat_key == "resilience":
            c.resilience = min(100, c.resilience + 1)
            print("Your Resilience hardens.")

    def award_xp(self, amount: int) -> None:
        if not self.state:
            return
        c = self.state.character
        c.xp += amount
        needed = self.xp_needed(c.level)
        while c.xp >= needed:
            c.xp -= needed
            c.level += 1
            c.max_hp += 3
            c.hp = c.max_hp
            c.resilience += 1
            c.clarity += 1
            c.presence += 1
            c.ease += 1
            print(f"\n⭐ LEVEL UP! You are now Level {c.level}!")
            print("All stats +1. HP fully restored.")
            needed = self.xp_needed(c.level)

    def xp_needed(self, level: int) -> int:
        # Slow, steady curve: 15, 27, 39, 51...
        return 15 + (level - 1) * 12

    def check_titles(self) -> None:
        if not self.state:
            return
        c = self.state.character
        for lvl, title in self.level_titles.items():
            if c.level >= lvl and title not in self.state.unlocked_titles:
                self.state.unlocked_titles.append(title)
                print(f"🏅 Title Unlocked: {title}")

    # ----------------------------
    # Individual Exercises
    # ----------------------------

    # --- Grounding ---
    def do_ground_54321(self) -> None:
        print("Name 5 things you can SEE.")
        self.safe_input("> ")
        print("Name 4 things you can FEEL.")
        self.safe_input("> ")
        print("Name 3 things you can HEAR.")
        self.safe_input("> ")
        print("Name 2 things you can SMELL.")
        self.safe_input("> ")
        print("Name 1 thing you can TASTE.")
        self.safe_input("> ")
        print("You are anchored to now.")

    def do_body_scan(self) -> None:
        zones = ["head", "jaw", "shoulders", "chest", "stomach", "hands", "legs"]
        print("Scan your body. Rate tension 0-10 for each zone.")
        for z in zones:
            self.safe_input(f"{z.capitalize()} tension: ")
        print("Body mapped. Awareness is grounding.")

    def do_cold_anchor(self) -> None:
        print("Hold something cool—an ice cube, cold water, or a cool surface.")
        print("Focus entirely on temperature and texture for 20 seconds.")
        self.safe_input("Press Enter when finished...")
        print("Cold anchors the nervous system. Well done.")

    def do_rooted_feet(self) -> None:
        print("Stand or sit with feet flat. Press feet down firmly for 3 seconds, then release.")
        for i in range(1, 4):
            self.safe_input(f"Root {i}/3 (Enter after): ")
        print("You are rooted.")

    # --- Critical Thinking ---
    def do_evidence_check(self) -> None:
        print("Thought Detective: Write down one worried thought.")
        thought = self.safe_input("Thought: ")
        print("List one real piece of evidence FOR it being completely true.")
        self.safe_input("Evidence for: ")
        print("List one real piece of evidence AGAINST it.")
        self.safe_input("Evidence against: ")
        print("Few thoughts survive a fair trial.")
        self._offer_journal("Evidence Check", thought)

    def do_scenario_plan(self) -> None:
        print("Scenario Planner: Name a current worry.")
        worry = self.safe_input("Worry: ")
        print("What is the WORST realistic outcome?")
        self.safe_input("Worst: ")
        print("What is the BEST realistic outcome?")
        self.safe_input("Best: ")
        print("What is the MOST LIKELY outcome?")
        self.safe_input("Most likely: ")
        print("Clarity comes from balance, not certainty.")
        self._offer_journal("Scenario Plan", worry)

    def do_thought_reframe(self) -> None:
        print("Reframe Workshop: Name a harsh thought you have about yourself.")
        neg = self.safe_input("Harsh thought: ")
        print("What would you say to a close friend who believed this about themselves?")
        friend = self.safe_input("For a friend: ")
        print(f"Balanced view: '{friend}'")
        print("Treat yourself with the same kindness.")
        self._offer_journal("Reframe", f"{neg} -> {friend}")

    def do_pros_cons(self) -> None:
        print("Pros & Cons: Name something you are avoiding or deciding.")
        topic = self.safe_input("Topic: ")
        print("List one pro of taking effective action:")
        self.safe_input("Pro: ")
        print("List one con of taking effective action:")
        self.safe_input("Con: ")
        print("No perfect choice exists—only informed ones.")
        self._offer_journal("Pros & Cons", topic)

    # --- Mindfulness ---
    def do_breath_count(self) -> None:
        print("Breath Counting: Breathe naturally. Count 10 full breaths.")
        for i in range(1, 11):
            self.safe_input(f"Breath {i}/10 (Enter after each): ")
        print("Ten breaths of presence. The mind settles.")

    def do_mindful_obs(self) -> None:
        print("Pick an object near you. Observe it as if for the very first time.")
        print("Notice color, shadow, texture, and edges.")
        self.safe_input("Press Enter after 30 seconds of observation...")
        print("Attention is the antidote to autopilot.")

    def do_label_watch(self) -> None:
        print("Notice the strongest emotion present right now.")
        emo = self.safe_input("Emotion label: ")
        print("Where in your body do you feel it most?")
        self.safe_input("Body location: ")
        print("On a scale of 1-10, how intense?")
        self.safe_input("Intensity: ")
        print(f"Labeling '{emo}' reduces its grip. You are the sky, not the storm.")

    def do_urge_surf(self) -> None:
        print("Urge Surfing: Picture your distress as an ocean wave.")
        print("It rises, peaks, and falls. You are the surfer, not the water.")
        self.safe_input("Press Enter after riding the wave for 30 seconds...")
        print("Urges pass. You remained steady.")

    # --- Relaxation ---
    def do_pmr(self) -> None:
        groups = ["hands (fists)", "shoulders", "forehead", "stomach", "thighs"]
        print("Progressive Muscle Relaxation: Tense for 5 seconds, then release.")
        for g in groups:
            self.safe_input(f"Tense and release your {g} (Enter after): ")
        print("Release stored tension. Softness is strength.")

    def do_safe_place(self) -> None:
        print("Imagine a place where you feel completely safe and at ease.")
        print("Engage every sense: sights, sounds, temperature, smells.")
        self.safe_input("Describe one sensory detail: ")
        print("Carry this place with you. It is always within reach.")

    def do_breathing_478(self) -> None:
        print("4-7-8 Breathing: Inhale for 4, hold for 7, exhale for 8.")
        for i in range(1, 4):
            self.safe_input(f"Cycle {i}/3 complete (Enter after): ")
        print("The exhale is longer than the worry.")

    def do_tension_release(self) -> None:
        print("Scan: Where is your body holding stress right now?")
        loc = self.safe_input("Location: ")
        print(f"On your next exhale, let your {loc} soften. Drop your shoulders.")
        self.safe_input("Press Enter after 3 release breaths...")
        print("Tension released. Space created.")

    def _offer_journal(self, exercise_name: str, content: str) -> None:
        if not self.state:
            return
        save = self.safe_input("Save a note to your journal? (yes/no): ").lower()
        if save in {"yes", "y"}:
            self.state.journal_entries.append({
                "time": datetime.now().isoformat(),
                "type": exercise_name,
                "content": content,
            })
            print("Saved to journal.")

    # ----------------------------
    # Progress & Journal
    # ----------------------------
    def show_progress(self) -> None:
        if not self.state:
            return
        c = self.state.character
        print("\n" + "=" * 60)
        print("PROGRESS")
        print(f"Name: {c.name}")
        print(f"Level: {c.level}  |  XP: {c.xp} / {self.xp_needed(c.level)}")
        print(f"Total XP earned: {self.state.total_xp_earned}")
        print(f"Resilience: {c.resilience} | Clarity: {c.clarity} | Presence: {c.presence} | Ease: {c.ease}")
        print(f"HP: {c.hp}/{c.max_hp}")
        print(f"Exercises completed: {len(self.state.completed_exercises)}")
        print("Titles:")
        for t in self.state.unlocked_titles:
            print(f"  - {t}")
        if self.state.mood_history:
            print("\nRecent mood:")
            for m in self.state.mood_history[-5:]:
                print(f"  - {m['type']}: {m['rating']}/10 ({m.get('note', '')})")
        print("=" * 60)

    def journal_prompt(self) -> None:
        if not self.state:
            return
        print("\nFree Journal")
        prompt = random.choice([
            "What is one small win from today?",
            "What emotion visited most often?",
            "What are you carrying that you could set down?",
            "Describe a moment of calm, however brief.",
            "What is one thing you are learning about yourself?",
        ])
        print(f"Prompt: {prompt}")
        entry = self.safe_input("> ")
        if entry:
            self.state.journal_entries.append({
                "time": datetime.now().isoformat(),
                "type": "free_journal",
                "prompt": prompt,
                "content": entry,
            })
            print("Entry saved. (Journaling is its own reward—no XP, pure reflection.)")

    # ----------------------------
    # Input & Safety Helpers
    # ----------------------------
    def safe_input(self, prompt: str) -> str:
        text = input(prompt).strip()
        if self.monitor.detect(text):
            self.monitor.show_resources()
            offer = input("Would you like a brief grounding step now? (yes/no): ").strip().lower()
            if offer in {"yes", "y"}:
                self._quick_grounding()
        return text

    def _quick_grounding(self) -> None:
        # Use plain input here to avoid recursion through safe_input
        print("\nQuick Grounding:")
        input("Name 3 things you see: ")
        input("Name 2 things you feel: ")
        input("Name 1 thing you hear: ")
        print("You are here. The moment is manageable.")


def main() -> None:
    game = MindfulRealmsGame()
    game.run()


if __name__ == "__main__":
    main()