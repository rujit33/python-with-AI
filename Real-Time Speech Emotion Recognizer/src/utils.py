'''Utility functions for audio processing and format conversion for inference 
'''

import subprocess
import os
import uuid

def convert_to_wav(input_path):
    """
    Converts ANY audio/video file into standardized WAV format
    """

    output_path = os.path.join("temp", f"{uuid.uuid4().hex}.wav")
    os.makedirs("temp", exist_ok=True)

    command = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-ac", "1",        # mono
        "-ar", "16000",    # 16kHz (standard for speech ML)
        "-vn",             # ignore video if present
        output_path
    ]

    try:
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return output_path
    except subprocess.CalledProcessError as e:
        print("[FFMPEG ERROR]", e)
        return None