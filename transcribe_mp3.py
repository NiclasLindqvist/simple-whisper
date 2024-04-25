#!/usr/bin/env python3

import argparse
import os
import subprocess


# Parse command line arguments
def parse_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_file", help="MP3 file to convert", required=True)
    parser.add_argument("-l", "--language", help="Language", default="sv")
    parser.add_argument("-m", "--model", help="Model", default="ggml-large-v3-q5_0.bin")
    parser.add_argument("-f", "--input_folder", help="Input folder", default="/audios")
    parser.add_argument(
        "-o", "--output_folder", help="Output folder", default="/outputs"
    )
    parser.add_argument(
        "-n", "--models_folder", help="Models folder", default="/models"
    )
    parser.add_argument(
        "-w", "--whisper_path", help="Whisper path", default="../whisper.cpp/main"
    )
    return parser.parse_args()


def transcribe_mp3(
    input_file: str,
    language: str = "sv",
    model: str = "ggml-large-v3-q5_0.bin",
    input_folder: str = "/audios",
    output_folder: str = "/outputs",
    models_folder: str = "/models",
    whisper_path: str = "../whisper.cpp/main",
):
    """
    Transcribe an MP3 file using the whisper executable.
    """
    # Check if the input file exists
    input_file_path = os.path.join(input_folder, input_file)
    if not os.path.isfile(input_file_path):
        print(f"File not found: {input_file_path}")
        exit(1)

    # Create the output file name by replacing the extension
    x_input_file = os.path.splitext(os.path.basename(input_file))[0]
    output_file = f"/tmp/{x_input_file}.wav"

    # Use ffmpeg to convert the file
    subprocess.run(
        ["ffmpeg", "-i", input_file_path, "-ar", "16000", output_file],
        check=True,
        capture_output=True,
    )

    # Check if the conversion was successful
    if os.path.isfile(output_file):
        print(f"Conversion successful. Output file: {output_file}")
    else:
        print("Conversion failed.")
        exit(1)

    # Transcribe the output file
    transcription_command = [
        whisper_path,
        "-m",
        os.path.join(models_folder, model),
        "-f",
        output_file,
        "-l",
        language,
        "-ovtt",
        "-otxt",
        "-of",
        os.path.join(output_folder, x_input_file),
    ]
    subprocess.run(transcription_command, check=True, capture_output=True)

    print(
        f"Transcription finished. Output files: {x_input_file}.vtt, {x_input_file}.txt"
    )


if __name__ == "__main__":
    args = parse_args()

    transcribe_mp3(
        args.input_file,
        language=args.language,
        model=args.model,
        input_folder=args.input_folder,
        output_folder=args.output_folder,
        models_folder=args.models_folder,
        whisper_path=args.whisper_path,
    )
