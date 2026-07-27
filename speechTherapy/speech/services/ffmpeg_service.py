import subprocess
import os

class FFmpegService:
    @staticmethod
    def to_wav_16k_mono(input_path):
        """
        Converts any input audio to 16kHz mono WAV, which Whisper prefers.
        Returns the path to the converted file.
        """
        output_path = os.path.splitext(input_path)[0] + "_16k.wav"

        command = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-ar", "16000",
            "-ac", "1",
            output_path
        ]

        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg conversion failed: {result.stderr}")

        return output_path