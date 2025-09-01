# Multilingual Word Cloud API

## 🌍 Overview

The multilingual word cloud API generates beautiful word cloud images from text in **150+ languages and scripts** including Arabic, Chinese, Japanese, Korean, Hindi, Thai, Hebrew, and many more. Using the Python `wordcloud` library with comprehensive Noto font support (2,380+ fonts), these endpoints return high-quality PNG images that correctly display text in any language or script.

### ✨ Key Features

- **🌐 Universal Language Support**: 150+ languages including RTL scripts (Arabic, Hebrew), CJK (Chinese, Japanese, Korean), and Indic scripts
- **🎨 2,380+ Fonts**: Comprehensive Noto font collection ensures proper character rendering
- **🎯 Production Ready**: Currently deployed on Azure Container Apps with global availability
- **⚡ High Performance**: Optimized font loading and memory management for production workloads

## 🚀 Endpoints

### 1. POST /api/cloud - Custom Multilingual Word Clouds

Generate word clouds from custom sentences in any supported language.

#### 📝 Request Body

```json
{
  "sentences": ["你很棒", "あなたはすばらしい", "أنت مذهل", "You are amazing"],
  "width": 800,
  "height": 400,
  "background_color": "white",
  "colormap": "viridis"
}
```

#### 🔧 Parameters

- `sentences` (required): Array of strings - Text in any language or mixed languages
- `width` (optional): Integer - Width of the generated image (default: 800)
- `height` (optional): Integer - Height of the generated image (default: 400)
- `background_color` (optional): String - Background color (default: "white")
- `colormap` (optional): String - Matplotlib colormap name (default: "viridis")

#### 📤 Response

Returns a PNG image file with content-type `image/png`.

#### 💡 Example Usage

```bash
# Production API - Multilingual Word Cloud
curl -X POST "https://youareamazing-api.ambitiousmushroom-0229ef63.westus2.azurecontainerapps.io/api/cloud" \
  -H "Content-Type: application/json" \
  -d '{
    "sentences": ["你很棒", "あなたはすばらしい", "أنت مذهل", "आप अद्भुत हैं", "You are amazing"],
    "width": 1200,
    "height": 600,
    "background_color": "navy",
    "colormap": "rainbow"
  }' \
  --output multilingual_wordcloud.png

# Local Development
curl -X POST "http://localhost:8000/api/cloud" \
  -H "Content-Type: application/json" \
  -d '{
    "sentences": ["Eres increíble", "Tu es incroyable", "Du bist erstaunlich"],
    "width": 800,
    "height": 400
  }' \
  --output european_languages.png
```

### 2. GET /api/cloud/amazing - Amazing Items Word Cloud

Generate word clouds from all existing amazing items in the system (supports multilingual items).

#### 🎛️ Query Parameters

- `width` (optional): Integer - Width of the generated image (default: 800)
- `height` (optional): Integer - Height of the generated image (default: 400)
- `background_color` (optional): String - Background color (default: "white")
- `colormap` (optional): String - Matplotlib colormap name (default: "viridis")

#### 📤 Response

Returns a PNG image file with content-type `image/png`.

#### 💡 Example Usage

```bash
# Production API
curl -X GET "https://youareamazing-api.ambitiousmushroom-0229ef63.westus2.azurecontainerapps.io/api/cloud/amazing?width=1000&height=500&background_color=darkblue&colormap=plasma" \
  --output amazing_items_wordcloud.png

# Local Development
curl -X GET "http://localhost:8000/api/cloud/amazing?width=800&height=400&background_color=navy&colormap=cool" \
  --output amazing_wordcloud.png
```

## 🌍 Multilingual Language Support

### 📝 Supported Writing Systems

Our wordcloud system supports **150+ languages** across all major writing systems:

#### Latin Scripts

- **Western European**: English, Spanish, French, German, Italian, Portuguese, Dutch, etc.
- **Eastern European**: Polish, Czech, Slovak, Hungarian, Romanian, Croatian, etc.
- **Extended Latin**: Vietnamese, Turkish, Azerbaijani, Estonian, Latvian, Lithuanian

#### Cyrillic Scripts

- **Slavic Languages**: Russian, Ukrainian, Bulgarian, Serbian, Macedonian, Belarusian
- **Other Cyrillic**: Mongolian, Kazakh, Kyrgyz, Uzbek, Tajik

#### East Asian Scripts

- **Chinese**: Simplified and Traditional Chinese (Han characters)
- **Japanese**: Hiragana, Katakana, Kanji (mixed scripts)
- **Korean**: Hangul syllables

#### South Asian Scripts

- **Devanagari**: Hindi, Marathi, Nepali, Sanskrit
- **Bengali**: Bengali, Assamese
- **Tamil**: Tamil script
- **Other Indic**: Telugu, Kannada, Malayalam, Gujarati, Punjabi (Gurmukhi), Oriya, Sinhala

#### Middle Eastern Scripts

- **Arabic**: Arabic, Persian, Urdu, Kurdish, Pashto (RTL support)
- **Hebrew**: Hebrew, Yiddish (RTL support)

#### Southeast Asian Scripts

- **Thai**: Thai script
- **Myanmar**: Burmese script
- **Khmer**: Cambodian script
- **Lao**: Lao script

#### African Scripts

- **Ethiopic**: Amharic, Tigrinya
- **Other African**: Swahili (Latin), Yoruba (Latin), etc.

### 🔤 Font Coverage

Our system includes **2,380+ Noto fonts** providing comprehensive coverage:

- **Noto Sans**: Modern, clean sans-serif fonts for all scripts
- **Noto Serif**: Traditional serif fonts where appropriate
- **Noto CJK**: Specialized fonts for Chinese, Japanese, Korean
- **Noto Emoji**: Emoji and symbol support
- **Script-Specific Fonts**: Optimized fonts for complex scripts (Arabic, Devanagari, etc.)

### 🎨 Mixed Language Examples

```json
{
  "sentences": [
    "Hello World", // English (Latin)
    "你好世界", // Chinese (Han)
    "こんにちは世界", // Japanese (Hiragana + Kanji)
    "مرحبا بالعالم", // Arabic (RTL)
    "नमस्ते दुनिया", // Hindi (Devanagari)
    "Привет мир", // Russian (Cyrillic)
    "안녕하세요 세계", // Korean (Hangul)
    "שלום עולם", // Hebrew (RTL)
    "สวัสดีโลก", // Thai
    "Γεια σας κόσμε" // Greek
  ]
}
```

## 🎨 Customization Options

### Color Maps

The following matplotlib colormaps are supported:

- `viridis` (default) - Blue to yellow gradient
- `plasma` - Purple to yellow gradient
- `rainbow` - Full spectrum colors
- `cool` - Cyan to magenta
- `hot` - Black to red to yellow
- `spring` - Magenta to yellow
- `summer` - Green to yellow
- `autumn` - Red to yellow
- `winter` - Blue to green

### Background Colors

Common background colors:

- `white` (default)
- `black`
- `navy`
- `darkblue`
- `darkgreen`
- `maroon`
- `transparent` - Transparent background

### 400 Bad Request

- Empty sentences array
- Invalid parameters
- No amazing items found (for `/api/cloud/amazing`)

### 500 Internal Server Error

- Word cloud generation failure
- Server processing errors

## ⚠️ Error Handling

### 400 Bad Request

- Empty sentences array
- Invalid parameters
- No amazing items found (for `/api/cloud/amazing`)
- Unsupported colormap or background color

### 500 Internal Server Error

- Word cloud generation failure
- Font loading errors
- Server processing errors

## 🌐 Frontend Integration

The multilingual word cloud functionality is integrated into the frontend at:

**🔗 Production**: https://white-cliff-0303bcc1e.2.azurestaticapps.net/cloud

### Features

1. **🌍 Multilingual Input**: Add sentences in any supported language
2. **✨ Amazing Items Integration**: Generate word clouds from existing multilingual items
3. **🎨 Customization Options**: Configure dimensions, colors, and color maps
4. **👀 Real-time Preview**: View generated word clouds immediately
5. **💾 Download Functionality**: Download word cloud images as PNG files
6. **🔤 Script Detection**: Automatic font selection based on detected scripts

## 🔧 Dependencies

The multilingual word cloud functionality requires:

### Python Packages

- `wordcloud>=1.9.0` - Core word cloud generation with multilingual support
- `pillow>=10.0.0` - Advanced image processing and font handling
- `numpy` - Mathematical operations (auto-installed with wordcloud)
- `matplotlib` - Color maps and visualization (auto-installed with wordcloud)

### Font System

- **2,380+ Noto Fonts**: Complete Unicode coverage for all supported scripts
- **Font Management**: Automated font selection based on text script detection
- **Memory Optimization**: Efficient font loading and caching for production environments

## ⚙️ Technical Details

### 🌐 Multilingual Word Cloud Configuration

- **Max Words**: 100 (maximum number of words displayed)
- **Relative Scaling**: 0.5 (balance between word frequency and font size)
- **Random State**: 42 (ensures reproducible results)
- **Image Format**: PNG with transparency support
- **Font Selection**: Automatic script-based font selection from 2,380+ Noto fonts
- **Unicode Support**: Full Unicode 15.0 compliance
- **RTL Support**: Proper handling of right-to-left scripts (Arabic, Hebrew)

### 🚀 Performance Considerations

- **Font Loading**: Optimized font caching reduces generation time for multilingual content
- **Script Detection**: Automatic script detection minimizes font loading overhead
- **Memory Management**: Efficient handling of large font collections in production
- **Generation Time**: Complex multilingual text may require additional processing time
- **Container Resources**: Production deployment includes all fonts in container image

### 💾 Memory Management

- **Streaming Response**: Images streamed directly to client (no server storage)
- **Blob URLs**: Frontend creates temporary URLs for display
- **Font Caching**: Intelligent font caching for frequently used scripts
- **Automatic Cleanup**: Memory automatically cleaned up after response
- **Production Optimization**: Container memory optimized for concurrent multilingual requests

## 🔗 Example Integrations

### 🌐 JavaScript/TypeScript Frontend

```javascript
// Generate multilingual word cloud
const generateMultilingualWordCloud = async (sentences) => {
  const response = await fetch(
    "https://youareamazing-api.ambitiousmushroom-0229ef63.westus2.azurecontainerapps.io/api/cloud",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sentences,
        width: 1200,
        height: 600,
        background_color: "navy",
        colormap: "rainbow",
      }),
    }
  );

  if (response.ok) {
    const blob = await response.blob();
    const imageUrl = URL.createObjectURL(blob);
    // Use imageUrl to display the multilingual word cloud
    return imageUrl;
  }
  throw new Error("Failed to generate word cloud");
};

// Example usage with mixed languages
const multilingualSentences = [
  "Hello World", // English
  "你好世界", // Chinese
  "こんにちは世界", // Japanese
  "مرحبا بالعالم", // Arabic
  "नमस्ते दुनिया", // Hindi
];

generateMultilingualWordCloud(multilingualSentences);
```

### 🐍 Python Client

```python
import requests

def generate_multilingual_word_cloud(sentences, output_filename="multilingual_wordcloud.png"):
    """Generate a multilingual word cloud using the production API."""

    response = requests.post(
        'https://youareamazing-api.ambitiousmushroom-0229ef63.westus2.azurecontainerapps.io/api/cloud',
        json={
            'sentences': sentences,
            'width': 1200,
            'height': 600,
            'background_color': 'darkblue',
            'colormap': 'plasma'
        },
        timeout=30  # Allow extra time for multilingual processing
    )

    if response.status_code == 200:
        with open(output_filename, 'wb') as f:
            f.write(response.content)
        print(f"Multilingual word cloud saved as {output_filename}")
        return True
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return False

# Example usage
multilingual_sentences = [
    "You are amazing",       # English
    "Eres increíble",       # Spanish
    "Tu es incroyable",     # French
    "Du bist erstaunlich",  # German
    "あなたはすばらしい",      # Japanese
    "你很棒",               # Chinese
    "أنت مذهل",            # Arabic
    "आप अद्भुत हैं",        # Hindi
]

generate_multilingual_word_cloud(multilingual_sentences, "amazing_multilingual.png")
```

### 🖥️ cURL Examples

```bash
# Mixed European languages
curl -X POST "https://youareamazing-api.ambitiousmushroom-0229ef63.westus2.azurecontainerapps.io/api/cloud" \
  -H "Content-Type: application/json" \
  -d '{
    "sentences": ["Hello", "Bonjour", "Hola", "Hallo", "Ciao", "Привет"],
    "width": 800,
    "height": 400,
    "colormap": "viridis"
  }' \
  --output european_multilingual.png

# East Asian languages
curl -X POST "https://youareamazing-api.ambitiousmushroom-0229ef63.westus2.azurecontainerapps.io/api/cloud" \
  -H "Content-Type: application/json" \
  -d '{
    "sentences": ["你好", "こんにちは", "안녕하세요", "Xin chào"],
    "width": 1000,
    "height": 500,
    "background_color": "black",
    "colormap": "rainbow"
  }' \
  --output east_asian_languages.png

# Middle Eastern RTL languages
curl -X POST "https://youareamazing-api.ambitiousmushroom-0229ef63.westus2.azurecontainerapps.io/api/cloud" \
  -H "Content-Type: application/json" \
  -d '{
    "sentences": ["مرحبا", "שלום", "سلام", "Merhaba"],
    "width": 800,
    "height": 600,
    "background_color": "navy",
    "colormap": "cool"
  }' \
  --output rtl_languages.png
```

## 🧪 Testing

### Production API Testing

Test the multilingual functionality with the live production API:

```bash
# Test multilingual word cloud generation
curl -X POST "https://youareamazing-api.ambitiousmushroom-0229ef63.westus2.azurecontainerapps.io/api/cloud" \
  -H "Content-Type: application/json" \
  -d '{
    "sentences": ["Test", "测试", "テスト", "اختبار", "परीक्षण"],
    "width": 800,
    "height": 400
  }' \
  --output production_test.png

# Test amazing items endpoint
curl -X GET "https://youareamazing-api.ambitiousmushroom-0229ef63.westus2.azurecontainerapps.io/api/cloud/amazing" \
  --output production_amazing.png
```

### Local Development Testing

For local testing and development:

```bash
# Run local test script (requires local FastAPI server)
cd /workspaces/ui-prototyper/api-python
python test_wordcloud_diagnostic.py

# Test multilingual font coverage
python test_multilingual_wordcloud.py
```

### 🔍 Available Test Scripts

1. **`test_wordcloud_diagnostic.py`** - Tests basic wordcloud functionality and font loading
2. **`test_multilingual_wordcloud.py`** - Tests multilingual text processing and font selection
3. **`test_font_fix.py`** - Validates font installation and Unicode coverage

### 📊 Test Coverage

The test suite validates:

- ✅ Multilingual text processing (150+ languages)
- ✅ Font loading and selection (2,380+ fonts)
- ✅ Image generation and formatting
- ✅ API endpoint responses
- ✅ Error handling scenarios
- ✅ Memory management and cleanup
