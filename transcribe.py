#!/usr/bin/env python3

import argparse
import subprocess
from transcribe_mp3 import transcribe_mp3


def parse_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description="Transcribe MP3 files.")
    parser.add_argument("mp3_file", help="The MP3 file to transcribe")
    parser.add_argument(
        "--whisper-path",
        default="../whisper.cpp/main",
        help="The path to the whisper executable",
    )
    parser.add_argument(
        "--use-docker", action="store_true", help="Use Docker to run the script"
    )
    parser.add_argument(
        "--model",
        default="ggml-large-v3-q5_0.bin",
        help="The model to use for transcription",
    )
    parser.add_argument(
        "--input_folder",
        default="./audios",
        help="The folder where the MP3 file is located",
    )
    parser.add_argument(
        "--output_folder",
        default="./outputs",
        help="The folder where the output files will be saved",
    )
    parser.add_argument(
        "--models_folder",
        default="./models",
        help="The folder where the models are located",
    )
    return parser.parse_args()


def transcribe(
    mp3_file,
    whisper_path="../whisper.cpp/main",
    use_docker=False,
    model="ggml-large-v3-q5_0.bin",
    input_folder="./audios",
    output_folder="./outputs",
    models_folder="./models",
):
    """
    Transcribe an MP3 file using the whisper executable."""
    # Check if the user wants to use Docker
    if use_docker:
        # Check if Docker is running
        try:
            subprocess.check_output(["docker", "info"], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            print("Docker is not running. Please start Docker and try again.")
            exit(1)

        # Check if the Docker image exists
        try:
            subprocess.check_output(
                ["docker", "image", "inspect", "simple-whisper"],
                stderr=subprocess.STDOUT,
            )
        except subprocess.CalledProcessError:
            print("Docker image simple-whisper not found. Building the image...")
            subprocess.run(["docker", "build", "-t", "simple-whisper", "."])

        docker_command = [
            "docker",
            "run",
            "-it",
            "--rm",
            "-v",
            f"{models_folder}:/models",
            "-v",
            f"{input_folder}:/audios",
            "-v",
            f"{output_folder}:/outputs",
            "simple-whisper",
            "-i",
            mp3_file,
            "-l",
            "sv",
            "-m",
            model,
            "-w",
            "./main",
        ]
        print("Running with Docker:", " ".join(docker_command))
        subprocess.run(docker_command)
    else:
        transcribe_mp3(
            mp3_file,
            "sv",
            model,
            input_folder,
            output_folder,
            models_folder,
            whisper_path,
        )


if __name__ == "__main__":
    args = parse_args()
    transcribe(
        mp3_file=args.mp3_file,
        whisper_path=args.whisper_path,
        use_docker=args.use_docker,
        model=args.model,
        input_folder=args.input_folder,
        output_folder=args.output_folder,
        models_folder=args.models_folder,
    )
