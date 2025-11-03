import os
from pathlib import Path
import yt_dlp

def download_youtube_audio(url, output_dir):
    """
    Download audio from a YouTube video.
    
    Args:
        url: YouTube video URL
        output_dir: Directory where audio files will be saved
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Configure yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(output_dir, '%(title)s [%(id)s].%(ext)s'),
            'quiet': False,
            'no_warnings': False,
        }
        
        # Download the audio
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Unknown')
            video_id = info.get('id', 'Unknown')
            print(f"✓ Successfully downloaded: {title} [{video_id}]")
            return True
            
    except Exception as e:
        print(f"✗ Error downloading {url}: {str(e)}")
        return False

def download_all_youtube_audios(links_file, output_dir):
    """
    Download audio from all YouTube URLs in the links file.
    
    Args:
        links_file: Path to text file containing YouTube URLs (one per line)
        output_dir: Directory where audio files will be saved
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Read all URLs from the file
    try:
        with open(links_file, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: Could not find {links_file}")
        return
    
    if not urls:
        print(f"No URLs found in {links_file}")
        return
    
    print(f"Found {len(urls)} YouTube URL(s) to download")
    print(f"{'='*60}\n")
    
    successful = 0
    failed = 0
    
    # Download each video's audio
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Processing: {url}")
        
        if download_youtube_audio(url, output_dir):
            successful += 1
        else:
            failed += 1
        
        print()  # Empty line for readability
    
    print(f"{'='*60}")
    print(f"Download complete!")
    print(f"Successfully downloaded: {successful}")
    print(f"Failed: {failed}")
    print(f"Output directory: {output_dir}")
    print(f"{'='*60}")

def main():
    # Define input file and output directory
    links_file = 'links.txt'
    output_dir = 'youtube_audios'
    
    print("YouTube Audio Downloader")
    print(f"{'='*60}")
    print(f"Links file: {links_file}")
    print(f"Output directory: {output_dir}")
    print(f"{'='*60}\n")
    
    download_all_youtube_audios(links_file, output_dir)

if __name__ == "__main__":
    main()
