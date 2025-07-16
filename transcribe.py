import os
from faster_whisper import WhisperModel
from post_processor import UrduTextFormatter

model = WhisperModel("large-v3", device="cpu", compute_type="int8")

audio_dir = "audio_files"
transcribed_dir = "transcribed"
for audio_file in os.listdir(audio_dir):
    if audio_file.endswith(".mp3"):
        audio_path = os.path.join(audio_dir, audio_file)
        segments, info = model.transcribe(audio_path, language="ur")
        transcript = "".join(segment.text for segment in segments)
        transcribed_file = os.path.join(transcribed_dir, audio_file.replace(".mp3", ".txt"))
        with open(transcribed_file, "w", encoding="utf-8") as f:
            f.write(transcript)

formatter = UrduTextFormatter()

transcribed_dir = "transcribed"
postprocessed_dir = "postprocessed"
for transcribed_file in os.listdir(transcribed_dir):
    transcribed_path = os.path.join(transcribed_dir, transcribed_file)
    with open(transcribed_path, "r", encoding="utf-8") as f:
        text = f.read()
    formatted_text = formatter.format_transcript(text)
    postprocessed_file = os.path.join(postprocessed_dir, transcribed_file)
    with open(postprocessed_file, "w", encoding="utf-8") as f:
        f.write(formatted_text)            