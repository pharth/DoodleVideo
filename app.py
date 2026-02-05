"""Streamlit web application for video scribble generation."""

import streamlit as st
import tempfile
import shutil
from pathlib import Path
import os
import time
import cv2
from concurrent.futures import ThreadPoolExecutor, as_completed

import config
from video_processor import VideoProcessor
from scribble_generator import ScribbleGenerator


# Page config
st.set_page_config(
    page_title="Video Scribble Generator",
    page_icon="🎨",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #4ECDC4;
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

def process_single_frame(generator, frame_file, output_file, mode, delay):
    """Process a single frame (used for parallel execution)."""
    if mode == "ai":
        generator._process_frame_ai(frame_file, output_file)
        time.sleep(delay)  # Rate limiting
    else:
        generator._process_frame_experimental(frame_file, output_file)

def process_video(
    video_path: str,
    duration: float,
    target_fps: int,
    original_fps: float,
    mode: str,
    delay: float
):
    """Process video with scribbles."""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Extract frames
        processor = VideoProcessor(video_path)
        
        # Get frame count first
        import cv2
        cap = cv2.VideoCapture(video_path)
        original_total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        frames_to_extract = int(duration * original_fps)
        
        status_text.text(f"📹 Step 1/3: Extracting frames (0/{frames_to_extract})...")
        
        # Extract with progress updates
        total_frames, fps, frame_size = processor.extract_frames(max_duration=duration)
        progress_bar.progress(33)
        
        # Calculate frame skip for FPS reduction
        frame_skip = int(original_fps / target_fps) if target_fps < original_fps else 1
        
        # If FPS reduction needed, subsample frames
        if frame_skip > 1:
            status_text.text(f"🎬 Subsampling frames (every {frame_skip} frames for {target_fps} FPS)...")
            subsample_frames(config.TEMP_ORIGINAL_DIR, frame_skip)
            # Update frame count after subsampling
            remaining_frames = len(list(config.TEMP_ORIGINAL_DIR.glob("frame_*.jpg")))
        else:
            remaining_frames = total_frames
        
        # Step 2: Generate scribbles with progress updates (parallel processing)
        generator = ScribbleGenerator(mode=mode)
        frame_files = sorted(config.TEMP_ORIGINAL_DIR.glob("frame_*.jpg"))
        
        # Process frames in parallel batches
        max_workers = 5 if mode == "ai" else 10  # 5 parallel API calls for AI mode
        completed = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_frame = {}
            for frame_file in frame_files:
                output_file = config.TEMP_SCRIBBLED_DIR / frame_file.name
                future = executor.submit(
                    process_single_frame,
                    generator,
                    frame_file,
                    output_file,
                    mode,
                    delay
                )
                future_to_frame[future] = frame_file
            
            # Process completed tasks
            for future in as_completed(future_to_frame):
                completed += 1
                status_text.text(f"🎨 Step 2/3: Generating scribbles ({completed}/{len(frame_files)})...")
                
                # Update progress (33% to 66%)
                progress_pct = 33 + int((completed / len(frame_files)) * 33)
                progress_bar.progress(progress_pct)
                
                # Check for errors
                try:
                    future.result()
                except Exception as e:
                    print(f"Error processing frame: {e}")
        
        # Step 3: Stitch video with progress updates
        output_dir = config.TEMP_SCRIBBLED_DIR
        output_path = config.OUTPUT_DIR / f"scribbled_output{config.VIDEO_EXTENSION}"
        
        stitch_frames = sorted(output_dir.glob("frame_*.jpg"))
        total_stitch = len(stitch_frames)
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*config.VIDEO_CODEC)
        out = cv2.VideoWriter(str(output_path), fourcc, target_fps, frame_size)
        
        for idx, frame_file in enumerate(stitch_frames, 1):
            status_text.text(f"🎬 Step 3/3: Stitching video ({idx}/{total_stitch})...")
            
            frame = cv2.imread(str(frame_file))
            if (frame.shape[1], frame.shape[0]) != frame_size:
                frame = cv2.resize(frame, frame_size)
            out.write(frame)
            
            # Update progress (66% to 100%)
            progress_pct = 66 + int((idx / total_stitch) * 34)
            progress_bar.progress(progress_pct)
        
        out.release()
        progress_bar.progress(100)
        
        # Clean up temporary frames
        status_text.text("🗑️ Cleaning up temporary files...")
        clear_temp_folders()
        
        status_text.text("✅ Processing complete!")
        
        return str(output_path), True
        
    except Exception as e:
        status_text.text(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, False


def subsample_frames(frames_dir: Path, skip: int):
    """Keep every Nth frame and remove others."""
    frames = sorted(frames_dir.glob("frame_*.jpg"))
    
    frames_to_keep = frames[::skip]
    frames_to_remove = [f for f in frames if f not in frames_to_keep]
    
    # Remove frames
    for frame in frames_to_remove:
        frame.unlink()
    
    # Rename remaining frames sequentially
    for idx, frame in enumerate(sorted(frames_dir.glob("frame_*.jpg"))):
        new_name = frames_dir / f"frame_{idx:05d}.jpg"
        if frame != new_name:
            frame.rename(new_name)


def clear_temp_folders():
    """Clear temporary folders."""
    for folder in [config.TEMP_ORIGINAL_DIR, config.TEMP_SCRIBBLED_DIR]:
        if folder.exists():
            for file in folder.glob("*"):
                if file.is_file():
                    file.unlink()


def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<p class="main-header">🎨 Video Scribble Generator 🎨</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Transform your videos with AI-powered doodles!</p>', unsafe_allow_html=True)
    
    # Sidebar settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        mode = st.selectbox(
            "Generation Mode",
            options=["ai", "experimental"],
            format_func=lambda x: "🤖 AI (Gemini)" if x == "ai" else "🔬 Experimental (Fast)",
            help="AI mode uses Gemini for creative scribbles. Experimental mode is faster."
        )
        
        if mode == "ai":
            delay = st.slider(
                "Delay between API calls (sec)",
                min_value=0.5,
                max_value=3.0,
                value=1.0,
                step=0.1,
                help="Delay to respect API rate limits"
            )
        else:
            delay = 0.5
        
        st.divider()
        
        if st.button("🗑️ Clear Temp Folders"):
            clear_temp_folders()
            st.success("Temp folders cleared!")
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📤 Upload Video")
        uploaded_file = st.file_uploader(
            "Choose a video file",
            type=["mp4", "avi", "mov", "mkv"],
            help="Upload a short video (recommended: 5-15 seconds)"
        )
        
        if uploaded_file is not None:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
                tmp_file.write(uploaded_file.read())
                video_path = tmp_file.name
            
            # Display video info
            st.video(video_path)
            
            # Get video info
            import cv2
            cap = cv2.VideoCapture(video_path)
            original_fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            video_duration = total_frames / original_fps
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
            
            st.info(f"📊 **Video Info**\n\n- Resolution: {width}x{height}\n- FPS: {original_fps:.1f}\n- Duration: {video_duration:.2f} seconds\n- Total Frames: {total_frames}")
            
            # Processing options
            st.subheader("🎛️ Processing Options")
            
            duration = st.number_input(
                "Duration to process (seconds)",
                min_value=1.0,
                max_value=float(video_duration),
                value=min(5.0, video_duration),
                step=1.0,
                help=f"Process first N seconds of video (max: {video_duration:.1f}s)"
            )
            
            # FPS options
            fps_options = [int(original_fps)]
            for divisor in [2, 3, 4, 5, 6]:
                new_fps = int(original_fps / divisor)
                if new_fps >= 10 and new_fps not in fps_options:
                    fps_options.append(new_fps)
            fps_options.sort(reverse=True)
            
            target_fps = st.selectbox(
                "Output FPS (lower = time-lapse effect)",
                options=fps_options,
                help="Reducing FPS creates a time-lapse effect, making the video shorter and faster"
            )
            
            # Calculate output duration
            frames_to_extract = int(duration * original_fps)
            frames_after_skip = frames_to_extract // (int(original_fps / target_fps))
            output_duration = frames_after_skip / target_fps
            
            if target_fps < original_fps:
                st.warning(f"⏱️ Output will be ~{output_duration:.2f} seconds (time-lapse: {duration/output_duration:.1f}x faster)")
            
            # Process button
            if st.button("🚀 Generate Scribbled Video", type="primary", use_container_width=True):
                with col2:
                    st.subheader("🎬 Processing")
                    
                    output_path, success = process_video(
                        video_path,
                        duration,
                        target_fps,
                        original_fps,
                        mode,
                        delay
                    )
                    
                    if success and output_path:
                        st.success("🎉 Video processed successfully!")
                        
                        # Display output video
                        st.video(output_path)
                        
                        # Download button
                        with open(output_path, "rb") as file:
                            st.download_button(
                                label="⬇️ Download Scribbled Video",
                                data=file,
                                file_name=f"scribbled_{uploaded_file.name}",
                                mime="video/mp4",
                                use_container_width=True
                            )
                        
                        # Stats
                        st.info(f"""
                        📊 **Processing Stats**
                        
                        - Input Duration: {duration:.2f}s @ {original_fps:.0f} FPS
                        - Output Duration: {output_duration:.2f}s @ {target_fps} FPS
                        - Frames Processed: {frames_after_skip}
                        - Speed: {(duration/output_duration if output_duration > 0 else 1):.1f}x
                        - Mode: {mode.upper()}
                        """)
                    
                    # Cleanup
                    try:
                        os.unlink(video_path)
                    except:
                        pass
    
    with col2:
        if uploaded_file is None:
            st.subheader("👈 Start by uploading a video")
            st.info("""
            **How it works:**
            
            1. 📤 Upload your video
            2. ⏱️ Choose duration to process
            3. 🎬 Select output FPS (lower for time-lapse)
            4. 🎨 Pick generation mode
            5. 🚀 Click generate!
            
            **Tips:**
            - Start with short videos (5-10 sec)
            - Use experimental mode for testing
            - Lower FPS = faster output video
            """)
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #888;'>
        Made with ❤️ using Streamlit & Google Gemini
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
