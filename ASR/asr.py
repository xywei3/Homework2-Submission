import whisper
from pathlib import Path
import json

def generate_transcripts(dir, audio_files):
    successful = 0
    failed = 0
    talks = []
    model = whisper.load_model("turbo")

    for i, audio_path in enumerate(audio_files, 1):
        audio_file = dir + '/' + audio_path.name
        try:
            result = model.transcribe(audio_file, fp16=False)
            segments = result['segments']
            new_segments = []
            for segment in segments:
                filtered_segment = {'timestamp': f"{segment['start']} - {segment['end']}", 'text': segment['text']}
                new_segments.append(filtered_segment)
            
            talk = {
                'audio_title': audio_path.name,
                'audio_text': result['text'],
                'segments': new_segments
            }
            talks.append(talk)
            print(f"✓ Success reading audio file {audio_file}")
            successful += 1
        except Exception as e:
            print(f"✗ Error reading audio file {audio_file}: {str(e)}")
            failed += 1

    print(f"Successfully generated transcripts: {successful}")
    print(f"Failed: {failed}")

    return talks


def main():
    input_dir = 'youtube_audios'
    audio_files = list(Path(input_dir).glob('*.mp3'))
    output_file = 'talks_transcripts.jsonl'
    
    if not audio_files:
        print(f"No audio files found in {input_dir}")
        return
    
    print(f"Found {len(audio_files)} audio files to convert")

    transcripts = generate_transcripts(input_dir, audio_files)

    with open(output_file, 'w') as f:
        for transcript in transcripts:
            f.write(json.dumps(transcript) + '\n')
    
    print(f"Successfully saved to {output_file}")
    

if __name__ == "__main__":
    main()
