# Vietnamese Font Support in Shadow Echo

This document explains how Vietnamese character support was implemented in Shadow Echo.

## Overview

The application now uses Noto Sans fonts for proper Vietnamese character rendering. The implementation includes:

1. A custom font utility module to load and use Noto Sans fonts
2. Helper functions for proper text rendering
3. Updated UI components to use the new font utility

## Font Utility Implementation

The font utility is implemented in `/src/utils/font_utils.py` and provides:

- `get_font(size, bold=False, italic=False)` - Gets a font that supports Vietnamese characters
- `render_text(font, text, color, background=None)` - Renders text with proper encoding for Vietnamese

## Fonts Used

The following Noto Sans fonts are used for Vietnamese support:

- `NotoSans-Regular.ttf` - Regular font
- `NotoSans-Bold.ttf` - Bold font
- `NotoSans-Italic.ttf` - Italic font
- `NotoSans-BoldItalic.ttf` - Bold italic font

These fonts are stored in `/assets/sounds/fonts/` directory.

## Testing

To test Vietnamese text rendering, run the included test script:

```bash
cd /path/to/shadow_echo
source venv_new/bin/activate  # Activate the virtual environment
python test_vietnamese_font.py
```

This will display a window with various Vietnamese text samples to verify proper rendering.

## Implementation Details

The following files were modified to support Vietnamese text:

1. `/src/utils/font_utils.py` - New font utility module
2. `/src/core/game.py` - Updated to use font utility
3. `/src/interfaces/pygame_ui.py` - Updated to use font utility
4. `/src/interfaces/multiplayer_ui.py` - Updated to use font utility
5. `/src/core/card_selection_ui.py` - Updated to use font utility
6. `/main.py` - Updated to initialize and verify fonts

## Troubleshooting

If Vietnamese text is not displaying correctly:

1. Verify that Noto Sans fonts are present in the `/assets/sounds/fonts/` directory
2. Check the console for font loading errors
3. Ensure pygame is properly installed and up to date

## Future Improvements

Potential future improvements include:

1. Add additional font options for different UI components
2. Implement font caching for better performance
3. Add language selection feature with language-specific fonts

## References

- [Noto Sans Fonts](https://www.google.com/get/noto/)
- [Pygame Font Documentation](https://www.pygame.org/docs/ref/font.html)
- [Unicode in Python](https://docs.python.org/3/howto/unicode.html)