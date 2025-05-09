"""
Font utilities for supporting multilingual text rendering including Vietnamese
"""
import os
import unicodedata
import pygame
from pathlib import Path

# Find the project root directory
project_root = Path(__file__).resolve().parent.parent.parent

# Font paths
FONT_DIR = project_root / "assets" / "sounds" / "fonts"
NOTO_REGULAR = FONT_DIR / "NotoSans-Regular.ttf"
NOTO_BOLD = FONT_DIR / "NotoSans-Bold.ttf"
NOTO_ITALIC = FONT_DIR / "NotoSans-Italic.ttf"
NOTO_BOLD_ITALIC = FONT_DIR / "NotoSans-BoldItalic.ttf"

# Vietnamese character handling
def normalize_vietnamese(text):
    """
    Normalize Vietnamese text to ensure proper rendering

    This normalizes composite characters to ensure proper display
    of Vietnamese diacritical marks

    Args:
        text (str): Text that may contain Vietnamese characters

    Returns:
        str: Normalized text
    """
    # Normalize to composed form (NFC) for Vietnamese
    # This ensures combining diacritical marks are properly combined with base characters
    return unicodedata.normalize('NFC', text)

def get_font(size, bold=False, italic=False):
    """
    Get a font that supports Vietnamese characters

    Args:
        size (int): Font size
        bold (bool): Whether to use bold font
        italic (bool): Whether to use italic font

    Returns:
        pygame.font.Font: Font object that supports Vietnamese
    """
    # Select the appropriate font file
    if bold and italic:
        font_path = NOTO_BOLD_ITALIC
    elif bold:
        font_path = NOTO_BOLD
    elif italic:
        font_path = NOTO_ITALIC
    else:
        font_path = NOTO_REGULAR

    # Verify font file exists
    if not os.path.exists(font_path):
        # Fall back to system font if font file not found
        print(f"Warning: Font file not found: {font_path}")
        return pygame.font.SysFont("Arial", size, bold=bold, italic=italic)

    try:
        # Load font with unicode=True to ensure proper handling of Unicode characters
        return pygame.font.Font(str(font_path), size)
    except Exception as e:
        print(f"Error loading font: {e}")
        # Fall back to system font
        return pygame.font.SysFont("Arial", size, bold=bold, italic=italic)

def render_text(font, text, color=(255, 255, 255), background=None):
    """
    Render text with proper encoding for Vietnamese

    Args:
        font (pygame.font.Font): Font to use
        text (str): Text to render (can include Vietnamese)
        color (tuple): RGB color tuple
        background (tuple): RGB background color tuple or None for transparent

    Returns:
        pygame.Surface: Rendered text surface
    """
    try:
        # Normalize the text before rendering to ensure proper display
        normalized_text = normalize_vietnamese(text)
        return font.render(normalized_text, True, color, background)
    except UnicodeError:
        # Handle Unicode-specific errors
        print(f"Unicode error rendering: {text}")
        try:
            # Try rendering with NFKC normalization which may help with some cases
            normalized_text = unicodedata.normalize('NFKC', text)
            return font.render(normalized_text, True, color, background)
        except Exception as e:
            print(f"Failed second attempt to render text: {e}")
            fallback_font = pygame.font.SysFont("Arial", font.get_height())
            return fallback_font.render(text, True, color, background)
    except Exception as e:
        print(f"Error rendering text: {e}")
        # Try rendering with default font if there's an error
        fallback_font = pygame.font.SysFont("Arial", font.get_height())
        return fallback_font.render(text, True, color, background)

# Input text handling for Vietnamese
def process_vietnamese_input(text, new_char):
    """
    Process Vietnamese text input with proper diacritical mark handling

    Args:
        text (str): Current text buffer
        new_char (str): New character to add

    Returns:
        str: Updated text with Vietnamese characters properly handled
    """
    # Normalize the combined text
    combined = text + new_char
    return normalize_vietnamese(combined)