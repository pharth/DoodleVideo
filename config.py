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
    "Add a playful overlay of hand-drawn doodles on top of this image. First, detect the main subjects, objects, and strong edges in the scene. Draw thick, bold white contour lines around these elements — the outlines should loosely follow their shapes, creating an exaggerated marker-style border that clearly separates each object from the background. Then add colorful doodles (stars, swirls, smiley faces, loops, zigzags, waves, and marker scribbles) in bright red, yellow, green, and blue. Make the doodles hug the edges and flow around the outlined elements, following their curves or general direction, rather than floating randomly. They should feel like they interact with the objects. Ensure each doodle has a sense of direction and motion — for example: wrapping around a corner, pointing toward edges, or swirling along shapes. Keep a small amount of space between doodles, so they do not overlap each other, but still appear energetic and lively. Preserve the original photo underneath. The final result should look like a stylized, expressive scribble layer with bold outlines emphasizing the subjects and playful doodles that follow and accent the scene."
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
