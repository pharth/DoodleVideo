"""Video processing module for frame extraction and video reconstruction."""

import cv2
import os
from pathlib import Path
from typing import Tuple, List
from tqdm import tqdm
import config


class VideoProcessor:
    """Handles video splitting into frames and stitching frames back into video."""
    
    def __init__(self, video_path: str):
        """Initialize with video path."""
        self.video_path = Path(video_path)
        self.fps = None
        self.frame_size = None
        self.total_frames = 0
        
    def extract_frames(self, output_dir: Path = None, max_duration: float = None) -> Tuple[int, float, Tuple[int, int]]:
        """
        Extract all frames from video.
        
        Args:
            output_dir: Directory to save frames (default: temp/original)
            max_duration: Maximum duration in seconds to extract (None for full video)
            
        Returns:
            Tuple of (total_frames, fps, frame_size)
        """
        if output_dir is None:
            output_dir = config.TEMP_ORIGINAL_DIR
        
        # Clear existing frames
        self._clear_directory(output_dir)
        
        # Open video
        cap = cv2.VideoCapture(str(self.video_path))
        
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {self.video_path}")
        
        # Get video properties
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frame_size = (width, height)
        
        # Calculate frame limit based on duration
        if max_duration is not None:
            max_frames = int(max_duration * self.fps)
            frames_to_extract = min(max_frames, self.total_frames)
            print(f"📹 Video Info:")
            print(f"   Resolution: {width}x{height}")
            print(f"   FPS: {self.fps}")
            print(f"   Total Frames: {self.total_frames} (Full video)")
            print(f"   Extracting: First {max_duration} seconds ({frames_to_extract} frames)\n")
        else:
            frames_to_extract = self.total_frames
            print(f"📹 Video Info:")
            print(f"   Resolution: {width}x{height}")
            print(f"   FPS: {self.fps}")
            print(f"   Total Frames: {self.total_frames}")
            print(f"   Duration: {self.total_frames/self.fps:.2f} seconds\n")
        
        # Extract frames
        frame_count = 0
        with tqdm(total=frames_to_extract, desc="Extracting frames", unit="frame") as pbar:
            while frame_count < frames_to_extract:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Save frame
                frame_filename = output_dir / f"frame_{frame_count:05d}.jpg"
                cv2.imwrite(str(frame_filename), frame)
                
                frame_count += 1
                pbar.update(1)
        
        cap.release()
        print(f"✅ Extracted {frame_count} frames to {output_dir}\n")
        
        return frame_count, self.fps, self.frame_size
    
    def stitch_frames(
        self, 
        frames_dir: Path = None, 
        output_path: str = None,
        fps: float = None,
        frame_size: Tuple[int, int] = None
    ) -> str:
        """
        Stitch frames back into a video.
        
        Args:
            frames_dir: Directory containing frames (default: temp/scribbled)
            output_path: Output video path
            fps: Frames per second (uses extracted fps if None)
            frame_size: Frame dimensions (uses extracted size if None)
            
        Returns:
            Path to output video
        """
        if frames_dir is None:
            frames_dir = config.TEMP_SCRIBBLED_DIR
        
        if output_path is None:
            output_path = config.OUTPUT_DIR / f"scribbled_{self.video_path.stem}{config.VIDEO_EXTENSION}"
        
        fps = fps or self.fps or config.DEFAULT_FPS
        
        # Get list of frames
        frame_files = sorted(frames_dir.glob("frame_*.jpg"))
        
        if not frame_files:
            raise ValueError(f"No frames found in {frames_dir}")
        
        # Read first frame to get dimensions if not provided
        if frame_size is None:
            first_frame = cv2.imread(str(frame_files[0]))
            frame_size = (first_frame.shape[1], first_frame.shape[0])
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*config.VIDEO_CODEC)
        out = cv2.VideoWriter(str(output_path), fourcc, fps, frame_size)
        
        # Write frames
        with tqdm(total=len(frame_files), desc="Stitching video", unit="frame") as pbar:
            for frame_file in frame_files:
                frame = cv2.imread(str(frame_file))
                
                # Resize if needed
                if (frame.shape[1], frame.shape[0]) != frame_size:
                    frame = cv2.resize(frame, frame_size)
                
                out.write(frame)
                pbar.update(1)
        
        out.release()
        print(f"✅ Video saved to {output_path}\n")
        
        return str(output_path)
    
    def _clear_directory(self, directory: Path):
        """Clear all files in directory."""
        if directory.exists():
            for file in directory.glob("*"):
                if file.is_file():
                    file.unlink()
    
    @staticmethod
    def get_frame_files(directory: Path) -> List[Path]:
        """Get sorted list of frame files from directory."""
        return sorted(directory.glob("frame_*.jpg"))
