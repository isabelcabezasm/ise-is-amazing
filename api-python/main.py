from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import time
import os
import io
import re
import glob
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from wordcloud import WordCloud
from PIL import Image
from multilingual_wordcloud_sentences import MultilingualWordCloud, create_multilingual_wordcloud

# Load environment variables
load_dotenv()


def find_existing_font(candidates):
    """Find the first existing font from a list of candidates"""
    for font_path in candidates:
        if '*' in font_path:
            # Handle wildcard patterns
            matches = glob.glob(font_path)
            if matches:
                return matches[0]
        elif os.path.exists(font_path):
            return font_path
    return None


def get_font_for_text(text: str) -> str:
    """
    Detect the script/language in the text and return appropriate font path.
    Returns the best font for rendering the given text with improved multilingual support.
    """
    # Define multiple possible font paths for different scripts (Debian/Ubuntu paths)
    # Try multiple possible locations since container font paths may vary
    font_candidates = {
        'hebrew': [
            '/usr/share/fonts/truetype/noto/NotoSansHebrew-Regular.ttf',
            '/usr/share/fonts/opentype/noto/NotoSansHebrew-Regular.otf',
            '/usr/share/fonts/truetype/noto/NotoSansHebrew[wght].ttf',
            '/usr/share/fonts/truetype/noto/NotoSansHebrew-*.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Fallback with Hebrew support
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
        ],
        'arabic': [
            '/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf',
            '/usr/share/fonts/opentype/noto/NotoSansArabic-Regular.otf',
            '/usr/share/fonts/truetype/noto/NotoSansArabic[wght].ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        ],
        'cjk': [
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/truetype/noto/NotoSansCJKjp-Regular.otf',
            '/usr/share/fonts/opentype/noto/NotoSansCJKjp-Regular.otf',
        ],
        'devanagari': [
            '/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf',
            '/usr/share/fonts/opentype/noto/NotoSansDevanagari-Regular.otf',
            '/usr/share/fonts/truetype/noto/NotoSansDevanagari[wght].ttf',
        ],
        'greek': [
            # NotoSans has good Greek support
            '/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
        ],
        'cyrillic': [
            # NotoSans has good Cyrillic support
            '/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
        ],
        'multilingual': [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Better Hebrew+Latin support
            '/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
        ],
        'general': [
            '/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
        ]
    }

    # Define Unicode patterns for script detection
    hebrew_pattern = re.compile(r'[\u0590-\u05ff\ufb1d-\ufb4f]')
    arabic_pattern = re.compile(
        r'[\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff\ufb50-\ufdff\ufe70-\ufeff]')
    cjk_pattern = re.compile(
        r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]')
    devanagari_pattern = re.compile(r'[\u0900-\u097f]')
    latin_pattern = re.compile(r'[a-zA-Z]')
    greek_pattern = re.compile(r'[\u0370-\u03ff\u1f00-\u1fff]')
    cyrillic_pattern = re.compile(r'[\u0400-\u04ff]')

    # Count how many different scripts are present
    scripts_detected = []
    if hebrew_pattern.search(text):
        scripts_detected.append('hebrew')
    if arabic_pattern.search(text):
        scripts_detected.append('arabic')
    if cjk_pattern.search(text):
        scripts_detected.append('cjk')
    if devanagari_pattern.search(text):
        scripts_detected.append('devanagari')
    if latin_pattern.search(text):
        scripts_detected.append('latin')
    if greek_pattern.search(text):
        scripts_detected.append('greek')
    if cyrillic_pattern.search(text):
        scripts_detected.append('cyrillic')

    # If multiple scripts detected, use smart multilingual font selection
    if len(scripts_detected) > 1:
        # Special handling for extreme multilingual cases (3+ scripts)
        if len(scripts_detected) >= 3:
            # For many scripts, use DejaVu Sans which has broader Unicode support than NotoSans
            print(
                f"DEBUG: Extreme multilingual text detected ({len(scripts_detected)} scripts: {', '.join(scripts_detected)})")
            font_path = find_existing_font(
                ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'])
            if font_path:
                print(
                    f"DEBUG: Using DejaVu Sans for extreme multilingual support: {font_path}")
                return font_path
            else:
                print("DEBUG: DejaVu Sans not found, using system font fallbacks")
                return None  # Let WordCloud use system font fallbacks

        # Special handling for 2-script combinations
        elif 'cjk' in scripts_detected and 'latin' in scripts_detected:
            # For CJK+Latin, use CJK font which usually has Latin support
            font_path = find_existing_font(font_candidates['cjk'])
            if font_path:
                print(
                    f"DEBUG: CJK+Latin multilingual text detected, using CJK font: {font_path}")
                return font_path

        elif 'arabic' in scripts_detected and 'latin' in scripts_detected:
            # For Arabic+Latin, DejaVu Sans works well
            font_path = find_existing_font(font_candidates['multilingual'])
            if font_path:
                print(
                    f"DEBUG: Arabic+Latin multilingual text detected, using multilingual font: {font_path}")
                return font_path

        elif 'hebrew' in scripts_detected and 'latin' in scripts_detected:
            # For Hebrew+Latin, DejaVu Sans works well
            font_path = find_existing_font(font_candidates['multilingual'])
            if font_path:
                print(
                    f"DEBUG: Hebrew+Latin multilingual text detected, using multilingual font: {font_path}")
                return font_path

        else:
            # For other 2-script combinations, try multilingual font first
            font_path = find_existing_font(font_candidates['multilingual'])
            if font_path:
                print(
                    f"DEBUG: Multilingual text detected ({', '.join(scripts_detected)}), using multilingual font: {font_path}")
                return font_path

        print(f"WARNING: Multilingual text detected but no suitable multilingual font found, falling back to script-specific")

    # Single script detection - use script-specific fonts
    if 'hebrew' in scripts_detected:
        font_path = find_existing_font(font_candidates['hebrew'])
        if font_path:
            print(f"DEBUG: Using Hebrew font: {font_path}")
            return font_path
        print("WARNING: No Hebrew font found, using fallback")

    if 'arabic' in scripts_detected:
        font_path = find_existing_font(font_candidates['arabic'])
        if font_path:
            print(f"DEBUG: Using Arabic font: {font_path}")
            return font_path

    if 'cjk' in scripts_detected:
        font_path = find_existing_font(font_candidates['cjk'])
        if font_path:
            print(f"DEBUG: Using CJK font: {font_path}")
            return font_path

    if 'devanagari' in scripts_detected:
        font_path = find_existing_font(font_candidates['devanagari'])
        if font_path:
            print(f"DEBUG: Using Devanagari font: {font_path}")
            return font_path

    if 'greek' in scripts_detected:
        font_path = find_existing_font(font_candidates['greek'])
        if font_path:
            print(f"DEBUG: Using Greek font: {font_path}")
            return font_path

    if 'cyrillic' in scripts_detected:
        font_path = find_existing_font(font_candidates['cyrillic'])
        if font_path:
            print(f"DEBUG: Using Cyrillic font: {font_path}")
            return font_path

    # For Greek, Cyrillic, and other scripts, use general fonts
    if greek_pattern.search(text) or cyrillic_pattern.search(text):
        font_path = find_existing_font(font_candidates['general'])
        if font_path:
            print(f"DEBUG: Using general font for special script: {font_path}")
            return font_path

    # Final fallback - try to find any usable font
    font_path = find_existing_font(font_candidates['general'])
    if font_path:
        print(f"DEBUG: Using fallback font: {font_path}")
        return font_path

    print("WARNING: No suitable font found, using system default")
    return None


def create_wordcloud_with_font_support(text, width: int = 800, height: int = 400, background_color: str = 'white', **kwargs):
    """
    Create a wordcloud with comprehensive multilingual font support
    Accepts either text string or frequency dictionary
    """
    if isinstance(text, dict):
        print(
            f"📝 Creating multilingual wordcloud for {len(text)} frequency entries...")
    else:
        print(
            f"📝 Creating multilingual wordcloud for text: {str(text)[:100]}...")

    # Use the updated MultilingualWordCloud
    try:
        # Merge default settings with any kwargs passed
        default_kwargs = {
            'width': width,
            'height': height,
            'background_color': background_color,
            'max_words': 200,
            'min_font_size': 12,        # Larger minimum font
            'prefer_horizontal': 0.8,   # More horizontal text
            'relative_scaling': 0.6,    # Better scaling
            'colormap': 'viridis',
            'margin': 10
        }

        # Update with any additional kwargs
        default_kwargs.update(kwargs)

        # Create wordcloud with improved settings for better visibility
        if isinstance(text, dict):
            # Handle frequency dictionary case
            wordcloud = MultilingualWordCloud(**default_kwargs)
            wordcloud_generated = wordcloud.generate_from_frequencies(text)
        else:
            # Handle text string case
            wordcloud_generated = create_multilingual_wordcloud(
                text, **default_kwargs)

        # Save to file and then read it back
        temp_filename = 'temp_multilingual_wordcloud.png'
        wordcloud_generated.to_file(temp_filename)

        # Read the saved file
        img = Image.open(temp_filename)

        # Clean up the temporary file
        import os
        try:
            os.remove(temp_filename)
        except:
            pass  # Ignore cleanup errors

        print(f"✅ Successfully created multilingual wordcloud: {img.size}")
        return img

    except Exception as e:
        print(f"❌ Error creating multilingual wordcloud: {e}")
        import traceback
        traceback.print_exc()
        raise


app = FastAPI(title="You Are Amazing API", version="2.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models


class AmazingItem(BaseModel):
    id: str
    text: str
    language: str
    reps: int = 1


class CreateItemRequest(BaseModel):
    text: str


class DetectLanguageRequest(BaseModel):
    text: str


class DetectLanguageResponse(BaseModel):
    text: str
    detected_language: str
    confidence: Optional[float] = None


class ItemsResponse(BaseModel):
    items: List[AmazingItem]


class ItemResponse(BaseModel):
    item: AmazingItem
    duplicate: Optional[bool] = None


class MessageResponse(BaseModel):
    message: str


class CloudRequest(BaseModel):
    sentences: List[str]
    width: Optional[int] = 800
    height: Optional[int] = 400
    background_color: Optional[str] = "white"
    colormap: Optional[str] = "viridis"


class BatchItemRequest(BaseModel):
    sentences: List[str]


class BatchItemData(BaseModel):
    text: str
    language: Optional[str] = "Auto-detected"
    reps: Optional[int] = 1


class EnhancedBatchItemRequest(BaseModel):
    items: List[BatchItemData]


class BatchItemResponse(BaseModel):
    added_items: List[AmazingItem]
    skipped_duplicates: int
    total_processed: int


# In-memory storage for amazing items
amazing_items: List[AmazingItem] = [
    AmazingItem(id="1", text="You are amazing!", language="English", reps=1),
]

# Global variable to store the agent IDs
language_detector_agent_id = None
semantic_validator_agent_id = None

# Initialize Azure AI Project Client


def get_ai_client():
    try:
        # Get the endpoint from environment
        endpoint = os.environ.get("PROJECT_ENDPOINT")
        model_name = os.environ.get("MODEL_DEPLOYMENT_NAME")

        print(f"DEBUG: PROJECT_ENDPOINT = {endpoint}")
        print(f"DEBUG: MODEL_DEPLOYMENT_NAME = {model_name}")

        if not endpoint:
            raise HTTPException(
                status_code=500,
                detail="PROJECT_ENDPOINT environment variable is not set. Please check your .env file."
            )

        if not model_name:
            raise HTTPException(
                status_code=500,
                detail="MODEL_DEPLOYMENT_NAME environment variable is not set. Please check your .env file."
            )

        # Use DefaultAzureCredential for authentication
        print(f"DEBUG: Initializing AIProjectClient with endpoint: {endpoint}")
        return AIProjectClient(
            endpoint=endpoint,
            credential=DefaultAzureCredential(),
        )
    except HTTPException:
        raise  # Re-raise HTTPExceptions as they are
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to initialize Azure AI client: {str(e)}")


def get_or_create_semantic_validator_agent(project_client):
    """Get existing semantic validator agent or create a new one"""
    global semantic_validator_agent_id

    # Check if we already have an agent ID stored
    if semantic_validator_agent_id:
        try:
            # Try to retrieve the existing agent
            agent = project_client.agents.get_agent(
                semantic_validator_agent_id)
            print(
                f"DEBUG: Using existing semantic validator agent: {agent.id}")
            return agent
        except Exception as e:
            print(
                f"DEBUG: Existing semantic validator agent not found or error retrieving: {e}")
            semantic_validator_agent_id = None

    # List existing agents to see if we have a semantic validator
    try:
        agents = project_client.agents.list_agents()
        for agent in agents:
            if agent.name == "semantic-validator-agent":
                print(
                    f"DEBUG: Found existing semantic validator agent: {agent.id}")
                semantic_validator_agent_id = agent.id
                return agent
    except Exception as e:
        print(f"DEBUG: Error listing agents: {e}")

    # Create new agent if none exists
    print("DEBUG: Creating new semantic validator agent...")
    tools = []  # No special tools needed for semantic validation

    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="semantic-validator-agent",
        instructions=(
            "You are a semantic validation expert. "
            "Your job is to determine if a given text message conveys the same meaning as 'You are amazing'. "
            "The message can be in any language and can use different words, but it should express appreciation, "
            "encouragement, praise, or positive affirmation similar to telling someone they are amazing, wonderful, "
            "great, fantastic, incredible, awesome, brilliant, outstanding, or any other positive sentiment. "
            "Respond with exactly 'VALID' if the message has a similar positive meaning, or 'INVALID' if it doesn't. "
            "Examples of VALID: 'You are wonderful', 'Eres increíble', 'Tu es fantastique', 'You rock', 'You're the best' "
            "Examples of INVALID: 'Hello world', 'What time is it?', 'I like pizza', 'Random text', 'poooppuupu'"
        ),
        tools=tools,
    )

    semantic_validator_agent_id = agent.id
    print(f"DEBUG: Created new semantic validator agent: {agent.id}")
    return agent


async def validate_semantic_meaning(text: str) -> bool:
    """Validate if the text means something similar to 'you are amazing' using Azure AI"""

    print("DEBUG: Attempting to validate semantic meaning with Azure AI...")
    project_client = get_ai_client()

    try:
        # Get or create the semantic validator agent
        agent = get_or_create_semantic_validator_agent(project_client)

        # Use the create_thread_and_run method
        message_content = f"Does this text convey a meaning similar to 'You are amazing'? Text: '{text}'"
        print(
            f"DEBUG: Creating thread and run for semantic validation: {message_content}")

        run = project_client.agents.create_thread_and_run(
            agent_id=agent.id,
            thread={
                "messages": [
                    {
                        "role": "user",
                        "content": message_content
                    }
                ]
            }
        )

        # Wait for completion
        print("DEBUG: Waiting for semantic validation response...")
        while run.status in ["queued", "in_progress"]:
            import asyncio
            await asyncio.sleep(0.5)
            run = project_client.agents.runs.get(
                thread_id=run.thread_id, run_id=run.id)

        if run.status == "completed":
            # Get the response messages
            messages = project_client.agents.messages.list(
                thread_id=run.thread_id)

            # Get the latest assistant message
            for msg in messages:
                if msg.role == "assistant":
                    response = msg.content[0].text.value.strip().upper()
                    print(f"DEBUG: Semantic validation response: {response}")

                    # Clean up the thread
                    try:
                        project_client.agents.threads.delete(run.thread_id)
                    except Exception as e:
                        print(f"DEBUG: Error deleting thread: {e}")

                    return response == "VALID"

            # If no assistant message found, return False
            is_valid = False
        else:
            print(
                f"DEBUG: Semantic validation run failed with status: {run.status}")
            is_valid = False

        # Clean up the thread in case of error
        try:
            project_client.agents.threads.delete(run.thread_id)
        except Exception as e:
            print(f"DEBUG: Error deleting thread: {e}")

        return is_valid

    except Exception as e:
        print(f"DEBUG: Error in validate_semantic_meaning: {e}")
        print(f"DEBUG: Exception type: {type(e)}")
        return False


def get_or_create_language_agent(project_client):
    """Get existing language detector agent or create a new one"""
    global language_detector_agent_id

    # Check if we already have an agent ID stored
    if language_detector_agent_id:
        try:
            # Try to retrieve the existing agent
            agent = project_client.agents.get_agent(language_detector_agent_id)
            print(f"DEBUG: Using existing agent: {agent.id}")
            return agent
        except Exception as e:
            print(
                f"DEBUG: Existing agent not found or error retrieving: {e}")
            language_detector_agent_id = None

    # List existing agents to see if we have a language detector
    try:
        agents = project_client.agents.list_agents()
        for agent in agents:
            if agent.name == "language-detector-agent":
                print(
                    f"DEBUG: Found existing language detector agent: {agent.id}")
                language_detector_agent_id = agent.id
                return agent
    except Exception as e:
        print(f"DEBUG: Error listing agents: {e}")

    # Create new agent if none exists
    print("DEBUG: Creating new language detector agent...")
    tools = []  # No special tools needed for language detection

    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="language-detector-agent",
        instructions=(
            "You are a language detection expert. "
            "Analyze the provided text and identify its language. "
            "Always respond with only the language name in English "
            "(e.g., 'English', 'French', 'Spanish', 'German', etc.). "
            "If you're not confident about the language, respond with 'Unknown'."
        ),
        tools=tools,
    )

    language_detector_agent_id = agent.id
    print(f"DEBUG: Created new language detector agent: {agent.id}")
    return agent


async def detect_language_with_ai(text: str) -> tuple[str, float]:
    """Detect language using Azure AI Project Client with agents"""

    print("DEBUG: Attempting to initialize Azure AI client...")
    project_client = get_ai_client()
    print("DEBUG: Azure AI client initialized successfully")

    try:
        # Get or create the language detector agent
        agent = get_or_create_language_agent(project_client)

        # Use the simpler create_thread_and_run method
        message_content = f"Detect the language of this text: '{text}'"
        print(
            f"DEBUG: Creating thread and run with message: {message_content}")

        run = project_client.agents.create_thread_and_run(
            agent_id=agent.id,
            thread={
                "messages": [
                    {
                        "role": "user",
                        "content": message_content
                    }
                ]
            }
        )

        # Wait for completion
        print("DEBUG: Waiting for agent response...")
        while run.status in ["queued", "in_progress"]:
            import asyncio
            await asyncio.sleep(0.5)
            run = project_client.agents.runs.get(
                thread_id=run.thread_id, run_id=run.id)

        if run.status == "completed":
            # Get the response messages
            messages = project_client.agents.messages.list(
                thread_id=run.thread_id)

            # Get the latest assistant message
            for msg in messages:
                if msg.role == "assistant":
                    detected_language = msg.content[0].text.value.strip()
                    print(
                        f"DEBUG: Azure AI agent detected language: {detected_language}")
                    confidence = 0.9  # High confidence with AI agent

                    # Clean up the thread
                    try:
                        project_client.agents.threads.delete(run.thread_id)
                    except Exception as e:
                        print(f"DEBUG: Error deleting thread: {e}")

                    return detected_language, confidence

            # If no assistant message found, return unknown
            detected_language = "Unknown"
            confidence = 0.0
        else:
            print(f"DEBUG: Agent run failed with status: {run.status}")
            detected_language = "Unknown"
            confidence = 0.0

        # Clean up the thread in case of error
        try:
            project_client.agents.threads.delete(run.thread_id)
        except Exception as e:
            print(f"DEBUG: Error deleting thread: {e}")

        return detected_language, confidence

    except Exception as e:
        print(f"DEBUG: Error in detect_language_with_ai: {e}")
        print(f"DEBUG: Exception type: {type(e)}")
        return "Unknown", 0.0


@app.get("/")
async def root():
    return {"message": "You Are Amazing API - FastAPI Version"}


@app.get("/api/amazing", response_model=ItemsResponse)
async def get_amazing_items():
    """Get all amazing items"""
    return ItemsResponse(items=amazing_items)


@app.post("/api/amazing", response_model=ItemResponse)
async def create_amazing_item(request: CreateItemRequest):
    """Create a new amazing item or increment reps if duplicate"""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")

    # First, validate that the message means something similar to "you are amazing"
    is_semantically_valid = await validate_semantic_meaning(request.text)
    if not is_semantically_valid:
        raise HTTPException(
            status_code=400,
            detail="The message should express something similar to 'You are amazing'"
        )

    # Detect language automatically using AI
    detected_language, confidence = await detect_language_with_ai(request.text)

    # Check if language detection failed
    if detected_language == "Unknown":
        raise HTTPException(
            status_code=400,
            detail="Language could not be detected. Please try with text in a recognizable language."
        )

    # Check if we already have a message in this language
    existing_language_item = None
    for item in amazing_items:
        if item.language.lower() == detected_language.lower():
            existing_language_item = item
            break

    if existing_language_item:
        # Increment reps for existing language and return message about repetition
        existing_language_item.reps += 1
        raise HTTPException(
            status_code=400,
            detail=f"We already have the sentence '{existing_language_item.text}' in {detected_language}. Adding a repetition instead."
        )

    # Check for exact text duplicates (case-insensitive)
    existing_item = None
    for item in amazing_items:
        if item.text.lower() == request.text.lower():
            existing_item = item
            break

    if existing_item:
        # Increment reps for existing item
        existing_item.reps += 1
        return ItemResponse(item=existing_item, duplicate=True)
    else:
        # Create new item with detected language
        new_item = AmazingItem(
            id=str(int(time.time() * 1000)),  # Timestamp as ID
            text=request.text.strip(),
            language=detected_language,
            reps=1
        )
        amazing_items.append(new_item)
        return ItemResponse(item=new_item)


@app.post("/api/amazing/batch", response_model=BatchItemResponse)
async def add_batch_amazing_items(request: BatchItemRequest):
    """Add multiple amazing items in batch without AI validation"""
    if not request.sentences or len(request.sentences) == 0:
        raise HTTPException(
            status_code=400, detail="At least one sentence is required")

    added_items = []
    skipped_duplicates = 0

    for sentence in request.sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        # Check for exact text duplicates (case-insensitive)
        existing_item = None
        for item in amazing_items:
            if item.text.lower() == sentence.lower():
                existing_item = item
                break

        if existing_item:
            # Skip duplicate, just count it
            skipped_duplicates += 1
        else:
            # Create new item without AI validation
            new_item = AmazingItem(
                # Unique timestamp-based ID
                id=str(int(time.time() * 1000000) + len(added_items)),
                text=sentence,
                language="Auto-detected",  # Default language for batch uploads
                reps=1
            )
            amazing_items.append(new_item)
            added_items.append(new_item)

    return BatchItemResponse(
        added_items=added_items,
        skipped_duplicates=skipped_duplicates,
        total_processed=len(request.sentences)
    )


@app.post("/api/amazing/batch-enhanced", response_model=BatchItemResponse)
async def add_enhanced_batch_amazing_items(request: EnhancedBatchItemRequest):
    """Add multiple amazing items with language and repetition info without AI validation"""
    if not request.items or len(request.items) == 0:
        raise HTTPException(
            status_code=400, detail="At least one item is required")

    added_items = []
    skipped_duplicates = 0

    for item_data in request.items:
        text = item_data.text.strip()
        if not text:
            continue

        # Check for exact text duplicates (case-insensitive)
        existing_item = None
        for item in amazing_items:
            if item.text.lower() == text.lower():
                existing_item = item
                break

        if existing_item:
            # Update the existing item's reps instead of skipping
            existing_item.reps += item_data.reps or 1
            skipped_duplicates += 1
        else:
            # Create new item with provided language and reps
            new_item = AmazingItem(
                # Unique timestamp-based ID
                id=str(int(time.time() * 1000000) + len(added_items)),
                text=text,
                language=item_data.language or "Auto-detected",
                reps=item_data.reps or 1
            )
            amazing_items.append(new_item)
            added_items.append(new_item)

    return BatchItemResponse(
        added_items=added_items,
        skipped_duplicates=skipped_duplicates,
        total_processed=len(request.items)
    )


@app.delete("/api/amazing", response_model=MessageResponse)
async def clear_amazing_items():
    """Clear all amazing items"""
    amazing_items.clear()
    return MessageResponse(message="All items cleared")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "items_count": len(amazing_items)}


@app.post("/api/detect-language", response_model=DetectLanguageResponse)
async def detect_language(request: DetectLanguageRequest):
    """Detect the language of the provided text using Azure AI"""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")

    detected_language, confidence = await detect_language_with_ai(request.text)
    return DetectLanguageResponse(
        text=request.text,
        detected_language=detected_language,
        confidence=confidence
    )


@app.get("/api/cloud/amazing")
async def generate_amazing_word_cloud(
    width: Optional[int] = 800,
    height: Optional[int] = 400,
    background_color: Optional[str] = "white",
    colormap: Optional[str] = "viridis"
):
    """Generate a word cloud from all existing amazing items"""
    if not amazing_items:
        raise HTTPException(
            status_code=400, detail="No amazing items found to generate word cloud")

    # Extract all text from amazing items, repeating based on reps
    sentences = []
    for item in amazing_items:
        for _ in range(item.reps):
            sentences.append(item.text)

    # Combine all sentences into one text
    combined_text = "\n".join(sentences)

    try:
        # Create WordCloud object with font support
        wordcloud_img = create_wordcloud_with_font_support(
            combined_text,
            width=width,
            height=height,
            background_color=background_color,
            colormap=colormap,
            max_words=100,
            relative_scaling=0.5,
            random_state=42
        )

        # Convert PIL Image to buffer
        img_buffer = io.BytesIO()
        wordcloud_img.save(img_buffer, format='PNG')
        img_buffer.seek(0)

        # Return image as response
        return StreamingResponse(
            io.BytesIO(img_buffer.read()),
            media_type="image/png",
            headers={
                "Content-Disposition": "inline; filename=amazing_wordcloud.png"}
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating word cloud: {str(e)}")


@app.get("/api/cloud/sentences", response_class=StreamingResponse)
async def generate_sentence_cloud(
    background_color: str = Query(default="white"),
    colormap: str = Query(default="viridis"),
    width: int = Query(default=800, ge=200, le=1600),
    height: int = Query(default=600, ge=200, le=1200)
):
    """Generate a sentence cloud from amazing items where each sentence appears as a unit"""

    if not amazing_items:
        raise HTTPException(
            status_code=404, detail="No amazing items found")

    # Create frequency dictionary where each sentence is a "word" with its repetition count
    sentence_frequencies = {}

    for item in amazing_items:
        # Use the sentence as the "word" and reps as frequency
        # Clean up the sentence to avoid issues with special characters
        clean_sentence = item.text.strip().replace('\n', ' ').replace('\r', '')
        if clean_sentence:
            sentence_frequencies[clean_sentence] = item.reps

    if not sentence_frequencies:
        raise HTTPException(
            status_code=400, detail="No valid sentences found")

    try:
        # Create WordCloud object with sentence-friendly settings and font support
        wordcloud_img = create_wordcloud_with_font_support(
            sentence_frequencies,
            width=width,
            height=height,
            background_color=background_color,
            colormap=colormap,
            max_words=len(sentence_frequencies),  # Show all sentences
            relative_scaling=0.5,  # Smaller scaling for better sentence fitting
            random_state=42,
            min_font_size=8,  # Smaller minimum font for longer sentences
        )

        # Convert PIL Image to buffer
        img_buffer = io.BytesIO()
        wordcloud_img.save(img_buffer, format='PNG')
        img_buffer.seek(0)

        # Return image as response
        return StreamingResponse(
            io.BytesIO(img_buffer.read()),
            media_type="image/png",
            headers={
                "Content-Disposition": "inline; filename=sentence_cloud.png"}
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating sentence cloud: {str(e)}")


@app.post("/api/cloud/sentences", response_class=StreamingResponse)
async def generate_custom_sentence_cloud(request: CloudRequest):
    """Generate a sentence cloud from custom sentences"""

    if not request.sentences:
        raise HTTPException(
            status_code=400, detail="Sentences list cannot be empty")

    # Create frequency dictionary where each sentence is a "word" with frequency 1
    sentence_frequencies = {}

    for sentence in request.sentences:
        # Clean up the sentence
        clean_sentence = sentence.strip().replace('\n', ' ').replace('\r', '')
        if clean_sentence:
            # If sentence already exists, increment frequency
            sentence_frequencies[clean_sentence] = sentence_frequencies.get(
                clean_sentence, 0) + 1

    if not sentence_frequencies:
        raise HTTPException(
            status_code=400, detail="No valid sentences found")

    try:
        # Create WordCloud object with sentence-friendly settings and font support
        wordcloud_img = create_wordcloud_with_font_support(
            sentence_frequencies,
            width=request.width,
            height=request.height,
            background_color=request.background_color,
            colormap=request.colormap,
            max_words=len(sentence_frequencies),  # Show all sentences
            relative_scaling=0.3,  # Smaller scaling for better sentence fitting
            random_state=42,
            prefer_horizontal=0.9,  # Prefer horizontal text for readability
            min_font_size=8,  # Smaller minimum font for longer sentences
            max_font_size=40,  # Reasonable max font size
            margin=5,  # Add margin for better spacing
            collocations=False  # Don't treat word pairs as single units
        )

        # Convert PIL Image to buffer
        img_buffer = io.BytesIO()
        wordcloud_img.save(img_buffer, format='PNG')
        img_buffer.seek(0)

        # Return image as response
        return StreamingResponse(
            io.BytesIO(img_buffer.read()),
            media_type="image/png",
            headers={"Content-Disposition": "inline; filename=sentence_cloud.png"}
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating sentence cloud: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
