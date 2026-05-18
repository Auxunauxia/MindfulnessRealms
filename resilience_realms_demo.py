#!/usr/bin/env python3
"""
Resilience Realms: Therapeutic RPG Prototype
A demo of the integrated therapeutic gaming system
"""

import json
import random
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field

# ============================================================================
# CORE DATA STRUCTURES
# ============================================================================

@dataclass
class Character:
    """Player character with therapeutic tracking"""
    name: str
    archetype: str
    pain_points: int = 0
    pleasure_points: int = 0
    resilience_score: int = 50
    emotional_state: str = "neutral"
    session_history: List[Dict] = field(default_factory=list)

    def update_emotional_state(self):
        """Update emotional state based on pain/pleasure balance"""
        balance = self.pleasure_points - self.pain_points
        if balance > 10:
            self.emotional_state = "thriving"
        elif balance > 0:
            self.emotional_state = "positive"
        elif balance > -10:
            self.emotional_state = "challenged"
        else:
            self.emotional_state = "struggling"

    def add_pain(self, amount: int, source: str):
        """Add pain points with tracking"""
        self.pain_points += amount
        self.session_history.append({
            "type": "pain",
            "amount": amount,
            "source": source,
            "timestamp": datetime.now().isoformat()
        })
        self.update_emotional_state()

    def add_pleasure(self, amount: int, source: str):
        """Add pleasure points with tracking"""
        self.pleasure_points += amount
        self.session_history.append({
            "type": "pleasure",
            "amount": amount,
            "source": source,
            "timestamp": datetime.now().isoformat()
        })
        self.update_emotional_state()

    def adjust_resilience(self, amount: int):
        """Adjust resilience score"""
        self.resilience_score = max(0, min(100, self.resilience_score + amount))

@dataclass
class GameState:
    """Current game state"""
    character: Character
    current_scene: str = ""
    scene_count: int = 0
    choices_made: List[Dict] = field(default_factory=list)
    crisis_detected: bool = False

# ============================================================================
# DICE SYSTEM (from TestDiceBias_v1.py)
# ============================================================================

class BiasedDice:
    """Dice system with therapeutic bias"""

    def __init__(self, bias_factor: float = 0.0):
        self.bias_factor = bias_factor  # -1.0 to 1.0

    def roll(self, sides: int = 20) -> int:
        """Roll dice with bias toward success or failure"""
        base_roll = random.randint(1, sides)

        if self.bias_factor > 0:  # Bias toward success
            bonus_chance = self.bias_factor
            if random.random() < bonus_chance:
                base_roll = max(base_roll, random.randint(sides // 2, sides))
        elif self.bias_factor < 0:  # Bias toward challenge
            penalty_chance = abs(self.bias_factor)
            if random.random() < penalty_chance:
                base_roll = min(base_roll, random.randint(1, sides // 2))

        return base_roll

    def adjust_bias(self, character: Character):
        """Adjust dice bias based on character state"""
        if character.emotional_state == "struggling":
            self.bias_factor = 0.3  # Help struggling players
        elif character.emotional_state == "thriving":
            self.bias_factor = -0.1  # Add challenge for thriving players
        else:
            self.bias_factor = 0.0

# ============================================================================
# STORY ENGINE
# ============================================================================

class StoryEngine:
    """Manages story progression and therapeutic content"""

    def __init__(self, story_cards: List[Dict]):
        self.story_cards = story_cards
        self.used_cards = set()
        self.therapeutic_domains = [
            "emotional_regulation",
            "social_connection",
            "problem_solving",
            "self_awareness",
            "coping_strategies"
        ]

    def get_scene(self, domain: Optional[str] = None) -> Dict:
        """Get a story scene, optionally filtered by therapeutic domain"""
        available_cards = [
            card for card in self.story_cards 
            if card.get('id') not in self.used_cards
        ]

        if not available_cards:
            self.used_cards.clear()  # Reset for replayability
            available_cards = self.story_cards

        # Filter by domain if specified
        if domain and available_cards:
            domain_cards = [
                card for card in available_cards
                if domain.lower() in str(card).lower()
            ]
            if domain_cards:
                available_cards = domain_cards

        if available_cards:
            scene = random.choice(available_cards)
            self.used_cards.add(scene.get('id'))
            return scene

        return self._create_fallback_scene()

    def _create_fallback_scene(self) -> Dict:
        """Create a fallback scene if no cards available"""
        return {
            "id": "fallback",
            "text": "You find yourself at a crossroads, reflecting on your journey so far.",
            "keys": ["reflection", "choice"]
        }

# ============================================================================
# THERAPEUTIC SYSTEM (from TherapyBot scripts)
# ============================================================================

class TherapeuticMonitor:
    """Monitors player wellbeing and provides interventions"""

    def __init__(self):
        self.crisis_keywords = [
            "hopeless", "suicide", "harm", "end it all", "give up",
            "no point", "can't go on"
        ]
        self.support_resources = {
            "crisis": "National Crisis Hotline: 988",
            "support": "You're not alone. Consider reaching out to a counselor.",
            "encouragement": "You've shown great resilience. Keep going."
        }

    def check_input(self, text: str) -> Tuple[bool, str]:
        """Check player input for crisis indicators"""
        text_lower = text.lower()
        for keyword in self.crisis_keywords:
            if keyword in text_lower:
                return True, self.support_resources["crisis"]
        return False, ""

    def provide_feedback(self, character: Character) -> str:
        """Provide therapeutic feedback based on character state"""
        if character.emotional_state == "struggling":
            return self.support_resources["support"]
        elif character.emotional_state == "thriving":
            return self.support_resources["encouragement"]
        return ""

# ============================================================================
# GAME ENGINE
# ============================================================================

class ResilienceRealmsGame:
    """Main game engine integrating all systems"""

    def __init__(self, story_cards: List[Dict]):
        self.story_engine = StoryEngine(story_cards)
        self.dice = BiasedDice()
        self.monitor = TherapeuticMonitor()
        self.game_state = None

    def start_game(self):
        """Initialize and start the game"""
        print("=" * 70)
        print("RESILIENCE REALMS: Therapeutic RPG Demo")
        print("=" * 70)
        print()
        print("Welcome to Resilience Realms, where your choices shape your journey")
        print("toward greater emotional resilience and self-understanding.")
        print()

        # Informed consent
        print("INFORMED CONSENT:")
        print("- This is a therapeutic game designed to build resilience")
        print("- Your choices and progress are tracked for therapeutic benefit")
        print("- You can stop at any time")
        print("- This is not a substitute for professional mental health care")
        print()

        consent = input("Do you consent to participate? (yes/no): ").strip().lower()
        if consent != "yes":
            print("Thank you for your time. Take care!")
            return

        # Character creation
        print("\n" + "=" * 70)
        print("CHARACTER CREATION")
        print("=" * 70)
        name = input("\nWhat is your character's name? ").strip()

        print("\nChoose your archetype:")
        archetypes = ["Warrior", "Healer", "Scholar", "Explorer", "Guardian"]
        for i, arch in enumerate(archetypes, 1):
            print(f"{i}. {arch}")

        arch_choice = input("\nEnter number (1-5): ").strip()
        archetype = archetypes[int(arch_choice) - 1] if arch_choice.isdigit() and 1 <= int(arch_choice) <= 5 else "Explorer"

        character = Character(name=name, archetype=archetype)
        self.game_state = GameState(character=character)

        print(f"\nWelcome, {name} the {archetype}!")
        print(f"Your journey toward resilience begins now...")

        # Main game loop
        self.game_loop()

    def game_loop(self):
        """Main game loop"""
        max_scenes = 5  # Demo length

        while self.game_state.scene_count < max_scenes:
            print("\n" + "=" * 70)
            print(f"SCENE {self.game_state.scene_count + 1}")
            print("=" * 70)

            # Adjust dice bias based on character state
            self.dice.adjust_bias(self.game_state.character)

            # Get next scene
            scene = self.story_engine.get_scene()
            self.present_scene(scene)

            # Get player choice
            choice = self.get_player_choice()

            # Check for crisis indicators
            is_crisis, crisis_msg = self.monitor.check_input(choice)
            if is_crisis:
                print(f"\n⚠️  {crisis_msg}")
                continue_game = input("\nWould you like to continue playing? (yes/no): ").strip().lower()
                if continue_game != "yes":
                    self.end_game()
                    return

            # Process choice
            self.process_choice(choice, scene)

            # Show character status
            self.show_status()

            # Therapeutic feedback
            feedback = self.monitor.provide_feedback(self.game_state.character)
            if feedback:
                print(f"\n💭 {feedback}")

            self.game_state.scene_count += 1

        self.end_game()

    def present_scene(self, scene: Dict):
        """Present a scene to the player"""
        scene_text = scene.get('text', scene.get('title', 'A mysterious situation unfolds...'))
        self.game_state.current_scene = scene_text

        print(f"\n{scene_text}")
        print()

    def get_player_choice(self) -> str:
        """Get player's choice/action"""
        print("What do you do?")
        print("1. Face the challenge directly")
        print("2. Seek understanding and connection")
        print("3. Take time to reflect and plan")
        print("4. Ask for help or support")

        choice = input("\nEnter your choice (1-4) or describe your action: ").strip()
        return choice

    def process_choice(self, choice: str, scene: Dict):
        """Process player choice and update game state"""
        char = self.game_state.character

        # Roll dice for outcome
        roll = self.dice.roll(20)
        success_threshold = 10

        print(f"\n🎲 Rolling... You rolled a {roll}!")

        if roll >= success_threshold:
            print("✅ Success!")
            char.add_pleasure(random.randint(2, 5), "successful_action")
            char.adjust_resilience(random.randint(1, 3))
            outcome = "Your action proves effective, and you feel more confident."
        else:
            print("⚠️  Challenge!")
            char.add_pain(random.randint(1, 3), "difficult_situation")
            outcome = "The situation is more difficult than expected, but you learn from it."

        print(f"\n{outcome}")

        # Record choice
        self.game_state.choices_made.append({
            "scene": self.game_state.current_scene[:50],
            "choice": choice,
            "roll": roll,
            "outcome": outcome
        })

    def show_status(self):
        """Display character status"""
        char = self.game_state.character
        print(f"\n📊 STATUS:")
        print(f"   Resilience: {char.resilience_score}/100")
        print(f"   Emotional State: {char.emotional_state.title()}")
        print(f"   Pain Points: {char.pain_points} | Pleasure Points: {char.pleasure_points}")

    def end_game(self):
        """End game and show summary"""
        char = self.game_state.character

        print("\n" + "=" * 70)
        print("JOURNEY COMPLETE")
        print("=" * 70)
        print(f"\nThank you for playing, {char.name} the {char.archetype}!")
        print(f"\nYour Final Stats:")
        print(f"  Resilience Score: {char.resilience_score}/100")
        print(f"  Emotional State: {char.emotional_state.title()}")
        print(f"  Scenes Completed: {self.game_state.scene_count}")
        print(f"  Pain/Pleasure Balance: {char.pleasure_points - char.pain_points}")

        print(f"\n💡 Therapeutic Insights:")
        if char.resilience_score >= 60:
            print("  You've shown great adaptability and growth!")
        elif char.resilience_score >= 40:
            print("  You're building resilience through each challenge.")
        else:
            print("  Remember: every journey has difficult moments. Keep going!")

        print(f"\n🌟 Thank you for participating in this therapeutic journey.")
        print(f"   Consider reflecting on the choices you made and what you learned.")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main entry point for demo"""
    # Load story cards (in actual implementation, load from JSON files)
    story_cards = [
        {
            "id": "scene_1",
            "text": "You encounter a stranger who seems distressed and asks for your help.",
            "keys": ["empathy", "social_connection"]
        },
        {
            "id": "scene_2",
            "text": "A difficult memory surfaces, challenging your sense of peace.",
            "keys": ["emotional_regulation", "self_awareness"]
        },
        {
            "id": "scene_3",
            "text": "You face a complex problem that requires creative thinking.",
            "keys": ["problem_solving", "resilience"]
        },
        {
            "id": "scene_4",
            "text": "An opportunity arises to connect with others who share your struggles.",
            "keys": ["social_connection", "support"]
        },
        {
            "id": "scene_5",
            "text": "You must choose between a safe path and a challenging growth opportunity.",
            "keys": ["courage", "growth_mindset"]
        }
    ]

    game = ResilienceRealmsGame(story_cards)
    game.start_game()

if __name__ == "__main__":
    main()
