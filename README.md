# Video Scribble Generator 🎨

Transform your videos with colorful, playful scribbles and doodles using AI or procedural generation!

## Features

- 🎬 **Frame Extraction**: Automatically split videos into individual frames
- 🎨 **AI Scribbles**: Use Google's Gemini 2.0 Flash model to generate creative doodles
- 🔬 **Experimental Mode**: Procedural scribble generation for faster processing
- 🎥 **Video Reconstruction**: Stitch processed frames back into video
- 💫 **Random Variations**: Each frame gets unique, randomized scribbles

## Installation

1. **Clone or navigate to the project**:
   ```bash
   cd TakeTwoAssignment
   ```

2. **Create virtual environment** (recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up API key**:
   - Copy `.env.template` to `.env`
   - Get your Google AI Studio API key from: https://makersuite.google.com/app/apikey
   - Add it to `.env`:
     ```
     GOOGLE_API_KEY=your_actual_api_key_here
     ```

## Usage

### Quick Start

Place your video in the `input/` folder and run:
```bash
python main.py
```

### Specify Video File

```bash
python main.py path/to/your/video.mp4
```

### Modes

**AI Mode (Default)** - Uses Gemini AI for creative scribbles:
```bash
python main.py --mode ai
```

**Experimental Mode** - Fast procedural generation:
```bash
python main.py --mode experimental
```

### Advanced Options

```bash
python main.py video.mp4 --mode ai --delay 1.5 --output custom_output.mp4
```

Options:
- `--mode`: Choose `ai` or `experimental`
- `--delay`: Delay between AI requests (default: 1.0 seconds)
- `--output`: Custom output video path

## Project Structure

```
TakeTwoAssignment/
├── main.py                 # CLI application
├── video_processor.py      # Frame extraction/stitching
├── scribble_generator.py   # AI & experimental scribble generation
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── .env                   # API keys (create from .env.template)
├── input/                 # Place input videos here
├── output/                # Generated videos saved here
└── temp/                  # Temporary frames (auto-cleaned)
    ├── original/          # Extracted frames
    └── scribbled/         # Processed frames
```

## How It Works

1. **Frame Extraction**: Video is split into individual JPEG frames
2. **Scribble Generation**: 
   - **AI Mode**: Each frame is sent to Gemini with randomized prompts for variety
   - **Experimental Mode**: Procedural algorithms draw stars, swirls, smileys, etc.
3. **Video Reconstruction**: Processed frames are stitched back at original FPS

## Examples

Process a 10-second video with AI:
```bash
python main.py my_video.mp4
```

Quick test with experimental mode:
```bash
python main.py test.mp4 --mode experimental
```

## Tips

- **Short videos work best** (10-15 seconds) for AI mode due to API limits
- **Experimental mode is faster** - great for testing and longer videos
- AI mode adds **~1 second per frame** (adjustable with `--delay`)
- Videos are saved to `output/` folder automatically

## Troubleshooting

**"GOOGLE_API_KEY not found"**:
- Make sure you created `.env` file (not `.env.template`)
- Add your actual API key to `.env`

**API Rate Limits**:
- Increase `--delay` parameter: `python main.py --delay 2.0`
- Use `--mode experimental` for unlimited processing

**Out of Memory**:
- Process shorter videos
- Reduce video resolution before processing

## Requirements

- Python 3.8+
- OpenCV
- Google Generative AI SDK
- Pillow
- See `requirements.txt` for full list

## License

Free to use for personal and commercial projects.

---

Made with ❤️ for creative video transformation!
