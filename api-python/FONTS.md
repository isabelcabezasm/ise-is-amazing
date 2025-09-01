# Multilingual Wordcloud Font Guide

## 🌍 Supported Scripts & Languages

The multilingual wordcloud system supports **10 different writing systems** with dedicated fonts for each:

| Script System  | Languages Supported                                                                                                          | Status    |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------- | --------- |
| **Latin**      | English, Spanish, French, German, Italian, Portuguese, Polish, Swedish, Czech, Slovak, Icelandic, Catalan, Azerbaijani, etc. | ✅ Active |
| **Hebrew**     | Hebrew, Yiddish                                                                                                              | ✅ Active |
| **Arabic**     | Arabic, Persian, Urdu                                                                                                        | ✅ Active |
| **Armenian**   | Eastern & Western Armenian                                                                                                   | ✅ Active |
| **Bengali**    | Bengali, Assamese                                                                                                            | ✅ Active |
| **Georgian**   | Georgian                                                                                                                     | ✅ Active |
| **Greek**      | Modern Greek, Ancient Greek                                                                                                  | ✅ Active |
| **Cyrillic**   | Russian, Bulgarian, Ukrainian, Belarusian, Macedonian, Serbian, Tatar, etc.                                                  | ✅ Active |
| **Devanagari** | Hindi, Nepali, Marathi, Sanskrit                                                                                             | ✅ Active |
| **CJK**        | Chinese (Simplified/Traditional), Japanese (Hiragana/Katakana/Kanji), Korean (Hangul)                                        | ✅ Active |

## 🚀 Automatic Installation (DevContainer)

All fonts are automatically installed when the DevContainer is built via the Dockerfile:

```dockerfile
RUN apt-get update && apt-get install -y \
    fonts-noto \          # Basic Noto fonts (Latin, Greek, Cyrillic)
    fonts-noto-cjk \      # Chinese, Japanese, Korean support
    fonts-noto-extra \    # Hebrew, Arabic, Devanagari, Armenian, Bengali, Georgian, etc.
    fonts-noto-color-emoji \
    && rm -rf /var/lib/apt/lists/*
```

## 📋 Complete Font Inventory

### Primary Script Fonts

| Script                   | Font File                        | File Size | Location                            |
| ------------------------ | -------------------------------- | --------- | ----------------------------------- |
| **Hebrew**               | `NotoSansHebrew-Regular.ttf`     | 26KB      | `/usr/share/fonts/truetype/noto/`   |
| **Arabic**               | `NotoSansArabic-Regular.ttf`     | 244KB     | `/usr/share/fonts/truetype/noto/`   |
| **Armenian**             | `NotoSansArmenian-Regular.ttf`   | 30KB      | `/usr/share/fonts/truetype/noto/`   |
| **Bengali**              | `NotoSansBengali-Regular.ttf`    | 201KB     | `/usr/share/fonts/truetype/noto/`   |
| **Georgian**             | `NotoSansGeorgian-Regular.ttf`   | 53KB      | `/usr/share/fonts/truetype/noto/`   |
| **Devanagari**           | `NotoSansDevanagari-Regular.ttf` | 229KB     | `/usr/share/fonts/truetype/noto/`   |
| **CJK**                  | `NotoSansCJK-Regular.ttc`        | 19MB      | `/usr/share/fonts/opentype/noto/`   |
| **Latin/Greek/Cyrillic** | `NotoSans-Regular.ttf`           | 512KB     | `/usr/share/fonts/truetype/noto/`   |
| **Fallback**             | `DejaVuSans.ttf`                 | 757KB     | `/usr/share/fonts/truetype/dejavu/` |

### Font Mapping Configuration

The system automatically selects the appropriate font based on Unicode character ranges:

```python
font_mapping = {
    'hebrew': '/usr/share/fonts/truetype/noto/NotoSansHebrew-Regular.ttf',
    'arabic': '/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf',
    'armenian': '/usr/share/fonts/truetype/noto/NotoSansArmenian-Regular.ttf',
    'bengali': '/usr/share/fonts/truetype/noto/NotoSansBengali-Regular.ttf',
    'georgian': '/usr/share/fonts/truetype/noto/NotoSansGeorgian-Regular.ttf',
    'cjk': '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
    'devanagari': '/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf',
    'greek': '/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf',
    'cyrillic': '/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf',
    'latin': '/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf',
    'fallback': '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
}
```

## 🎯 Unicode Range Detection

The system automatically detects script types using these Unicode ranges:

| Script         | Unicode Range                                                      | Detection Pattern                 |
| -------------- | ------------------------------------------------------------------ | --------------------------------- |
| **Hebrew**     | `U+0590-U+05FF`, `U+FB1D-U+FB4F`                                   | `[\u0590-\u05ff\ufb1d-\ufb4f]`    |
| **Arabic**     | `U+0600-U+06FF`, `U+0750-U+077F`, `U+08A0-U+08FF`, etc.            | `[\u0600-\u06ff\u0750-\u077f...]` |
| **Armenian**   | `U+0530-U+058F`, `U+FB13-U+FB17`                                   | `[\u0530-\u058f\ufb13-\ufb17]`    |
| **Bengali**    | `U+0980-U+09FF`                                                    | `[\u0980-\u09ff]`                 |
| **Georgian**   | `U+10A0-U+10FF`                                                    | `[\u10a0-\u10ff]`                 |
| **CJK**        | `U+4E00-U+9FFF`, `U+3040-U+309F`, `U+30A0-U+30FF`, `U+AC00-U+D7AF` | Multiple ranges                   |
| **Devanagari** | `U+0900-U+097F`                                                    | `[\u0900-\u097f]`                 |
| **Greek**      | `U+0370-U+03FF`, `U+1F00-U+1FFF`                                   | `[\u0370-\u03ff\u1f00-\u1fff]`    |
| **Cyrillic**   | `U+0400-U+04FF`                                                    | `[\u0400-\u04ff]`                 |
| **Latin**      | `A-Z`, `a-z` + Extensions                                          | `[a-zA-Z]` + diacritics           |

## 🔧 Manual Installation (Alternative)

If you need to install fonts manually outside of DevContainer:

```bash
# Update package list
sudo apt update

# Install all Noto font packages
sudo apt install -y fonts-noto fonts-noto-cjk fonts-noto-extra fonts-noto-color-emoji

# Refresh font cache
fc-cache -fv
```

## ✅ Font Verification

The DevContainer setup script automatically verifies font installation during container creation:

### Automatic Verification

```bash
# The setup.sh script checks each font:
echo "   - Hebrew: $(ls /usr/share/fonts/truetype/noto/NotoSansHebrew-Regular.ttf 2>/dev/null && echo "✅" || echo "❌")"
echo "   - Arabic: $(ls /usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf 2>/dev/null && echo "✅" || echo "❌")"
echo "   - Armenian: $(ls /usr/share/fonts/truetype/noto/NotoSansArmenian-Regular.ttf 2>/dev/null && echo "✅" || echo "❌")"
echo "   - Bengali: $(ls /usr/share/fonts/truetype/noto/NotoSansBengali-Regular.ttf 2>/dev/null && echo "✅" || echo "❌")"
echo "   - Georgian: $(ls /usr/share/fonts/truetype/noto/NotoSansGeorgian-Regular.ttf 2>/dev/null && echo "✅" || echo "❌")"
echo "   - CJK: $(ls /usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc 2>/dev/null && echo "✅" || echo "❌")"
echo "   - Devanagari: $(ls /usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf 2>/dev/null && echo "✅" || echo "❌")"
```

### Manual Verification Commands

```bash
# List all Noto fonts
find /usr/share/fonts -name "*Noto*" | head -20

# Check specific multilingual fonts
ls -la /usr/share/fonts/truetype/noto/NotoSans*.ttf
ls -la /usr/share/fonts/opentype/noto/NotoSansCJK*.ttc

# Check file sizes (should match the table above)
du -h /usr/share/fonts/truetype/noto/NotoSansHebrew-Regular.ttf  # ~26KB
du -h /usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf  # ~244KB
du -h /usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc     # ~19MB

# Test font rendering capability
fc-list | grep -i noto | wc -l  # Should show many Noto fonts available
```

## 🎨 Usage in Code

### Basic Usage

The `MultilingualWordCloud` class automatically selects appropriate fonts based on detected text scripts:

```python
from multilingual_wordcloud_sentences import MultilingualWordCloud

# Create wordcloud with automatic multilingual font selection
wc = MultilingualWordCloud()
wc.generate("Hello שלום مرحبا 你好 Հայերեն বাংলা საქართული Ελληνικά Русский हिन्दी")
wc.to_file('multilingual_wordcloud.png')
```

### Advanced Configuration

```python
# Create with custom font mapping (if needed)
custom_font_mapping = {
    'hebrew': '/path/to/custom/hebrew/font.ttf',
    'arabic': '/path/to/custom/arabic/font.ttf',
    # ... other mappings
}

wc = MultilingualWordCloud(font_mapping=custom_font_mapping)
```

### Example Languages by Script

```python
test_text = {
    "Hello World": 1,                    # Latin
    "שלום עולם": 1,                      # Hebrew
    "مرحبا بالعالم": 1,                   # Arabic
    "Բարև աշխարհ": 1,                    # Armenian
    "নমস্কার বিশ্ব": 1,                    # Bengali
    "გამარჯობა მსოფლიო": 1,               # Georgian
    "你好世界": 1,                        # Chinese
    "こんにちは世界": 1,                     # Japanese
    "안녕하세요 세계": 1,                    # Korean
    "Γεια σου κόσμε": 1,                 # Greek
    "Привет мир": 1,                     # Cyrillic/Russian
    "नमस्ते संसार": 1,                     # Devanagari/Hindi
}

wc = MultilingualWordCloud()
wc.generate_from_frequencies(test_text)
wc.to_file('all_scripts_wordcloud.png')
```

## 🔍 Technical Details

### Font Loading Process

1. **Script Detection**: Text is analyzed using Unicode ranges to determine primary script
2. **Font Selection**: Appropriate font is selected from the mapping
3. **Font Loading**: PIL loads the specific font file for rendering
4. **Fallback System**: If primary font fails, system falls back to DejaVuSans.ttf

### Performance Notes

- **CJK Font**: Large file size (19MB) but supports thousands of characters
- **Script-Specific Fonts**: Optimized for their respective writing systems
- **Caching**: Fonts are loaded once per session and reused
- **Memory Usage**: ~21MB total for all fonts when loaded

### Troubleshooting

```bash
# If fonts appear as squares, check installation:
python3 -c "
import os
fonts_to_check = [
    '/usr/share/fonts/truetype/noto/NotoSansHebrew-Regular.ttf',
    '/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf',
    '/usr/share/fonts/truetype/noto/NotoSansArmenian-Regular.ttf',
    '/usr/share/fonts/truetype/noto/NotoSansBengali-Regular.ttf',
    '/usr/share/fonts/truetype/noto/NotoSansGeorgian-Regular.ttf',
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
]
for font in fonts_to_check:
    status = '✅' if os.path.exists(font) else '❌'
    print(f'{status} {font}')
"
```

The fonts are automatically configured in `_get_default_font_mapping()` and will be available immediately when the container is built.
