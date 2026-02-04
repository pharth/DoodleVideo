"""Scribble generation module using Gemini AI and experimental procedural methods."""

import random
import time
from pathlib import Path
from typing import Optional
import cv2
import numpy as np
from PIL import Image, ImageDraw
from tqdm import tqdm
from google import genai
from google.genai import types

import config


class ScribbleGenerator:
    """Generates scribbled versions of images using AI or procedural methods."""
    
    def __init__(self, mode: str = "ai"):
        """
        Initialize scribble generator.
        
        Args:
            mode: Generation mode - "ai" or "experimental"
        """
        self.mode = mode
        
        if mode == "ai":
            self._setup_ai()
    
    def _setup_ai(self):
        """Setup Google Gemini AI."""
        if not config.GOOGLE_API_KEY:
            raise ValueError(
                "GOOGLE_API_KEY not found. Please set it in your .env file.\n"
                "Get your key from: https://makersuite.google.com/app/apikey"
            )
        
        self.client = genai.Client(api_key=config.GOOGLE_API_KEY)
        print(f"✅ Gemini AI initialized with model: {config.GEMINI_MODEL}\n")
    
    def process_frames(
        self, 
        input_dir: Path = None, 
        output_dir: Path = None,
        delay_between_requests: float = 1.0
    ):
        """
        Process all frames in directory.
        
        Args:
            input_dir: Directory with original frames
            output_dir: Directory to save scribbled frames
            delay_between_requests: Delay between API calls (seconds)
        """
        if input_dir is None:
            input_dir = config.TEMP_ORIGINAL_DIR
        if output_dir is None:
            output_dir = config.TEMP_SCRIBBLED_DIR
        
        # Get all frames
        frame_files = sorted(input_dir.glob("frame_*.jpg"))
        
        if not frame_files:
            raise ValueError(f"No frames found in {input_dir}")
        
        print(f"🎨 Processing {len(frame_files)} frames in '{self.mode}' mode...\n")
        
        # Process each frame
        with tqdm(total=len(frame_files), desc="Generating scribbles", unit="frame") as pbar:
            for frame_file in frame_files:
                output_file = output_dir / frame_file.name
                
                if self.mode == "ai":
                    self._process_frame_ai(frame_file, output_file)
                    # Add delay to respect rate limits
                    time.sleep(delay_between_requests)
                else:
                    self._process_frame_experimental(frame_file, output_file)
                
                pbar.update(1)
        
        print(f"✅ All frames processed and saved to {output_dir}\n")
    
    def _process_frame_ai(self, input_path: Path, output_path: Path):
        """
        Process single frame using Gemini AI.
        
        Args:
            input_path: Path to input frame
            output_path: Path to save scribbled frame
        """
        try:
            # Load image
            image = Image.open(input_path)
            
            # Select random prompt for variety
            prompt = random.choice(config.SCRIBBLE_PROMPTS)
            
            # Generate scribbled version using image-to-image
            response = self.client.models.generate_content(
                model=config.GEMINI_MODEL,
                contents=[prompt, image],
            )
            
            # Extract and save the generated image
            image_saved = False
            for part in response.parts:
                if part.inline_data is not None:
                    generated_image = part.as_image()
                    generated_image.save(output_path)
                    image_saved = True
                    break
            
            # Fallback if no image was generated
            if not image_saved:
                print(f"\n⚠️  No image returned for {input_path.name}, using experimental mode")
                self._process_frame_experimental(input_path, output_path)
                
        except Exception as e:
            print(f"\n⚠️  AI generation failed for {input_path.name}: {e}")
            print("   Falling back to experimental mode...")
            self._process_frame_experimental(input_path, output_path)
    
    def _process_frame_experimental(self, input_path: Path, output_path: Path):
        """
        Process single frame using procedural scribble generation.
        
        Args:
            input_path: Path to input frame
            output_path: Path to save scribbled frame
        """
        # Load image
        img = Image.open(input_path)
        
        # Create drawing context
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        # Generate random scribbles
        for _ in range(config.EXPERIMENTAL_SCRIBBLE_COUNT):
            scribble_type = random.choice(['star', 'swirl', 'line', 'circle', 'smiley'])
            color = random.choice(config.SCRIBBLE_COLORS)
            line_width = random.randint(2, 5)
            
            if scribble_type == 'star':
                self._draw_star(draw, width, height, color, line_width)
            elif scribble_type == 'swirl':
                self._draw_swirl(draw, width, height, color, line_width)
            elif scribble_type == 'line':
                self._draw_squiggly_line(draw, width, height, color, line_width)
            elif scribble_type == 'circle':
                self._draw_circle(draw, width, height, color, line_width)
            elif scribble_type == 'smiley':
                self._draw_smiley(draw, width, height, color, line_width)
        
        # Save scribbled image
        img.save(output_path)
    
    def _draw_star(self, draw, width, height, color, line_width):
        """Draw a random star."""
        cx = random.randint(0, width)
        cy = random.randint(0, height)
        size = random.randint(10, 40)
        
        # 5-pointed star
        points = []
        for i in range(10):
            angle = (i * 36 - 90) * (3.14159 / 180)
            r = size if i % 2 == 0 else size / 2
            x = cx + r * np.cos(angle)
            y = cy + r * np.sin(angle)
            points.append((x, y))
        
        draw.polygon(points, outline=color, width=line_width)
    
    def _draw_swirl(self, draw, width, height, color, line_width):
        """Draw a random swirl."""
        cx = random.randint(0, width)
        cy = random.randint(0, height)
        
        points = []
        for i in range(20):
            angle = i * 0.5
            r = i * 2
            x = cx + r * np.cos(angle)
            y = cy + r * np.sin(angle)
            points.append((x, y))
        
        draw.line(points, fill=color, width=line_width)
    
    def _draw_squiggly_line(self, draw, width, height, color, line_width):
        """Draw a random squiggly line."""
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        
        points = [(x1, y1)]
        for _ in range(random.randint(3, 8)):
            x1 += random.randint(-50, 50)
            y1 += random.randint(-50, 50)
            x1 = max(0, min(width, x1))
            y1 = max(0, min(height, y1))
            points.append((x1, y1))
        
        draw.line(points, fill=color, width=line_width, joint='curve')
    
    def _draw_circle(self, draw, width, height, color, line_width):
        """Draw a random circle."""
        cx = random.randint(0, width)
        cy = random.randint(0, height)
        radius = random.randint(10, 40)
        
        bbox = [cx - radius, cy - radius, cx + radius, cy + radius]
        draw.ellipse(bbox, outline=color, width=line_width)
    
    def _draw_smiley(self, draw, width, height, color, line_width):
        """Draw a random smiley face."""
        cx = random.randint(0, width)
        cy = random.randint(0, height)
        size = random.randint(20, 50)
        
        # Face circle
        bbox = [cx - size, cy - size, cx + size, cy + size]
        draw.ellipse(bbox, outline=color, width=line_width)
        
        # Eyes
        eye_offset = size // 3
        eye_size = size // 8
        draw.ellipse([cx - eye_offset - eye_size, cy - eye_offset - eye_size,
                     cx - eye_offset + eye_size, cy - eye_offset + eye_size],
                     fill=color)
        draw.ellipse([cx + eye_offset - eye_size, cy - eye_offset - eye_size,
                     cx + eye_offset + eye_size, cy - eye_offset + eye_size],
                     fill=color)
        
        # Smile
        smile_bbox = [cx - size//2, cy - size//2, cx + size//2, cy + size//2]
        draw.arc(smile_bbox, start=0, end=180, fill=color, width=line_width)
