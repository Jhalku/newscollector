import argparse
import os
import sys
import glob
import subprocess
import whisper
import yt_dlp
import ffmpeg_downloader as ffdl

ffmpeg_path = os.path.dirname(ffdl.ffmpeg_path)
os.environ["PATH"] += os.pathsep + ffmpeg_path

def download_audio(url, output_dir="."):
    """Download audio from a Twitter URL using yt-dlp."""
    print(f"Downloading audio from {url}...")
    
    # We use a specific output template to avoid conflicts
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, 'audio_%(id)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'ffmpeg_location': ffmpeg_path,
        'quiet': False,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            # The actual downloaded file might be .mp3 due to the postprocessor
            # We can find it by looking for the id
            video_id = info.get('id')
            return video_id
        except Exception as e:
            print(f"Error downloading: {e}")
            sys.exit(1)

def transcribe_audio(audio_path, model_size="base"):
    """Transcribe audio producing both original and translated text."""
    print(f"Loading Whisper model ({model_size})...")
    # For CPU, smaller models are faster. For GPU, any model is fine.
    try:
        model = whisper.load_model(model_size)
    except Exception as e:
        print(f"Error loading model: {e}")
        sys.exit(1)
        
    print(f"Transcribing {audio_path} in original language (Hindi expected)...")
    # Transcribe original (Hindi)
    result_orig = model.transcribe(audio_path)
    orig_text = result_orig["text"]
    
    print("Translating to English...")
    # Translate to English
    result_en = model.transcribe(audio_path, task="translate")
    en_text = result_en["text"]
    
    return orig_text, en_text

def main():
    parser = argparse.ArgumentParser(description="Transcribe a Twitter Video to Hindi and English")
    parser.add_argument("url", help="Twitter (X) video URL")
    parser.add_argument("--model", default="base", help="Whisper model size (tiny, base, small, medium, large)")
    args = parser.parse_args()
    
    # Setup paths
    workspace = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(workspace, "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Download
    video_id = download_audio(args.url, output_dir)
    
    # Find the downloaded file
    search_pattern = os.path.join(output_dir, f"audio_{video_id}.*")
    downloaded_files = glob.glob(search_pattern)
    
    if not downloaded_files:
        print("Could not find the downloaded audio file.")
        sys.exit(1)
        
    audio_path = downloaded_files[0]
    
    # Transcribe and Translate
    orig_text, en_text = transcribe_audio(audio_path, args.model)
    
    # Save results
    orig_path = os.path.join(output_dir, f"{video_id}_original.txt")
    en_path = os.path.join(output_dir, f"{video_id}_english.txt")
    
    with open(orig_path, "w", encoding="utf-8") as f:
        f.write(orig_text)
        
    with open(en_path, "w", encoding="utf-8") as f:
        f.write(en_text)
        
    print(f"\nDone! Results saved to:\n- {orig_path}\n- {en_path}")
    
    # Cleanup audio
    try:
        os.remove(audio_path)
    except Exception as e:
        print(f"Warning: could not delete temporary audio file {audio_path}: {e}")

if __name__ == "__main__":
    main()
