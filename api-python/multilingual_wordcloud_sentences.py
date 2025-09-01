#!/usr/bin/env python3
"""
Multilingual WordCloud implementation that supports different fonts for different scripts
Modified to work with complete sentences instead of individual words
"""

import re
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from wordcloud import WordCloud
from operator import itemgetter
from random import Random
from collections import Counter


class MultilingualWordCloud(WordCloud):
    """
    Extended WordCloud that supports multiple fonts for different scripts
    and processes complete sentences instead of individual words
    """

    def __init__(self, *args, **kwargs):
        # Extract custom font mapping if provided
        self.font_mapping = kwargs.pop('font_mapping', None)

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Default font mapping if none provided
        if self.font_mapping is None:
            self.font_mapping = self._get_default_font_mapping()

        # Compile script detection patterns
        self.script_patterns = {
            'hebrew': re.compile(r'[\u0590-\u05ff\ufb1d-\ufb4f]'),
            'arabic': re.compile(r'[\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff\ufb50-\ufdff\ufe70-\ufeff]'),
            'armenian': re.compile(r'[\u0530-\u058f\ufb13-\ufb17]'),
            'bengali': re.compile(r'[\u0980-\u09ff]'),
            'georgian': re.compile(r'[\u10a0-\u10ff]'),
            'cjk': re.compile(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]'),
            'devanagari': re.compile(r'[\u0900-\u097f]'),
            'latin': re.compile(r'[a-zA-Z]'),
            'greek': re.compile(r'[\u0370-\u03ff\u1f00-\u1fff]'),
            'cyrillic': re.compile(r'[\u0400-\u04ff]')
        }

    def _get_default_font_mapping(self):
        """
        Get default font paths for different scripts

        These fonts are automatically installed in the devcontainer via:
        - fonts-noto: Basic Noto fonts including NotoSans-Regular.ttf
        - fonts-noto-cjk: CJK (Chinese, Japanese, Korean) support
        - fonts-noto-extra: Additional language support (Hebrew, Arabic, Devanagari, Armenian, Bengali, Georgian, etc.)
        """
        return {
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

    def _multilingual_process_text(self, text):
        """
        Process text to extract sentences while preserving different scripts
        """
        # Clean the text
        text = text.strip()
        if not text:
            return {}

        # For multilingual text, prioritize line-based splitting first
        # as different languages may not use the same punctuation

        # Step 1: Split by line breaks and clean up
        potential_sentences = []
        for line in text.split('\n'):
            line = line.strip()
            if line and len(line) > 2:  # Allow shorter sentences for different languages
                potential_sentences.append(line)

        print(f"DEBUG: Split by lines: {len(potential_sentences)} sentences")
        for i, sent in enumerate(potential_sentences):
            print(f"  {i+1}: '{sent}'")

        # If we got good line-based splits, use them
        if len(potential_sentences) > 1:
            sentences = potential_sentences
        else:
            # Step 2: Fall back to punctuation-based splitting
            sentence_pattern = r'[.!?。！？।॥؟‽؍⸮⁇⁈⁉…]+\s*'
            sentences = re.split(sentence_pattern, text)

            # Filter out empty sentences and very short ones
            sentences = [s.strip()
                         for s in sentences if s.strip() and len(s.strip()) > 2]
            print(
                f"DEBUG: Punctuation split resulted in: {len(sentences)} sentences")

            # Step 3: If still no good splits, try double spaces or semantic chunking
            if len(sentences) <= 1:
                # Try splitting by double spaces or long sequences of spaces
                potential_sentences = [s.strip() for s in re.split(
                    r'\s{2,}', text) if s.strip() and len(s.strip()) > 2]
                if len(potential_sentences) > 1:
                    sentences = potential_sentences
                    print(
                        f"DEBUG: Double space split resulted in: {len(sentences)} sentences")
                else:
                    # Final fallback: semantic chunking for very long text
                    if len(text) > 80:
                        chunks = []
                        words = text.split()
                        current_chunk = ""
                        for word in words:
                            if len(current_chunk + " " + word) > 80 and current_chunk:
                                chunks.append(current_chunk.strip())
                                current_chunk = word
                            else:
                                current_chunk += (" " +
                                                  word if current_chunk else word)
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        sentences = chunks
                        print(
                            f"DEBUG: Semantic chunking resulted in: {len(sentences)} sentences")
                    else:
                        sentences = [text]
                        print(f"DEBUG: Using entire text as single sentence")

        # Count frequencies of sentences (treating each unique sentence as having frequency 1)
        sentence_counts = Counter(sentences)

        print(f"DEBUG: Final sentence frequencies:")
        for sentence, count in sentence_counts.items():
            print(f"  '{sentence[:50]}...' -> {count}")

        return sentence_counts

    def generate(self, text, max_font_size=None):
        """
        Generate wordcloud from text with proper multilingual sentence processing
        """
        print(
            f"DEBUG: Processing multilingual text for sentences: {text[:100]}...")

        # Process text using multilingual-aware method to get sentences
        frequencies = self._multilingual_process_text(text)

        if not frequencies:
            raise ValueError(
                "No sentences found in text after multilingual processing")

        # Use generate_from_frequencies directly to bypass original text processing
        return self.generate_from_frequencies(frequencies, max_font_size)

    def detect_script(self, text):
        """Detect the primary script of text"""
        if re.search(r'[\u0590-\u05FF]', text):
            return 'hebrew'
        elif re.search(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]', text):
            return 'arabic'  # Includes Urdu
        elif re.search(r'[\u0530-\u058F\uFB13-\uFB17]', text):
            return 'armenian'  # Armenian script
        elif re.search(r'[\u0980-\u09FF]', text):
            return 'bengali'  # Bengali script
        elif re.search(r'[\u10A0-\u10FF]', text):
            return 'georgian'  # Georgian script
        elif re.search(r'[\u4E00-\u9FFF\u3400-\u4DBF\uF900-\uFAFF]', text):
            return 'cjk'  # Changed from 'chinese' to 'cjk'
        elif re.search(r'[\u3040-\u309F\u30A0-\u30FF]', text):
            return 'cjk'  # Changed from 'japanese' to 'cjk'
        elif re.search(r'[\uAC00-\uD7AF\u1100-\u11FF\u3130-\u318F]', text):
            return 'cjk'  # Changed from 'korean' to 'cjk'
        elif re.search(r'[\u0900-\u097F]', text):
            return 'devanagari'  # Hindi
        elif re.search(r'[\u0370-\u03FF]', text):
            return 'greek'
        elif re.search(r'[\u0400-\u04FF]', text):
            return 'cyrillic'
        else:
            return 'latin'

    def get_font_for_word(self, sentence):
        """Get the appropriate font path for a sentence based on its primary script"""
        script = self.detect_script(sentence)

        # Get font path from mapping
        font_path = self.font_mapping.get(script)

        # Check if font exists, fallback if not
        if font_path and os.path.exists(font_path):
            return font_path

        # Try fallback font
        fallback_path = self.font_mapping.get('fallback')
        if fallback_path and os.path.exists(fallback_path):
            return fallback_path

        # Ultimate fallback to original font_path
        return self.font_path

    def generate_from_frequencies(self, frequencies, max_font_size=None):
        """
        Modified generate_from_frequencies that uses different fonts per sentence
        """
        print(
            f"DEBUG: MultilingualWordCloud generating from {len(frequencies)} frequencies")

        # Make sure frequencies are sorted and normalized
        frequencies = sorted(frequencies.items(),
                             key=itemgetter(1), reverse=True)
        if len(frequencies) <= 0:
            raise ValueError("We need at least 1 sentence to plot a word cloud, "
                             "got %d." % len(frequencies))
        frequencies = frequencies[:self.max_words]

        # Largest entry will be 1
        max_frequency = float(frequencies[0][1])
        frequencies = [(sentence, freq / max_frequency)
                       for sentence, freq in frequencies]

        if self.random_state is not None:
            random_state = self.random_state
        else:
            random_state = Random()

        # Set up canvas
        if self.mask is not None:
            # Use the mask to get dimensions and boolean mask
            width = self.mask.shape[1]
            height = self.mask.shape[0]
            # Convert mask to boolean - areas that are not white (255) are masked out
            boolean_mask = self.mask != 255
            print(
                f"DEBUG: Using mask dimensions - Width: {width}, Height: {height}")
        else:
            boolean_mask = None
            height, width = self.height, self.width
            print(
                f"DEBUG: Using default dimensions - Width: {width}, Height: {height}")

        print(f"DEBUG: Canvas size set to {width}x{height}")

        # Import occupancy map
        from wordcloud.wordcloud import IntegralOccupancyMap
        occupancy = IntegralOccupancyMap(height, width, boolean_mask)

        # Create image
        img_grey = Image.new("L", (width, height))
        print(
            f"DEBUG: Created grayscale image with size: {img_grey.size} (width x height)")
        draw = ImageDraw.Draw(img_grey)
        img_array = np.asarray(img_grey)
        print(f"DEBUG: Image array shape: {img_array.shape}")
        font_sizes, positions, orientations, colors, font_paths = [], [], [], [], []

        last_freq = 1.

        if max_font_size is None:
            # Figure out good font size for sentences - increased for bigger text
            if len(frequencies) == 1:
                # Single sentence - make it reasonably sized, bigger than before
                sentence = frequencies[0][0]
                sentence_length = len(sentence)
                font_size = max(
                    30, min(self.height // 6, self.width // max(8, sentence_length // 6)))
            else:
                # Multiple sentences - start bigger than before
                first_sentence = frequencies[0][0]
                first_font_path = self.get_font_for_word(first_sentence)
                temp_font = ImageFont.truetype(
                    first_font_path, 36)  # Test with larger size
                bbox = draw.textbbox((0, 0), first_sentence, font=temp_font)
                # Calculate based on fitting sentences reasonably - bigger base size
                font_size = max(
                    25, min(self.height // 8, self.width // max(6, len(first_sentence) // 5)))
        else:
            font_size = max_font_size

        print(f"DEBUG: Starting with font_size: {font_size}")

        # Process each sentence with its appropriate font
        for sentence, freq in frequencies:
            # Skip if frequency is too low
            if freq == 0:
                continue

            # Get font for this specific sentence
            sentence_font_path = self.get_font_for_word(sentence)
            script = self.detect_script(sentence)
            print(
                f"DEBUG: Sentence '{sentence[:30]}...' -> script: {script}, font: {os.path.basename(sentence_font_path)}")

            # Calculate font size for this sentence - keep bigger sizes
            sentence_length = len(sentence)
            # Increased multiplier
            base_font_size = max(
                int(freq * font_size * 1.5), self.min_font_size)

            # Adjust font size based on sentence length - less aggressive reduction for bigger text
            if sentence_length > 60:
                current_font_size = max(
                    # Less reduction
                    int(base_font_size * 0.6), self.min_font_size)
            elif sentence_length > 35:
                current_font_size = max(
                    # Less reduction
                    int(base_font_size * 0.8), self.min_font_size)
            else:
                current_font_size = base_font_size

            # Try different orientations
            orientation = None
            tried_other_orientation = False

            while True:
                if current_font_size < self.min_font_size:
                    break

                try:
                    # Load font for this specific sentence
                    font = ImageFont.truetype(
                        sentence_font_path, current_font_size)
                    transposed_font = ImageFont.TransposedFont(
                        font, orientation=orientation)

                    # Get size of resulting text
                    box_size = draw.textbbox(
                        (0, 0), sentence, font=transposed_font, anchor="lt")

                    # Find possible places using integral image
                    result = occupancy.sample_position(
                        box_size[3] + self.margin,
                        box_size[2] + self.margin,
                        random_state
                    )

                    if result is not None:
                        # Found a place!
                        break

                except (OSError, IOError) as e:
                    print(
                        f"WARNING: Could not load font {sentence_font_path} for sentence '{sentence[:30]}...': {e}")
                    # Fall back to default font
                    sentence_font_path = self.font_path
                    font = ImageFont.truetype(
                        sentence_font_path, current_font_size)
                    transposed_font = ImageFont.TransposedFont(
                        font, orientation=orientation)

                    box_size = draw.textbbox(
                        (0, 0), sentence, font=transposed_font, anchor="lt")
                    result = occupancy.sample_position(
                        box_size[3] + self.margin,
                        box_size[2] + self.margin,
                        random_state
                    )

                    if result is not None:
                        break

                # If we didn't find a place, make font smaller or try rotation
                if not tried_other_orientation and self.prefer_horizontal < 1:
                    orientation = (
                        Image.Transpose.ROTATE_90 if orientation is None else None)
                    tried_other_orientation = True
                else:
                    # Smaller steps for sentences
                    current_font_size -= max(1, self.font_step // 2)
                    orientation = None

            if current_font_size < self.min_font_size:
                print(
                    f"DEBUG: Skipping sentence '{sentence[:30]}...' - font too small")
                continue

            # Place the sentence
            x, y = np.array(result) + self.margin // 2

            # Debug: Print position information
            print(
                f"DEBUG: Positioned sentence '{sentence[:30]}...' at coordinates:")
            print(f"       Raw result: {result}")
            print(f"       Final position (x, y): ({x}, {y})")
            print(f"       Box size (w, h): ({box_size[2]}, {box_size[3]})")
            print(f"       Font size: {current_font_size}")
            print(f"       Orientation: {orientation}")

            # Draw the text with the sentence-specific font
            draw.text((y, x), sentence, fill="white", font=transposed_font)

            # Store layout information
            positions.append((x, y))
            orientations.append(orientation)
            font_sizes.append(current_font_size)
            font_paths.append(sentence_font_path)
            colors.append(self.color_func(
                sentence,
                font_size=current_font_size,
                position=(x, y),
                orientation=orientation,
                random_state=random_state,
                font_path=sentence_font_path  # Pass the sentence-specific font path
            ))

            # Update occupancy map
            if self.mask is None:
                img_array = np.asarray(img_grey)
            else:
                img_array = np.asarray(img_grey) + boolean_mask

            # Update integral image
            occupancy.update(img_array, x, y)
            last_freq = freq

        print(f"DEBUG: Successfully placed {len(positions)} sentences")
        print(f"DEBUG: Final canvas dimensions: {width}x{height}")

        # Store layout with frequencies and font paths
        self.layout_ = list(zip(frequencies, font_sizes,
                            positions, orientations, colors, font_paths))
        return self

    def to_file(self, filename):
        """
        Custom to_file method that properly handles multilingual fonts

        Parameters
        ----------
        filename : string
            Location to write to.

        Returns
        -------
        self
        """
        img = self.to_multilingual_image()
        img.save(filename, optimize=True)
        return self

    def to_multilingual_image(self):
        """
        Create image with proper multilingual font rendering

        Returns
        -------
        img : PIL Image
            Word cloud image with multilingual text properly rendered
        """
        self._check_generated()

        if self.mask is not None:
            width = self.mask.shape[1]
            height = self.mask.shape[0]
        else:
            width = self.width
            height = self.height

        print(f"DEBUG: Original image dimensions: {width}x{height}")
        print(f"DEBUG: Scale factor: {self.scale}")

        scaled_width = int(width * self.scale)
        scaled_height = int(height * self.scale)
        print(
            f"DEBUG: Scaled image dimensions: {scaled_width}x{scaled_height}")

        img = Image.new(self.mode, (scaled_width, scaled_height),
                        self.background_color)
        print(
            f"DEBUG: Created final image with size: {img.size} and mode: {self.mode}")
        draw = ImageDraw.Draw(img)

        # Render each sentence with its specific font
        for (sentence, count), font_size, position, orientation, color, font_path in self.layout_:
            try:
                # Load the specific font for this sentence
                font = ImageFont.truetype(
                    font_path, int(font_size * self.scale))

                # Handle orientation if needed
                if orientation is not None:
                    transposed_font = ImageFont.TransposedFont(
                        font, orientation=orientation)
                else:
                    transposed_font = font

                # Calculate position with scaling
                pos_y, pos_x = position
                scaled_pos = (int(pos_x * self.scale), int(pos_y * self.scale))

                print(
                    f"DEBUG: Rendering '{sentence[:20]}...' at scaled position {scaled_pos} with font size {int(font_size * self.scale)} and color {color}")

                # Draw the text with the sentence-specific font
                draw.text(scaled_pos, sentence,
                          fill=color, font=transposed_font)

            except (OSError, IOError) as e:
                print(
                    f"Warning: Could not load font {font_path} for sentence '{sentence[:30]}...': {e}")
                # Fallback to default font
                try:
                    fallback_font = ImageFont.truetype(
                        self.font_path, int(font_size * self.scale))
                    if orientation is not None:
                        fallback_font = ImageFont.TransposedFont(
                            fallback_font, orientation=orientation)
                    draw.text(scaled_pos, sentence,
                              fill=color, font=fallback_font)
                except Exception as fallback_error:
                    print(
                        f"Error: Could not render sentence '{sentence[:30]}...' with fallback font: {fallback_error}")

        print(f"DEBUG: Final rendered image size: {img.size}")
        print(f"DEBUG: Image mode: {img.mode}")
        return self._draw_contour(img=img)

    def _check_generated(self):
        """Check if layout was generated, otherwise raise error."""
        if not hasattr(self, "layout_"):
            raise ValueError(
                "WordCloud has not been calculated, call generate first.")

    def _draw_contour(self, img):
        """Draw mask contour on a pillow image - simplified version."""
        if self.mask is None or self.contour_width == 0:
            return img

        # For now, return image as-is since contour drawing is complex
        # This can be enhanced later if needed
        return img


def create_multilingual_wordcloud(text_or_frequencies, **kwargs):
    """
    Create a multilingual wordcloud that automatically uses appropriate fonts
    """
    # Set up default multilingual settings optimized for sentences
    default_kwargs = {
        'width': 1600,  # Wider for sentences
        'height': 900,  # Taller for sentences
        'background_color': 'white',
        'max_words': 100,  # Fewer sentences than words
        'colormap': 'viridis',
        'prefer_horizontal': 0.9,  # Prefer horizontal for readability
        'relative_scaling': 0.8,  # More size variation for bigger fonts
        'min_font_size': 15,  # Increased minimum for bigger text
        'font_step': 3,  # Larger font step for better scaling
        'margin': 8  # Larger margin for bigger sentences
    }

    # Merge with user kwargs
    default_kwargs.update(kwargs)

    # Create multilingual wordcloud
    wc = MultilingualWordCloud(**default_kwargs)

    # Generate the wordcloud
    if isinstance(text_or_frequencies, dict):
        return wc.generate_from_frequencies(text_or_frequencies)
    else:
        return wc.generate(text_or_frequencies)


if __name__ == "__main__":
    # Test the multilingual wordcloud with sentences

    test_text = {
        "أنت رائع": 1,  # Arabic
        "You're amazing!": 3,  # English
        "Du bist fantastisch": 1,  # German
        "Sei incredibile": 1,  # Italian
        "¡Eres increíble!": 2,  # Spanish
        "تو شگفت انگیزی": 2,  # Persian
        "Είσαι καταπληκτικός": 1,  # Greek
        "Harikasın": 1,  # Turkish
        "Ты потрясающий": 1,  # Russian
        "Você é incrível": 1,  # Portuguese
        "את מדהימה": 1,  # Hebrew
        "तुम अद्भुत हो": 1,  # Hindi
        "너는 정말 멋져": 1,  # Korean
        "あなたは素晴らしいです": 1,  # Japanese
        "你太棒了": 1,  # Chinese
        "Jesteś niesamowity": 1,  # Polish
        "Du är fantastisk": 1,  # Swedish
        "Вы дзіўныя": 1,  # Belarusian
        "Ти си невероятен": 1,  # Bulgarian
        "Ets increïble": 1,  # Catalan
        "Jsi úžasná": 1,  # Czech
        "Þú ert frábær": 1,  # Icelandic
        "Ти си неверојатен": 1,  # Macedonian
        "Si úžasná": 1,  # Slovak
        "Сез гаҗәп": 1,  # Tatar
        "דו ביסט געוואלדיג": 1,  # Yiddish
        "Դուք զարմանալի եք": 1,  # Armenian
        "Sən heyrətamizsən": 1,  # Azerbaijani
        "আপনি অসাধারণ": 1,  # Bengali
        "你太棒了": 1,  # Chinese
        "საოცარი ხარ": 1,  # Georgian
        # "તમે અદ્ભુત છો": 1,  # Gujarati is not supported
        "あなたが素晴らしいです": 1,  # Japanese
        "तपाईं अद्भुत हुनुहुन्छ": 1,  # Nepali
        "تم کمال ہو": 1,  # Urdu
        "Bạn thật tuyệt vời": 1,  # Vietnamese
        "Tu sosretî": 1,  # Sorani Kurdish
        # "ድንቅ ነህ": 1,  # Amharic not supported

    }

    print("🌍 Testing MultilingualWordCloud with sentences...")

    try:
        wc = create_multilingual_wordcloud(test_text)
        wc.to_file('test_multilingual_sentence_wordcloud.png')
        print("✅ Multilingual sentence wordcloud saved as 'test_multilingual_sentence_wordcloud.png'")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
