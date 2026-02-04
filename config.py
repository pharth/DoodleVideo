"""Configuration settings for video scribble generator."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
BASE_DIR = Path(__file__).parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
TEMP_DIR = BASE_DIR / "temp"
TEMP_ORIGINAL_DIR = TEMP_DIR / "original"
TEMP_SCRIBBLED_DIR = TEMP_DIR / "scribbled"

# API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash-image"  # Image-to-image generation model

# Video Processing Settings
DEFAULT_FPS = 30
VIDEO_CODEC = "mp4v"  # For .mp4 output
VIDEO_EXTENSION = ".mp4"
MAX_DURATION_SECONDS = None  # Set to number (e.g., 3) to process only first N seconds, None for full video

# Scribble Generation Settings
SCRIBBLE_PROMPTS = [
    "Add a playful overlay of colorful hand-drawn doodles on top of this image. First, detect the main subjects, objects, and prominent edges in the scene. Draw thick white marker-style contour lines around the people, plates, food, and other important shapes, following their edges loosely like an outline sketch. Then add random colorful scribbles, stars, swirls, smiley faces, zigzags, and messy strokes in bright red, yellow, green, and blue. Scatter these doodles around the outlined shapes in a spontaneous, energetic style, similar to fun chaotic hand-drawn graffiti. Keep the original image fully visible beneath the drawings. The effect should look like expressive doodles layered on top of the photograph, with outlines emphasizing edges and doodles adding chaos and personality. Include randomness in placement, size, and density of the scribbles so every result is unique."
]

# Experimental mode settings (procedural generation)
EXPERIMENTAL_SCRIBBLE_COUNT = 20  # Number of scribbles per frame
SCRIBBLE_COLORS = [
    (255, 0, 0),      # Red
    (0, 255, 0),      # Green
    (0, 0, 255),      # Blue
    (255, 255, 0),    # Yellow
    (255, 128, 0),    # Orange
    (128, 0, 255),    # Purple
]

# Ensure directories exist
for directory in [INPUT_DIR, OUTPUT_DIR, TEMP_ORIGINAL_DIR, TEMP_SCRIBBLED_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
