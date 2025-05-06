# src/core/entities/npc.py

class NPC:
    def __init__(self, npc_id: int, name: str, dialogue_list: list[str], position: tuple[float, float]):
        self.npc_id = npc_id
        self.name = name
        self.dialogue_list = dialogue_list
        self.position = position
        self.alive = True
        self.hp = 50  # Thêm hp để phù hợp với hệ thống combat
        self.max_hp = 50
        self.current_dialogue_index = 0

    def talk(self) -> str:
        if not self.alive:
            return f"{self.name} is silent..."

        if self.current_dialogue_index < len(self.dialogue_list):
            dialogue = self.dialogue_list[self.current_dialogue_index]
            self.current_dialogue_index += 1
            return dialogue
        else:
            return f"{self.name} has nothing more to say."

    def reset_dialogue(self):
        self.current_dialogue_index = 0

    def take_damage(self, amount: int):
        """Thêm method này để NPCs có thể nhận damage"""
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            return f"{self.name} has died."
        return f"{self.name} received {amount} damage. HP left: {self.hp}"

    def kill(self):
        self.alive = False

    def move_to(self, position: tuple[float, float]):
        self.position = position

    def __repr__(self):
        return f"<NPC {self.name} at {self.position}, HP: {self.hp}/{self.max_hp}, Alive: {self.alive}>"
