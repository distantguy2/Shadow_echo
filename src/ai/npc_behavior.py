# src/ai/npc_behavior.py

import random

class NPCBehavior:
    def __init__(self, npc_id: str, name: str):
        self.id = npc_id
        self.name = name
        self.hp = 100
        self.alive = True
        self.role_hint_given = False
        self.dialogue_state = 0

    def receive_damage(self, amount: int):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False
            return f"{self.name} has died."
        return f"{self.name} received {amount} damage. HP left: {self.hp}"

    def interact(self, context: dict) -> str:
        """
        Return dialogue or reaction based on current game context.
        """
        if not self.alive:
            return f"{self.name} is unresponsive..."

        if not self.role_hint_given and context.get("trust_level", 0) > 3:
            self.role_hint_given = True
            return f"{self.name} whispers: 'Some hide behind masks... beware the one who heals at night.'"

        dialogues = [
            f"{self.name}: 'Darkness falls. Keep your eyes open.'",
            f"{self.name}: 'I've seen shadows moving. Are you one of them?'",
            f"{self.name}: 'There's something strange about the chapel at night...'",
        ]

        response = dialogues[self.dialogue_state % len(dialogues)]
        self.dialogue_state += 1
        return response

    def decide_night_action(self, suspicion_level: int) -> str:
        """
        Determine NPC behavior at night based on suspicion level.
        """
        if suspicion_level > 7:
            return "hide"
        elif suspicion_level > 4:
            return "warn nearby player"
        else:
            return random.choice(["patrol", "stay inside", "observe"])
