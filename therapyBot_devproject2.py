#!/usr/bin/env python3
"""
Resilience Realms - Standalone Console RPG
Build emotional resilience through story choices, mindful skills, and reflective practice.

Standard library only. Designed to run on Windows 11 and other Python 3 environments.
"""

import json
import os
import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Tuple


DISCLAIMER = (
    "Resilience Realms is a supportive game, not therapy. "
    "I am not a licensed counselor."
)

CRISIS_RESOURCES = (
    "If you may be in immediate danger, call emergency services now.\n"
    "US & Canada: Call or text 988 (Suicide & Crisis Lifeline)\n"
    "US: Text HOME to 741741 (Crisis Text Line)\n"
    "If outside the US, contact your local emergency/crisis line."
)


class SafetyMonitor:
    """Detect potentially concerning language and show support resources."""

    def __init__(self) -> None:
        self.keywords = [
            "suicide",
            "kill myself",
            "end my life",
            "self harm",
            "self-harm",
            "hurt myself",
            "i want to die",
            "can't go on",
            "hopeless",
            "no reason to live",
            "overdose",
            "goodbye forever",
        ]

    def detect(self, text: str) -> bool:
        lowered = text.lower()
        return any(word in lowered for word in self.keywords)

    def show_resources(self) -> None:
        print("\n⚠️  I hear that this might be very heavy.")
        print("You matter, and support is available right now.")
        print(CRISIS_RESOURCES)


@dataclass
class Character:
    name: str
    path: str
    level: int = 1
    xp: int = 0
    resilience: int = 50
    emotional_strength: int = 5
    calm: int = 5
    insight: int = 5
    hp: int = 20
    max_hp: int = 20

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "path": self.path,
            "level": self.level,
            "xp": self.xp,
            "resilience": self.resilience,
            "emotional_strength": self.emotional_strength,
            "calm": self.calm,
            "insight": self.insight,
            "hp": self.hp,
            "max_hp": self.max_hp,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Character":
        return cls(**data)


@dataclass
class GameState:
    character: Character
    completed_quests: List[str] = field(default_factory=list)
    learned_skills: List[str] = field(default_factory=list)
    mood_history: List[Dict] = field(default_factory=list)
    journal_entries: List[Dict] = field(default_factory=list)
    sessions_played: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        return {
            "character": self.character.to_dict(),
            "completed_quests": self.completed_quests,
            "learned_skills": self.learned_skills,
            "mood_history": self.mood_history,
            "journal_entries": self.journal_entries,
            "sessions_played": self.sessions_played,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "GameState":
        return cls(
            character=Character.from_dict(data["character"]),
            completed_quests=data.get("completed_quests", []),
            learned_skills=data.get("learned_skills", []),
            mood_history=data.get("mood_history", []),
            journal_entries=data.get("journal_entries", []),
            sessions_played=data.get("sessions_played", 0),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
        )


class ResilienceRealmsGame:
    def __init__(self, save_path: str = "resilience_realms_save.json") -> None:
        self.save_path = save_path
        self.monitor = SafetyMonitor()
        self.state: GameState | None = None
        self.paths = {
            "1": ("Anchor Knight", "Steady under pressure."),
            "2": ("Ember Sage", "Transforms pain into insight."),
            "3": ("Kindred Ranger", "Finds strength through connection."),
        }
        self.quests = self._build_quests()

    # ----------------------------
    # Core Loop
    # ----------------------------
    def run(self) -> None:
        print("=" * 64)
        print("RESILIENCE REALMS")
        print("A story RPG for emotional resilience")
        print("=" * 64)
        print(DISCLAIMER)

        while True:
            print("\nMain Menu")
            print("1) New Game")
            print("2) Load Game")
            print("3) Delete Saved Game")
            print("4) Crisis Resources")
            print("5) Exit")
            choice = self.safe_input("Choose: ")

            if choice == "1":
                self.start_new_game()
            elif choice == "2":
                self.load_game()
            elif choice == "3":
                self.delete_save()
            elif choice == "4":
                self.monitor.show_resources()
            elif choice == "5":
                print("Take care. You did good work today.")
                break
            else:
                print("Please choose 1-5.")

    def game_hub(self) -> None:
        if not self.state:
            return

        while True:
            c = self.state.character
            print("\n" + "-" * 64)
            print(f"{c.name} | Path: {c.path} | Lv {c.level} | XP {c.xp}")
            print(f"Resilience {c.resilience} | Strength {c.emotional_strength} | Calm {c.calm} | Insight {c.insight}")
            print(f"HP {c.hp}/{c.max_hp} | Skills: {len(self.state.learned_skills)}")
            print("-" * 64)
            print("1) Continue Story Quest")
            print("2) Practice Mindfulness")
            print("3) Journal Prompt")
            print("4) View Progress")
            print("5) Save Game")
            print("6) End Session to Main Menu")

            choice = self.safe_input("Choose: ")
            if choice == "1":
                self.play_next_quest()
            elif choice == "2":
                self.mindfulness_menu()
            elif choice == "3":
                self.journaling_prompt()
            elif choice == "4":
                self.show_progress()
            elif choice == "5":
                self.save_game()
            elif choice == "6":
                self.session_checkout()
                self.save_game()
                print("Session saved. Returning to main menu.")
                break
            else:
                print("Please choose 1-6.")

    # ----------------------------
    # Setup / Save / Load / Delete
    # ----------------------------
    def start_new_game(self) -> None:
        consent = self.safe_input("\nDo you want to begin a new journey? (yes/no): ").lower()
        if consent not in {"yes", "y"}:
            print("No problem.")
            return

        name = self.safe_input("Hero name: ")
        if not name:
            name = "Traveler"

        print("\nChoose your path:")
        for k, (path_name, desc) in self.paths.items():
            print(f"{k}) {path_name} - {desc}")
        path_choice = self.safe_input("Path: ")
        path_name = self.paths.get(path_choice, self.paths["1"])[0]

        character = Character(name=name, path=path_name)
        self.state = GameState(character=character)
        self.state.sessions_played += 1

        print(f"\nWelcome, {character.name} of the {character.path}.")
        print("Your first power is simple: pause, breathe, choose.")

        self.session_checkin()
        self.unlock_skill("Breath Anchor")
        self.game_hub()

    def save_game(self) -> None:
        if not self.state:
            print("No game to save.")
            return

        self.state.updated_at = datetime.now().isoformat()
        payload = self.state.to_dict()
        try:
            with open(self.save_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            print(f"Game saved to {self.save_path}")
        except OSError as exc:
            print(f"Could not save game: {exc}")

    def load_game(self) -> None:
        if not os.path.exists(self.save_path):
            print("No save file found.")
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
        self.session_checkin()
        self.game_hub()

    def delete_save(self) -> None:
        if not os.path.exists(self.save_path):
            print("No saved game exists.")
            return

        confirm = self.safe_input("Type DELETE to remove your saved game: ")
        if confirm != "DELETE":
            print("Delete canceled.")
            return

        try:
            os.remove(self.save_path)
            print("Saved game deleted.")
        except OSError as exc:
            print(f"Could not delete save: {exc}")

    # ----------------------------
    # Mood Tracking
    # ----------------------------
    def session_checkin(self) -> None:
        if not self.state:
            return
        rating = self.ask_mood_rating("Session check-in mood (1-10): ")
        note = self.safe_input("One word for how you feel (optional): ")
        self.state.mood_history.append(
            {
                "time": datetime.now().isoformat(),
                "type": "check_in",
                "rating": rating,
                "note": note,
            }
        )

    def session_checkout(self) -> None:
        if not self.state:
            return
        rating = self.ask_mood_rating("Session check-out mood (1-10): ")
        note = self.safe_input("One word leaving this session (optional): ")
        self.state.mood_history.append(
            {
                "time": datetime.now().isoformat(),
                "type": "check_out",
                "rating": rating,
                "note": note,
            }
        )

    def ask_mood_rating(self, prompt: str) -> int:
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
    # Story / Quests / Challenges
    # ----------------------------
    def _build_quests(self) -> List[Dict]:
        return [
            {
                "id": "q1_fog_valley",
                "title": "Fog Valley of Doubt",
                "scene": "A silver fog whispers: 'You will fail before you begin.'",
                "choices": [
                    {
                        "text": "Name the fear and step forward anyway.",
                        "effects": {"resilience": 4, "insight": 1, "xp": 10},
                        "challenge": ("Echo Wraith", 9),
                    },
                    {
                        "text": "Pause for 3 breaths, then choose one small action.",
                        "effects": {"calm": 2, "resilience": 2, "xp": 9},
                        "challenge": ("Echo Wraith", 7),
                        "unlock": "Breath Anchor",
                    },
                    {
                        "text": "Ask a trusted ally for perspective.",
                        "effects": {"emotional_strength": 1, "resilience": 3, "xp": 8},
                        "challenge": ("Echo Wraith", 8),
                    },
                ],
            },
            {
                "id": "q2_mirror_keep",
                "title": "Mirror Keep",
                "scene": "The mirror shows your harsh inner critic, louder than thunder.",
                "choices": [
                    {
                        "text": "Challenge the thought with evidence.",
                        "effects": {"insight": 3, "resilience": 2, "xp": 12},
                        "challenge": ("Inner Critic", 10),
                        "unlock": "Thought Reframe",
                    },
                    {
                        "text": "Ground yourself: 5-4-3-2-1 senses.",
                        "effects": {"calm": 3, "xp": 11},
                        "challenge": ("Inner Critic", 8),
                        "unlock": "Grounding 5-4-3-2-1",
                    },
                    {
                        "text": "Avoid the mirror and rush ahead.",
                        "effects": {"resilience": -1, "xp": 6},
                        "challenge": ("Inner Critic", 11),
                    },
                ],
            },
            {
                "id": "q3_storm_bridge",
                "title": "Stormbridge",
                "scene": "Lightning cracks above as old memories rise like waves.",
                "choices": [
                    {
                        "text": "Body scan from head to toe, then cross with intention.",
                        "effects": {"calm": 2, "insight": 2, "xp": 12},
                        "challenge": ("Memory Tempest", 9),
                        "unlock": "Body Scan",
                    },
                    {
                        "text": "Repeat: 'I can feel this and still move forward.'",
                        "effects": {"resilience": 3, "xp": 10},
                        "challenge": ("Memory Tempest", 9),
                    },
                    {
                        "text": "Turn back and isolate.",
                        "effects": {"resilience": -2, "xp": 5},
                        "challenge": ("Memory Tempest", 12),
                    },
                ],
            },
            {
                "id": "q4_sun_garden",
                "title": "Sun Garden",
                "scene": "At dawn, the garden asks: 'What still gives you meaning?'",
                "choices": [
                    {
                        "text": "Name three things you are grateful for.",
                        "effects": {"calm": 2, "resilience": 2, "xp": 11},
                        "challenge": ("Numbness Shade", 8),
                        "unlock": "Gratitude Lens",
                    },
                    {
                        "text": "Write one kind sentence to yourself.",
                        "effects": {"insight": 1, "resilience": 3, "xp": 10},
                        "challenge": ("Numbness Shade", 8),
                    },
                    {
                        "text": "Ignore the question and push through.",
                        "effects": {"xp": 6},
                        "challenge": ("Numbness Shade", 10),
                    },
                ],
            },
            {
                "id": "q5_final_gate",
                "title": "The Gate of Returning",
                "scene": "The final gate opens only for those who can hold pain and hope together.",
                "choices": [
                    {
                        "text": "State one fear, one value, and one next step.",
                        "effects": {"resilience": 5, "insight": 2, "xp": 14},
                        "challenge": ("Void of Overwhelm", 11),
                    },
                    {
                        "text": "Use breath + grounding before stepping in.",
                        "effects": {"calm": 3, "resilience": 3, "xp": 13},
                        "challenge": ("Void of Overwhelm", 10),
                    },
                    {
                        "text": "Wait for perfect certainty.",
                        "effects": {"resilience": -2, "xp": 7},
                        "challenge": ("Void of Overwhelm", 12),
                    },
                ],
            },
        ]

    def play_next_quest(self) -> None:
        if not self.state:
            return

        remaining = [q for q in self.quests if q["id"] not in self.state.completed_quests]
        if not remaining:
            print("\nYou have completed all core quests.")
            print("You can keep training in mindfulness and journaling.")
            return

        quest = remaining[0]
        print("\n" + "=" * 64)
        print(f"Quest: {quest['title']}")
        print(quest["scene"])
        print("=" * 64)

        for i, ch in enumerate(quest["choices"], start=1):
            print(f"{i}) {ch['text']}")

        choice_idx = self.ask_choice(len(quest["choices"])) - 1
        chosen = quest["choices"][choice_idx]
        print(f"\nYou choose: {chosen['text']}")

        self.apply_effects(chosen.get("effects", {}))
        if "unlock" in chosen:
            self.unlock_skill(chosen["unlock"])

        enemy_name, difficulty = chosen.get("challenge", ("Doubt", 8))
        won = self.resolve_emotional_challenge(enemy_name, difficulty)

        if won:
            print("Victory. You move with more trust in yourself.")
            self.apply_effects({"resilience": 2, "xp": 5})
        else:
            print("You retreat, but you are not defeated. You still learn.")
            self.apply_effects({"insight": 1, "xp": 3})

        self.state.completed_quests.append(quest["id"])
        self.quick_reflection(quest["title"])

    def resolve_emotional_challenge(self, obstacle: str, difficulty: int) -> bool:
        if not self.state:
            return False

        c = self.state.character
        print(f"\n⚔ Emotional Challenge: {obstacle}")
        print("Choose your approach:")
        print("1) Steady Breath")
        print("2) Reframe Thought")
        print("3) Reach Out")

        approach = self.ask_choice(3)
        bonus = 0
        if approach == 1:
            bonus = c.calm
            if "Breath Anchor" in self.state.learned_skills:
                bonus += 2
        elif approach == 2:
            bonus = c.insight
            if "Thought Reframe" in self.state.learned_skills:
                bonus += 2
        elif approach == 3:
            bonus = c.emotional_strength
            bonus += 1

        player_roll = random.randint(1, 12) + bonus
        enemy_roll = random.randint(1, 12) + difficulty

        print(f"You: {player_roll} vs {obstacle}: {enemy_roll}")

        if player_roll >= enemy_roll:
            return True

        print("The obstacle presses in. One recovery move remains.")
        print("1) 30-second breath reset")
        print("2) 5-4-3-2-1 grounding reset")
        print("3) Accept loss")
        recovery = self.ask_choice(3)

        if recovery == 1:
            self.breathing_exercise(short=True)
            retry = random.randint(1, 10) + c.calm + 2
            print(f"Recovery roll: {retry} vs {enemy_roll}")
            return retry >= enemy_roll
        if recovery == 2:
            self.grounding_54321(short=True)
            retry = random.randint(1, 10) + c.insight + 2
            print(f"Recovery roll: {retry} vs {enemy_roll}")
            return retry >= enemy_roll

        return False

    # ----------------------------
    # Mindfulness Mechanics
    # ----------------------------
    def mindfulness_menu(self) -> None:
        print("\nMindfulness Practices")
        print("1) Breathing Exercise")
        print("2) Grounding 5-4-3-2-1")
        print("3) Body Scan")
        print("4) Gratitude Practice")
        print("5) CBT Reframing Tool")
        print("6) Back")
        choice = self.safe_input("Choose: ")

        if choice == "1":
            self.breathing_exercise()
        elif choice == "2":
            self.grounding_54321()
        elif choice == "3":
            self.body_scan()
        elif choice == "4":
            self.gratitude_practice()
        elif choice == "5":
            self.cbt_reframing()
        elif choice == "6":
            return
        else:
            print("Please choose 1-6.")

    def breathing_exercise(self, short: bool = False) -> None:
        if not self.state:
            return

        print("\nBreath Anchor")
        rounds = 2 if short else 4
        for i in range(1, rounds + 1):
            print(f"Round {i}: Inhale... hold... exhale.")
            input("Press Enter after one slow breath... ")

        self.apply_effects({"calm": 1, "resilience": 1, "xp": 4})
        self.unlock_skill("Breath Anchor")
        print("Nice work. Your body got the message: safer now.")

    def grounding_54321(self, short: bool = False) -> None:
        if not self.state:
            return

        print("\nGrounding 5-4-3-2-1")
        if short:
            print("Name 3 things you see, 2 you feel, 1 you hear.")
        else:
            print("Name 5 things you see.")
            self.safe_input("> ")
            print("Name 4 things you feel.")
            self.safe_input("> ")
            print("Name 3 things you hear.")
            self.safe_input("> ")
            print("Name 2 things you smell.")
            self.safe_input("> ")
            print("Name 1 thing you taste.")
            self.safe_input("> ")

        self.apply_effects({"calm": 2, "insight": 1, "xp": 5})
        self.unlock_skill("Grounding 5-4-3-2-1")
        print("Grounded. You are here, now.")

    def body_scan(self) -> None:
        if not self.state:
            return

        print("\nBody Scan")
        zones = ["forehead", "jaw", "shoulders", "chest", "stomach", "hands", "legs"]
        total_tension = 0
        for z in zones:
            raw = self.safe_input(f"Tension in your {z} (0-10): ")
            try:
                val = max(0, min(10, int(raw)))
            except ValueError:
                val = 5
            total_tension += val

        avg = total_tension / len(zones)
        if avg >= 7:
            print("High tension noticed. Try softer shoulders and slower exhale.")
            self.apply_effects({"calm": 2, "xp": 6})
        else:
            print("Good awareness. Your body map is clearer.")
            self.apply_effects({"calm": 1, "insight": 2, "xp": 6})

        self.unlock_skill("Body Scan")

    def gratitude_practice(self) -> None:
        if not self.state:
            return

        print("\nGratitude Lens")
        items = []
        for i in range(1, 4):
            entry = self.safe_input(f"One thing you're grateful for ({i}/3): ")
            items.append(entry)

        self.state.journal_entries.append(
            {
                "time": datetime.now().isoformat(),
                "type": "gratitude",
                "content": items,
            }
        )
        self.apply_effects({"resilience": 2, "calm": 1, "xp": 6})
        self.unlock_skill("Gratitude Lens")
        print("Small lights matter. You just collected three.")

    def cbt_reframing(self) -> None:
        if not self.state:
            return

        print("\nCBT Reframe")
        situation = self.safe_input("Situation: ")
        thought = self.safe_input("Automatic thought: ")
        evidence_for = self.safe_input("Evidence for it: ")
        evidence_against = self.safe_input("Evidence against it: ")
        balanced = self.safe_input("Balanced replacement thought: ")

        self.state.journal_entries.append(
            {
                "time": datetime.now().isoformat(),
                "type": "cbt_reframe",
                "situation": situation,
                "thought": thought,
                "evidence_for": evidence_for,
                "evidence_against": evidence_against,
                "balanced_thought": balanced,
            }
        )

        self.apply_effects({"insight": 3, "resilience": 2, "xp": 8})
        self.unlock_skill("Thought Reframe")
        print("Strong reframe. Thought is now a tool, not a trap.")

    def journaling_prompt(self) -> None:
        if not self.state:
            return

        prompts = [
            "What emotion visited most today, and what did it need?",
            "What challenge did you survive this week that you once feared?",
            "Which value do you want to live by tomorrow?",
            "What would you say to a friend feeling what you feel right now?",
        ]
        prompt = random.choice(prompts)
        print("\nJournal Prompt")
        print(prompt)
        response = self.safe_input("> ")

        self.state.journal_entries.append(
            {
                "time": datetime.now().isoformat(),
                "type": "journal",
                "prompt": prompt,
                "response": response,
            }
        )

        self.apply_effects({"insight": 1, "resilience": 1, "xp": 5})
        self.unlock_skill("Journal Forge")
        print("Entry recorded.")

    # ----------------------------
    # Progress / Character Systems
    # ----------------------------
    def apply_effects(self, effects: Dict[str, int]) -> None:
        if not self.state:
            return

        c = self.state.character
        c.resilience = max(0, min(100, c.resilience + effects.get("resilience", 0)))
        c.emotional_strength = max(1, c.emotional_strength + effects.get("emotional_strength", 0))
        c.calm = max(1, c.calm + effects.get("calm", 0))
        c.insight = max(1, c.insight + effects.get("insight", 0))

        gained_xp = effects.get("xp", 0)
        if gained_xp:
            self.gain_xp(gained_xp)

    def gain_xp(self, amount: int) -> None:
        if not self.state:
            return

        c = self.state.character
        c.xp += amount
        while c.xp >= self.xp_needed(c.level):
            c.xp -= self.xp_needed(c.level)
            c.level += 1
            c.max_hp += 3
            c.hp = c.max_hp
            c.emotional_strength += 1
            c.calm += 1
            c.insight += 1
            c.resilience = min(100, c.resilience + 3)
            print(f"\n⭐ Level up! You are now Level {c.level}.")

    def xp_needed(self, level: int) -> int:
        return 20 + (level - 1) * 10

    def unlock_skill(self, skill_name: str) -> None:
        if not self.state:
            return
        if skill_name not in self.state.learned_skills:
            self.state.learned_skills.append(skill_name)
            print(f"✨ Skill learned: {skill_name}")

    def show_progress(self) -> None:
        if not self.state:
            return

        c = self.state.character
        print("\nProgress")
        print(f"Name: {c.name}")
        print(f"Path: {c.path}")
        print(f"Level: {c.level}")
        print(f"XP: {c.xp}/{self.xp_needed(c.level)}")
        print(f"Resilience: {c.resilience}")
        print(f"Strength: {c.emotional_strength} | Calm: {c.calm} | Insight: {c.insight}")
        print(f"Quests completed: {len(self.state.completed_quests)}/{len(self.quests)}")
        print("Skills:")
        if self.state.learned_skills:
            for s in self.state.learned_skills:
                print(f"- {s}")
        else:
            print("- None yet")

        if self.state.mood_history:
            recent = self.state.mood_history[-5:]
            print("Recent mood ratings:")
            for m in recent:
                print(f"- {m['type']}: {m['rating']}/10 ({m.get('note', '')})")

    def quick_reflection(self, quest_title: str) -> None:
        if not self.state:
            return

        prompt = f"After '{quest_title}', what is one thing you handled better than before?"
        print("\nReflection")
        print(prompt)
        response = self.safe_input("> ")
        self.state.journal_entries.append(
            {
                "time": datetime.now().isoformat(),
                "type": "quest_reflection",
                "prompt": prompt,
                "response": response,
            }
        )

    # ----------------------------
    # Input / Safety Helpers
    # ----------------------------
    def safe_input(self, prompt: str) -> str:
        text = input(prompt).strip()
        if self.monitor.detect(text):
            self.monitor.show_resources()
            pause = input("Would you like a short grounding step now? (yes/no): ").strip().lower()
            if pause in {"yes", "y"}:
                self.grounding_54321(short=True)
        return text

    def ask_choice(self, max_choice: int) -> int:
        while True:
            raw = self.safe_input("Choose: ")
            try:
                val = int(raw)
                if 1 <= val <= max_choice:
                    return val
            except ValueError:
                pass
            print(f"Please choose 1-{max_choice}.")


def main() -> None:
    game = ResilienceRealmsGame()
    game.run()


if __name__ == "__main__":
    main()