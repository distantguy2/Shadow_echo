# src/systems/card_system.py

import json
import random
from typing import Dict, List, Optional, Any
from pathlib import Path

class CardSystem:
    """Manages all card-related operations including dealing, using, and tracking effects"""
    
    def __init__(self, game, card_db_path: str = None):
        self.game = game
        self.cards_data = {}
        
        # Load card database or use predefined cards
        if card_db_path and Path(card_db_path).exists():
            self._load_card_database(card_db_path)
        else:
            # Use predefined cards from CardGenerator if database not found
            if hasattr(game, 'card_generator'):
                self._initialize_from_generator()
            else:
                self._initialize_default_cards()
        
        # Track card usage history
        self.usage_history = {}

    def _load_card_database(self, path: str):
        """Load card database from JSON file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.cards_data = json.load(f)
                self.game.logger.info(f"Loaded {len(self.cards_data)} cards from database")
        except Exception as e:
            self.game.logger.error(f"Failed to load card database: {str(e)}")
            self._initialize_default_cards()
    
    def _initialize_from_generator(self):
        """Initialize cards data from the CardGenerator"""
        # Get all cards from generator
        all_cards = []
        all_cards.extend(self.game.card_generator.attack_cards)
        all_cards.extend(self.game.card_generator.utility_cards)
        all_cards.extend(self.game.card_generator.support_cards)
        
        # Convert to dictionary
        for card in all_cards:
            self.cards_data[card["id"]] = card
    
    def _initialize_default_cards(self):
        """Initialize with default cards if no database available"""
        self.cards_data = {
            "attack": {
                "id": "attack",
                "name": "Basic Attack",
                "type": "attack",
                "icon": "⚔️",
                "description": "A basic attack card.",
                "effect": {"damage": 20}
            },
            "utility": {
                "id": "utility",
                "name": "Basic Utility",
                "type": "utility",
                "icon": "🔧",
                "description": "A basic utility card.",
                "effect": {"slow": 0.3}
            },
            "support": {
                "id": "support",
                "name": "Basic Support",
                "type": "support",
                "icon": "❤️",
                "description": "A basic support card.",
                "effect": {"heal": 20}
            }
        }

    def get_card_info(self, card_id: str) -> Optional[Dict[str, Any]]:
        """Get complete information for a card"""
        return self.cards_data.get(card_id)

    def use_card(self, player, card_id: str, current_phase) -> Dict[str, Any]:
        """
        Attempt to use a card
        Returns dictionary with success status and message
        """
        card_info = self.get_card_info(card_id)
        if not card_info:
            return {"success": False, "message": "Invalid card"}
        
        # TODO: Implement phase restrictions and role restrictions
        
        # Apply card effects
        result = self._apply_card_effects(player, card_id, card_info)
        
        # Track usage
        self._record_card_usage(player, card_id)
        
        return result

    def _apply_card_effects(self, player, card_id: str, card_info: Dict[str, Any]) -> Dict[str, Any]:
        """Apply card effect to the game state"""
        try:
            effect = card_info.get("effect", {})
            card_type = card_info.get("type", "normal")
            
            # Apply effects based on card type
            effect_result = None
            
            if card_type == "attack":
                # Apply damage effects
                if "damage" in effect:
                    effect_result = f"Deals {effect['damage']} damage"
                
            elif card_type == "utility":
                # Apply utility effects
                if "slow" in effect:
                    effect_result = f"Slows enemies by {effect['slow']*100}%"
                
            elif card_type == "support":
                # Apply support effects
                if "heal" in effect:
                    player.hp = min(player.hp + effect["heal"], 100)
                    effect_result = f"Healed {effect['heal']} HP"
                
                if "max_hp" in effect:
                    # TODO: Implement max HP increase
                    effect_result = f"Increased max HP to {effect['max_hp']}"
            
            return {
                "success": True,
                "message": f"{player.name} used {card_info['name']}. {effect_result if effect_result else ''}"
            }
        except Exception as e:
            self.game.logger.error(f"Error applying card effects: {str(e)}")
            return {"success": False, "message": "Card effect failed"}

    def _record_card_usage(self, player, card_id: str):
        """Track card usage for combo detection"""
        player_id = str(player.id)
        if player_id not in self.usage_history:
            self.usage_history[player_id] = []
        
        self.usage_history[player_id].append(card_id)
        
        # Keep only last 3 cards for combo detection
        if len(self.usage_history[player_id]) > 3:
            self.usage_history[player_id].pop(0)

    def add_card_to_player(self, player, card: Dict[str, Any]):
        """Add a card to player's hand from selection"""
        # Make sure card is in the database
        card_id = card["id"]
        if card_id not in self.cards_data:
            self.cards_data[card_id] = card
        
        # Add to player's hand
        player.cards.append(card_id)
        
        return True
