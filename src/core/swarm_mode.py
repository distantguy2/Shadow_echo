# File: src/core/swarm_mode.py

import random
from typing import List, Dict, Any, Optional
from src.core.skill_system import get_skill_registry
from src.core.entities.player import Player, PlayerRole

class SwarmModeManager:
    """Manager for Swarm mode gameplay with character and role mechanics"""
    def __init__(self):
        self.skill_registry = get_skill_registry()
        self.players: List[Player] = []  # List of players in the game
        self.clues = []  # List of clues in the game world
        self.day = 1  # Current day
        self.max_days = 10  # Maximum number of days
        self.suspicious_actions = {}  # Track suspicious actions by player ID
        
    def add_player(self, player: Player):
        """Add a player to the game"""
        self.players.append(player)
        # Initialize suspicious actions tracking
        self.suspicious_actions[player.id] = []
        
    def remove_player(self, player_id: int) -> bool:
        """Remove a player from the game"""
        for i, player in enumerate(self.players):
            if player.id == player_id:
                self.players.pop(i)
                if player_id in self.suspicious_actions:
                    del self.suspicious_actions[player_id]
                return True
        return False
        
    def initialize_player(self, player: Player, character_id: str):
        """Initialize player with character passive skill and assign a secret role"""
        # Set character and passive skill
        if character_id in self.skill_registry.characters:
            character_data = self.skill_registry.characters[character_id]
            player.set_character(character_id, character_data, self.skill_registry)
            
            # Give player a starting weapon
            starting_weapon_id = 'ani_mines'  # Default starting weapon
            starting_weapon = self.skill_registry.create_weapon(starting_weapon_id, player)
            if starting_weapon:
                player.add_weapon(starting_weapon)
                
            # Secretly assign a role 
            self.assign_secret_role(player)
            
            return True
        return False
    
    def assign_secret_role(self, player: Player):
        """Secretly assign a role to player based on character potential roles"""
        # Get potential roles for this character
        character_id = player.character_id
        potential_roles = self.skill_registry.get_potential_roles_for_character(character_id)
        
        # Choose a random role from the potential roles
        role_id = random.choice(potential_roles)
        
        if role_id in self.skill_registry.roles:
            role_data = self.skill_registry.roles[role_id]
            # Pass skill_registry to assign_role for validation
            final_role_id = player.assign_role(role_id, role_data, self.skill_registry)
            
            # Initialize the role's special ability for the final assigned role
            role_ability = self.skill_registry.get_ability_for_role(final_role_id)
            if role_ability:
                role_ability.owner = player
                # Store it but don't tell the player they have it yet
                player.role_ability = role_ability
                
            return final_role_id
        return None
    
    def create_clue(self, clue_type: str, position, reveal_chance: float = 0.3) -> Dict[str, Any]:
        """Create a clue that may reveal player roles"""
        clue = {
            "type": clue_type,
            "position": position,
            "collected": False,
            "reveals_role": random.random() < reveal_chance,
            "content": self._generate_clue_content(clue_type)
        }
        self.clues.append(clue)
        return clue
    
    def _generate_clue_content(self, clue_type: str) -> str:
        """Generate appropriate content for a clue based on its type"""
        if clue_type == "document":
            return random.choice([
                "A torn page mentions suspicious behavior by one of the members...",
                "A coded message suggests someone is working for the enemy...",
                "A list of names with one circled in red ink...",
                "A map with strategic locations marked for sabotage..."
            ])
        elif clue_type == "item":
            return random.choice([
                "A peculiar device of unknown origin...",
                "A strange symbol that gives off an eerie glow...",
                "A weapon with distinctive markings...",
                "A personal item belonging to someone in your group..."
            ])
        elif clue_type == "environment":
            return random.choice([
                "Strange markings on the wall that reveal secrets when lit...",
                "A hidden compartment containing cryptic information...",
                "An unusual pattern in the environment that suggests hidden meanings...",
                "A recording device planted to spy on the group..."
            ])
        return "A mysterious clue that might reveal something about someone's true intentions..."
    
    def process_clue_collection(self, player: Player, clue_index: int) -> Dict[str, Any]:
        """Process a player collecting a clue"""
        if clue_index < 0 or clue_index >= len(self.clues):
            return {"success": False, "message": "Invalid clue index"}
            
        clue = self.clues[clue_index]
        if clue["collected"]:
            return {"success": False, "message": "Clue already collected"}
            
        clue["collected"] = True
        player.add_clue(clue)
        
        result = {
            "success": True,
            "message": f"Collected clue: {clue['content']}",
            "role_revealed": False
        }
        
        # Check if this clue reveals the player's role
        if clue["reveals_role"] and not player.known_role:
            discovered_role = player.discover_role()
            result["role_revealed"] = True
            result["role"] = discovered_role.name
            result["message"] += f"\n\nThe clue reveals your true role: {discovered_role.name}!"
            
        return result
    
    def record_suspicious_action(self, player: Player, action_type: str, details: str) -> None:
        """Record a suspicious action taken by a player"""
        if player.id not in self.suspicious_actions:
            self.suspicious_actions[player.id] = []
            
        self.suspicious_actions[player.id].append({
            "type": action_type,
            "details": details,
            "day": self.day,
            "witnesses": self._get_nearby_players(player)
        })
    
    def _get_nearby_players(self, player: Player) -> List[int]:
        """Get list of player IDs who are near enough to witness actions"""
        nearby_player_ids = []
        player_pos = player.position
        witness_range = 200  # Distance within which players can witness actions
        
        for other_player in self.players:
            if other_player.id != player.id and other_player.is_alive:
                other_pos = other_player.position
                distance = ((player_pos[0] - other_pos[0]) ** 2 + (player_pos[1] - other_pos[1]) ** 2) ** 0.5
                if distance <= witness_range:
                    nearby_player_ids.append(other_player.id)
                    
        return nearby_player_ids
    
    def check_player_alone(self, player: Player) -> bool:
        """Check if a player is alone (no other players nearby)"""
        return len(self._get_nearby_players(player)) == 0
    
    def advance_day(self) -> Dict[str, Any]:
        """Advance to the next day"""
        self.day += 1
        result = {
            "day": self.day,
            "game_over": self.day > self.max_days,
            "message": f"Day {self.day} has begun!"
        }
        
        # Generate new clues for the new day
        self._generate_daily_clues()
        
        return result
    
    def _generate_daily_clues(self) -> None:
        """Generate new clues for the current day"""
        clue_count = random.randint(2, 4)  # Random number of clues each day
        
        for _ in range(clue_count):
            clue_type = random.choice(["document", "item", "environment"])
            position = (random.randint(100, 1100), random.randint(100, 600))  # Random position on screen
            self.create_clue(clue_type, position)
    
    def check_victory_conditions(self) -> Dict[str, Any]:
        """Check if any role has achieved their victory conditions"""
        # Check protector victory conditions
        protectors_alive = sum(1 for p in self.players if p.true_role == PlayerRole.PROTECTOR and p.is_alive)
        traitors_alive = sum(1 for p in self.players if p.true_role == PlayerRole.TRAITOR and p.is_alive)
        chaos_alive = sum(1 for p in self.players if p.true_role == PlayerRole.CHAOS and p.is_alive)
        
        if self.day > self.max_days:
            # Protectors win if they survive to the end with at least half the players
            if protectors_alive >= len([p for p in self.players if p.is_alive]) / 2:
                return {
                    "game_over": True,
                    "winner": "PROTECTOR",
                    "message": "The Protectors have successfully completed their mission!"
                }
            # Traitors win if they're still alive at the end
            elif traitors_alive > 0:
                return {
                    "game_over": True,
                    "winner": "TRAITOR",
                    "message": "The Traitors have successfully infiltrated and compromised the mission!"
                }
        
        # Traitors win if all protectors are dead
        if protectors_alive == 0 and traitors_alive > 0:
            return {
                "game_over": True,
                "winner": "TRAITOR",
                "message": "All Protectors have been eliminated! The Traitors win!"
            }
            
        # Chaos wins on their own special conditions (having collected many items)
        chaos_collections = {}
        for player in self.players:
            if player.true_role == PlayerRole.CHAOS and player.is_alive:
                chaos_collections[player.id] = len(player.clues)
                
        if any(count >= 10 for count in chaos_collections.values()):
            return {
                "game_over": True,
                "winner": "CHAOS",
                "message": "Chaos reigns! A player has collected enough artifacts to unleash mayhem!"
            }
            
        # Game continues
        return {
            "game_over": False
        }
    
    def update(self, dt: float) -> None:
        """Update all players, weapons and skills"""
        for player in self.players:
            if player.is_alive:
                # Update player's passive skill
                if player.passive_skill and hasattr(player.passive_skill, 'update'):
                    player.passive_skill.update(dt)
                    
                # Update player's role ability if they've discovered their role
                if player.known_role and hasattr(player, 'role_ability') and player.role_ability:
                    player.role_ability.update(dt)
                    
                # Update all player's weapons
                for weapon in player.active_weapons:
                    if hasattr(weapon, 'update'):
                        weapon.update(dt)
                
                # Update player state
                player.update(dt)


# Create a global instance
swarm_manager = SwarmModeManager()

def get_swarm_manager():
    """Get the global Swarm mode manager"""
    return swarm_manager