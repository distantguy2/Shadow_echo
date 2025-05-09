#!/usr/bin/env python3
"""
Test script for Vietnamese text rendering in pygame
"""
import pygame
import sys
from src.utils.font_utils import get_font, render_text

# Initialize pygame
pygame.init()

# Set up the display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Vietnamese Font Test")

# Background color
bg_color = (30, 30, 50)

# Text samples - Vietnamese phrases with diacritical marks
vietnamese_text = [
    "Xin chào thế giới!",  # Hello world
    "Tôi có thể viết tiếng Việt",  # I can write Vietnamese
    "Các ký tự tiếng Việt: ă, â, đ, ê, ô, ơ, ư",  # Vietnamese characters
    "Dấu thanh: à, á, ả, ã, ạ, ằ, ắ, ẳ, ẵ, ặ",  # Tone marks
    "Ngôn ngữ và văn hoá Việt Nam",  # Vietnamese language and culture
    "Tôi muốn sửa lỗi font trong Claude",  # I want to fix the font issue in Claude
    "Chữ tiếng Việt hiển thị đúng không?",  # Is Vietnamese text displaying correctly?
]

def main():
    """Main function to run the test"""
    clock = pygame.time.Clock()
    
    # Load fonts at different sizes
    fonts = {
        "large": get_font(32, bold=True),
        "medium": get_font(24),
        "small": get_font(18),
        "tiny": get_font(14, italic=True)
    }
    
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Clear the screen
        screen.fill(bg_color)
        
        # Draw title
        title = render_text(fonts["large"], "Vietnamese Font Test", (255, 255, 255))
        screen.blit(title, (width // 2 - title.get_width() // 2, 30))
        
        # Draw subtitle
        subtitle = render_text(fonts["medium"], "Using Noto Sans for proper Vietnamese character display", (200, 200, 255))
        screen.blit(subtitle, (width // 2 - subtitle.get_width() // 2, 80))
        
        # Draw Vietnamese text samples
        y_pos = 150
        for i, text in enumerate(vietnamese_text):
            # Alternate between different font sizes
            font = fonts["medium"] if i % 2 == 0 else fonts["small"]
            
            # Render the text
            text_surface = render_text(font, text, (255, 255, 200))
            screen.blit(text_surface, (50, y_pos))
            y_pos += 50
        
        # Draw instructions
        instructions = render_text(fonts["tiny"], "Press ESC to exit", (150, 150, 150))
        screen.blit(instructions, (width // 2 - instructions.get_width() // 2, height - 40))
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(60)
    
    # Quit pygame
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()