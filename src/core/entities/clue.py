# src/core/entities/clue.py

class Clue:
    def __init__(self, text: str, credibility: float, source: str, target_player: str):
        self.text = text              # Nội dung của đầu mối
        self.credibility = credibility  # Độ tin cậy (0.0 - 1.0)
        self.source = source          # Nguồn cung cấp đầu mối
        self.target_player = target_player  # ID của người chơi liên quan đến đầu mối
        
    def __repr__(self):
        return f"<Clue from {self.source}: '{self.text}' (Credibility: {self.credibility:.1f})>"
