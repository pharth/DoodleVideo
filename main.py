"""Main CLI application for video scribble generation."""

import argparse
import sys
from pathlib import Path
import config
from video_processor import VideoProcessor
from scribble_generator import ScribbleGenerator


def print_banner():
    """Print application banner."""
    banner = """
    ╔════════════════════════════════════════╗
    ║   🎨 Video Scribble Generator 🎨      ║
    ║   Transform videos with AI doodles!    ║
    ╚════════════════════════════════════════╝
    """
    print(banner)


def validate_video_file(video_path: str) -> Path:
    """Validate that video file exists."""
    path = Path(video_path)
    
    if not path.exists():
        print(f"❌ Error: Video file not found: {video_path}")
        sys.exit(1)
    
    if path.suffix.lower() not in ['.mp4', '.avi', '.mov', '.mkv']:
        print(f"❌ Error: Unsupported video format: {path.suffix}")
        print("   Supported formats: .mp4, .avi, .mov, .mkv")
        sys.exit(1)
    
    return path


def main():
    """Main application entry point."""
    print_banner()
    
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Generate scribbled videos using AI or procedural methods"
    )
    parser.add_argument(
        "video",
        nargs="?",
        help="Path to input video file (or place video in 'input/' folder)"
    )
    parser.add_argument(
        "--mode",
        choices=["ai", "experimental"],
        default="ai",
        help="Generation mode: 'ai' (Gemini) or 'experimental' (procedural)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between AI requests in seconds (default: 1.0)"
    )
    parser.add_argument(
        "--output",
        help="Custom output video path (default: output/scribbled_<input_name>.mp4)"
    )
    parser.add_argument(
        "--duration",
        type=float,
        help="Process only first N seconds of video (e.g., --duration 3)"
    )
    
    args = parser.parse_args()
    
    # Get video path
    if args.video:
        video_path = validate_video_file(args.video)
    else:
        # Look for video in input folder
        videos = list(config.INPUT_DIR.glob("*.mp4")) + \
                 list(config.INPUT_DIR.glob("*.avi")) + \
                 list(config.INPUT_DIR.glob("*.mov"))
        
        if not videos:
            print("❌ No video file specified and none found in 'input/' folder.")
            print("\nUsage:")
            print("  python main.py <video_file>")
            print("  python main.py --mode experimental")
            print("\nOr place a video file in the 'input/' folder and run without arguments.")
            sys.exit(1)
        
        if len(videos) > 1:
            print("📁 Multiple videos found in 'input/' folder:")
            for i, v in enumerate(videos, 1):
                print(f"   {i}. {v.name}")
            
            choice = input("\nSelect video number: ").strip()
            try:
                video_path = videos[int(choice) - 1]
            except (ValueError, IndexError):
                print("❌ Invalid selection")
                sys.exit(1)
        else:
            video_path = videos[0]
    
    print(f"📹 Input video: {video_path}\n")
    print(f"🎨 Mode: {args.mode.upper()}\n")
    print("=" * 50)
    
    try:
        # Step 1: Extract frames
        print("\n🎬 STEP 1: Extracting frames from video...")
        print("=" * 50)
        processor = VideoProcessor(video_path)
        max_duration = args.duration if args.duration else config.MAX_DURATION_SECONDS
        total_frames, fps, frame_size = processor.extract_frames(max_duration=max_duration)
        
        # Step 2: Generate scribbles
        print("\n🎨 STEP 2: Generating scribbles on each frame...")
        print("=" * 50)
        generator = ScribbleGenerator(mode=args.mode)
        generator.process_frames(delay_between_requests=args.delay)
        
        # Step 3: Stitch video
        print("\n🎬 STEP 3: Stitching frames into final video...")
        print("=" * 50)
        output_path = processor.stitch_frames(output_path=args.output)
        
        # Success!
        print("\n" + "=" * 50)
        print("✨ SUCCESS! ✨")
        print("=" * 50)
        print(f"📹 Original video: {video_path}")
        print(f"🎨 Scribbled video: {output_path}")
        print(f"📊 Total frames processed: {total_frames}")
        print(f"⏱️  FPS: {fps}")
        print(f"📐 Resolution: {frame_size[0]}x{frame_size[1]}")
        print("\n🎉 Your scribbled video is ready to watch!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
