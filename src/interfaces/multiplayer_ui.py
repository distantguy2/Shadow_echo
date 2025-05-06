import pygame
import pygame_gui
import asyncio
from typing import Optional, List


class MultiplayerScreen:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.manager = pygame_gui.UIManager((screen.get_width(), screen.get_height()))
        self.client = None
        self.current_state = "main_menu"  # main_menu, lobby_list, in_lobby, connecting
        self.lobby_players = []
        self.create_ui_elements()

    def create_ui_elements(self):
        self.play_online_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((400, 300), (200, 50)),
            text='Play Online',
            manager=self.manager
        )

        self.play_local_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((400, 370), (200, 50)),
            text='Play Local',
            manager=self.manager
        )

        self.name_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((400, 250), (200, 32)),
            manager=self.manager,
            initial_text='Your Name'
        )

        self.create_lobby_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((50, 50), (200, 50)),
            text='Create Lobby',
            manager=self.manager,
            visible=False
        )

        self.refresh_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((50, 120), (200, 50)),
            text='Refresh',
            manager=self.manager,
            visible=False
        )

        self.back_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((50, 700), (150, 50)),
            text='Back',
            manager=self.manager,
            visible=False
        )

        self.start_game_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((900, 700), (200, 50)),
            text='Start Game',
            manager=self.manager,
            visible=False
        )

        self.ready_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((700, 700), (180, 50)),
            text='Ready',
            manager=self.manager,
            visible=False
        )

        self.status_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((400, 50), (400, 50)),
            text='Shadow Echo Online',
            manager=self.manager
        )

        self.lobby_selection = pygame_gui.elements.UISelectionList(
            relative_rect=pygame.Rect((300, 150), (600, 300)),
            item_list=[],
            manager=self.manager,
            visible=False
        )

    def set_state(self, state: str):
        self.current_state = state
        self.update_ui_visibility()

    def update_ui_visibility(self):
        for element in [
            self.play_online_button, self.play_local_button, self.name_input,
            self.create_lobby_button, self.refresh_button, self.back_button,
            self.start_game_button, self.ready_button, self.lobby_selection
        ]:
            element.hide()

        if self.current_state == "main_menu":
            self.play_online_button.show()
            self.play_local_button.show()
            self.name_input.show()
        elif self.current_state == "lobby_list":
            self.create_lobby_button.show()
            self.refresh_button.show()
            self.back_button.show()
            self.lobby_selection.show()
        elif self.current_state == "in_lobby":
            self.ready_button.show()
            self.back_button.show()

    def update(self, time_delta: float, event_list: List[pygame.event.Event]):
        for event in event_list:
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.play_online_button:
                    return {"action": "connect_multiplayer", "name": self.name_input.get_text()}
                elif event.ui_element == self.play_local_button:
                    return {"action": "start_local"}
                elif event.ui_element == self.create_lobby_button:
                    return {"action": "create_lobby"}
                elif event.ui_element == self.refresh_button:
                    return {"action": "refresh_lobbies"}
                elif event.ui_element == self.back_button:
                    self.set_state("main_menu")
                elif event.ui_element == self.ready_button:
                    return {"action": "set_ready"}
                elif event.ui_element == self.start_game_button:
                    return {"action": "start_game"}
            elif event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
                if event.ui_element == self.lobby_selection:
                    selected_lobby = event.text
                    lobby_id = selected_lobby.split(":")[0]
                    return {"action": "join_lobby", "lobby_id": lobby_id}
            self.manager.process_events(event)

        self.manager.update(time_delta)
        return None

    def draw(self):
        self.screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 72)
        title = font.render("Shadow Echo", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(center=(self.screen.get_width() // 2, 100)))

        if self.current_state == "lobby_list":
            self.draw_lobby_list()
        elif self.current_state == "in_lobby":
            self.draw_lobby_info()

        self.manager.draw_ui(self.screen)

    def draw_lobby_list(self):
        font = pygame.font.Font(None, 36)
        text = font.render("Available Lobbies", True, (255, 255, 255))
        self.screen.blit(text, (300, 120))

    def draw_lobby_info(self):
        font = pygame.font.Font(None, 36)
        text = font.render("Lobby Info", True, (255, 255, 255))
        self.screen.blit(text, (50, 50))
        y = 150
        font_small = pygame.font.Font(None, 28)
        for i, player in enumerate(self.lobby_players):
            status = "Ready" if player.get("ready", False) else "Not Ready"
            player_text = font_small.render(f"{player['name']}: {status}", True, (255, 255, 255))
            self.screen.blit(player_text, (50, y + i * 30))

    def update_lobby_list(self, lobbies: List[dict]):
        items = [
            f"{lobby['id']}: {lobby['name']} ({lobby['players']}/{lobby['max_players']})"
            for lobby in lobbies
        ]
        self.lobby_selection.set_item_list(items)

    def update_lobby_info(self, players: List[dict]):
        self.lobby_players = players
