# Vietnamese Text Handling Guide

This guide explains how to properly handle Vietnamese text in Shadow Echo, including special character composition and rendering.

## Challenges with Vietnamese Text

Vietnamese uses Latin script with additional diacritical marks to represent tones and modified vowels. Common issues include:

1. **Composite Characters** - Vietnamese combines base characters with diacritical marks
2. **Multiple Accent Marks** - Characters can have both a modifier (ă, â, ê) and a tone mark (à, á, ả, ã, ạ)
3. **Unicode Decomposition** - Sometimes characters are represented as separate code points instead of combined characters

## Solution Implemented

The solution addresses these challenges through:

1. **Unicode Normalization** - Ensures composite characters are properly combined
2. **Proper Font Selection** - Using Noto Sans which has full Vietnamese character support
3. **Consistent Text Processing** - Normalizing all text input and display

## How to Use

### Rendering Text

Always use the `render_text` function to render Vietnamese text:

```python
from src.utils.font_utils import get_font, render_text

# Get a font with Vietnamese support
my_font = get_font(24, bold=True)

# Render text (will automatically normalize)
text_surface = render_text(my_font, "Xin chào thế giới!", (255, 255, 255))
```

### Processing Input

When processing user input, use the `normalize_vietnamese` function:

```python
from src.utils.font_utils import normalize_vietnamese

# User input
input_text = "tôi muôốn suưửa lôỗi font"

# Normalize before processing
normalized_text = normalize_vietnamese(input_text)
```

### Testing Vietnamese Text

To test Vietnamese text rendering:

1. Run the simplified test: `python test_vietnamese_font.py`
2. For interactive testing: `python test_vietnamese_input.py`

## Vietnamese Character Reference

### Vietnamese Special Characters

| Base Characters | Special Vowels | Consonants |
|-----------------|---------------|------------|
| a, e, i, o, u, y | ă, â, ê, ô, ơ, ư | đ |

### Tone Marks

Vietnamese has 5 tone marks that can be applied to vowels:

| Mark | Name | Example |
|------|------|---------|
| à | Huyền (falling) | à, è, ì |
| á | Sắc (rising) | á, é, í |
| ả | Hỏi (questioning) | ả, ẻ, ỉ |
| ã | Ngã (tumbling) | ã, ẽ, ĩ |
| ạ | Nặng (heavy) | ạ, ẹ, ị |

### Combined Characters Examples

| Base | With Tone Marks |
|------|-----------------|
| a | à, á, ả, ã, ạ |
| ă | ằ, ắ, ẳ, ẵ, ặ |
| â | ầ, ấ, ẩ, ẫ, ậ |
| e | è, é, ẻ, ẽ, ẹ |
| ê | ề, ế, ể, ễ, ệ |
| i | ì, í, ỉ, ĩ, ị |
| o | ò, ó, ỏ, õ, ọ |
| ô | ồ, ố, ổ, ỗ, ộ |
| ơ | ờ, ớ, ở, ỡ, ợ |
| u | ù, ú, ủ, ũ, ụ |
| ư | ừ, ứ, ử, ữ, ự |
| y | ỳ, ý, ỷ, ỹ, ỵ |

## Common Problem Cases

Some Vietnamese text input may come in decomposed forms, where the tone marks are separate characters. The normalization process handles this by converting to composed forms.

### Example:

- Decomposed: `tô + ̂ + ́i` (3 separate characters)
- Normalized: `tối` (1 combined character)

## Troubleshooting

If Vietnamese text still appears incorrectly:

1. **Check normalization** - Print character codes to verify proper normalization:
   ```python
   text = "tối"
   print([ord(c) for c in text])  # Should be [116, 7889, 105]
   ```

2. **Verify font** - Ensure Noto Sans fonts are being loaded correctly

3. **Input method** - Some IMEs might produce decomposed forms; our normalizer handles this

4. **Debug with test tools** - Use the included test scripts to debug specific cases