brew install ffmpeg
pip install yt-dlp

run this command 
yt-dlp -x --audio-format mp3 --batch-file='links.txt' --paths='youtube_audios/'
to fetch the youtube audios

OR

run this command 
python youtube_audio_downloader.py
to fetch the youtube audios

pip install -U openai-whisper

run this command 
python asr.py
to generate the talks_transcripts.jsonl