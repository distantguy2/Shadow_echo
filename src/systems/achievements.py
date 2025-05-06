# src/systems/achievements.py

class Achievement:
    def __init__(self, id, name, description, requirement):
        self.id = id
        self.name = name
        self.description = description
        self.requirement = requirement
        self.unlocked = False

class AchievementManager:
    def __init__(self):
        self.achievements = {
            "first_kill": Achievement(
                "first_kill",
                "First Blood",
                "Kill your first monster",
                lambda stats: stats.get("monsters_killed", 0) >= 1
            ),
            "survivor": Achievement(
                "survivor",
                "Survivor",
                "Survive 3 days",
                lambda stats: stats.get("days_survived", 0) >= 3
            ),
            "card_master": Achievement(
                "card_master",
                "Card Master",
                "Use 10 cards in a match",
                lambda stats: stats.get("cards_used", 0) >= 10
            )
        }

    def check_achievements(self, player_stats):
        unlocked_list = []
        for achievement in self.achievements.values():
            if not achievement.unlocked and achievement.requirement(player_stats):
                achievement.unlocked = True
                unlocked_list.append(achievement.name)
        return unlocked_list

    def reset_achievements(self):
        for ach in self.achievements.values():
            ach.unlocked = False
