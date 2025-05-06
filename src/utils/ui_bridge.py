# src/utils/ui_bridge.py - IMPROVED VERSION

import pygame
from typing import Optional, List, Dict, Any
from ..core.skills import SKILL_LIBRARY

class UIBridge:
    """Enhanced UI Bridge with proper notifications and visual feedback"""
    
    def __init__(self, game):
        self.game = game
        self.notifications: List[Dict[str, Any]] = []
        self.exp_share_notifications: List[Dict[str, Any]] = []  # Separate list for EXP sharing
        self.notification_timer = 0.0
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
    
    def show_notification(self, message: str, type: str = "info", duration: float = 3.0):
        """Show notification with different types"""
        # Check if it's an EXP notification
        if "gained" in message.lower() and "exp" in message.lower():
            self.exp_share_notifications.append({
                "message": message,
                "type": type,
                "duration": duration,
                "timer": 0.0
            })
        else:
            self.notifications.append({
                "message": message,
                "type": type,
                "duration": duration,
                "timer": 0.0
            })
    
    def update(self, dt: float):
        """Update notifications"""
        # Update main notifications
        for notification in self.notifications[:]:
            notification["timer"] += dt
            if notification["timer"] >= notification["duration"]:
                self.notifications.remove(notification)
        
        # Update EXP notifications
        for notification in self.exp_share_notifications[:]:
            notification["timer"] += dt
            if notification["timer"] >= notification["duration"]:
                self.exp_share_notifications.remove(notification)
    
    def draw_notifications(self, screen: pygame.Surface):
        """Draw all notifications with proper positioning"""
        # Draw main notifications (top-right)
        y_offset = 50
        for i, notification in enumerate(self.notifications):
            self._draw_notification(screen, notification, 
                                  (screen.get_width() - 420, y_offset + i * 50))
        
        # Draw EXP share notifications (middle-right)
        y_offset = screen.get_height() // 2 - 100
        for i, notification in enumerate(self.exp_share_notifications):
            self._draw_notification(screen, notification, 
                                  (screen.get_width() - 420, y_offset + i * 35))
    
    def _draw_notification(self, screen: pygame.Surface, notification: dict, position: tuple):
        """Draw a single notification"""
        # Choose color based on type
        color = (255, 255, 255)  # Default white
        if notification["type"] == "success":
            color = (0, 255, 0)  # Green
        elif notification["type"] == "error":
            color = (255, 0, 0)  # Red
        elif notification["type"] == "warning":
            color = (255, 255, 0)  # Yellow
        elif notification["type"] == "info":
            color = (100, 200, 255)  # Light blue
        
        # Calculate alpha based on time remaining
        alpha = min(255, int(255 * (1 - notification["timer"] / notification["duration"])))
        
        # Create semi-transparent background
        surface = pygame.Surface((400, 40), pygame.SRCALPHA)
        surface.fill((0, 0, 0, 128))  # Semi-transparent black
        
        # Render text
        text = self.font.render(notification["message"], True, color)
        surface.blit(text, (10, 5))
        
        # Apply alpha and blit to screen
        surface.set_alpha(alpha)
        screen.blit(surface, position)
    
    def update_game_ui(self, screen: pygame.Surface):
        """Update all UI elements"""
        self.draw_game_info(screen)
        self.draw_skill_indicators(screen)
        self.draw_notifications(screen)
        
        # Draw EXP sharing radius indicator for current player
        if self.game.debug_mode:
            self.draw_exp_share_radius(screen)
    
    def draw_game_info(self, screen: pygame.Surface):
        """Draw game information"""
        player = self.game.players[self.game.current_player]
        
        # Phase and time
        phase_color = (255, 255, 0) if self.game.phase.value == "day" else (0, 0, 255)
        phase_text = self.font.render(f"{self.game.phase.value.upper()} - Day {self.game.day_count}", 
                                    True, phase_color)
        screen.blit(phase_text, (10, 10))
        
        time_text = self.font.render(f"Time: {int(self.game.time_left)}s", True, (255, 255, 255))
        screen.blit(time_text, (10, 50))
        
        # Health and level info
        self.draw_health_bar(screen, player.hp, player.max_hp, (10, 90))
        
        # Experience bar with proper scaling
        exp_progress = player.exp / (player.level * 100)
        self.draw_progress_bar(screen, exp_progress, f"EXP (Lvl {player.level})", (10, 130), (0, 255, 255))
    
    def draw_health_bar(self, screen: pygame.Surface, hp: float, max_hp: float, pos: tuple):
        """Draw health bar with improved visuals"""
        bar_width = 200
        bar_height = 20
        
        # Background
        pygame.draw.rect(screen, (100, 0, 0), (pos[0], pos[1], bar_width, bar_height))
        
        # Health percentage
        health_pct = hp / max_hp
        health_width = int(bar_width * health_pct)
        
        # Color gradient based on health
        if health_pct > 0.5:
            color = (0, 255, 0)  # Green
        elif health_pct > 0.25:
            color = (255, 255, 0)  # Yellow
        else:
            color = (255, 0, 0)  # Red
        
        pygame.draw.rect(screen, color, (pos[0], pos[1], health_width, bar_height))
        
        # Border
        pygame.draw.rect(screen, (255, 255, 255), (pos[0], pos[1], bar_width, bar_height), 1)
        
        # Text
        text = self.font.render(f"{int(hp)}/{int(max_hp)}", True, (255, 255, 255))
        screen.blit(text, (pos[0] + bar_width + 10, pos[1]))
    
    def draw_progress_bar(self, screen: pygame.Surface, progress: float, label: str, 
                         pos: tuple, color: tuple = (100, 100, 255)):
        """Draw progress bar"""
        bar_width = 200
        bar_height = 20
        
        # Background
        pygame.draw.rect(screen, (50, 50, 50), (pos[0], pos[1], bar_width, bar_height))
        
        # Progress
        progress_width = int(bar_width * progress)
        pygame.draw.rect(screen, color, (pos[0], pos[1], progress_width, bar_height))
        
        # Border
        pygame.draw.rect(screen, (255, 255, 255), (pos[0], pos[1], bar_width, bar_height), 1)
        
        # Text
        text = self.font.render(f"{label}: {int(progress * 100)}%", True, (255, 255, 255))
        screen.blit(text, (pos[0] + bar_width + 10, pos[1]))
    
    def draw_exp_share_radius(self, screen: pygame.Surface):
        """Draw EXP sharing radius indicator (debug mode)"""
        player = self.game.players[self.game.current_player]
        
        # Draw circle showing EXP share radius
        from ...config.settings import EXP_SHARE_RADIUS
        
        # Create transparent surface for circle
        radius_surface = pygame.Surface((EXP_SHARE_RADIUS * 2, EXP_SHARE_RADIUS * 2), pygame.SRCALPHA)
        pygame.draw.circle(radius_surface, (0, 255, 0, 50), (EXP_SHARE_RADIUS, EXP_SHARE_RADIUS), EXP_SHARE_RADIUS)
        
        # Position and blit
        circle_pos = (player.position[0] - EXP_SHARE_RADIUS, player.position[1] - EXP_SHARE_RADIUS)
        screen.blit(radius_surface, circle_pos)
        
        # Draw border
        pygame.draw.circle(screen, (0, 255, 0), player.position, EXP_SHARE_RADIUS, 2)
