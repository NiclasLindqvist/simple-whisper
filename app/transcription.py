"""
File: app.transcription.py
Description: This script transcribes an MP3 file using the whisper executable.
"""

import argparse
import logging
import os
import subprocess
from pathlib import Path

from ffmpeg import FFmpeg

logger = logging.getLogger(__name__)


# Parse command line arguments
def parse_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_file", help="MP3 file to convert", required=True)
    parser.add_argument("-l", "--language", help="Language", default="sv")
    parser.add_argument(
        "-m", "--model", help="Model", default=".models/ggml-large-v3-q5_0.bin"
    )
    parser.add_argument(
        "-w", "--whisper_path", help="Whisper path", default="../whisper.cpp/main"
    )
    parsed_args = parser.parse_args()
    if not parsed_args.input_file:
        parser.print_help()
        exit(1)

    return parsed_args


def transcribe_mp3(
    input_file: str,
    language: str = "sv",
    model: str = "./models/ggml-large-v3-q5_0.bin",
    whisper_path: str = "../whisper.cpp/main",
) -> list[str]:
    """
    Transcribe an MP3 file using the whisper executable.
    """

    output_file = None

    try:
        # Check if the whisper executable exists at the specified path
        whisper_path = Path(whisper_path)
        if not whisper_path.exists() or not whisper_path.is_file():
            logger.info("Whisper executable not found: %s", whisper_path)
            logger.info("Please specify the correct path to the whisper executable.")
            logger.info(
                "If you don't have the whisper executable, you need to clone the repository and compile it."
            )
            logger.info("")
            logger.info(
                "Do you want to clone the repository (if necessary) and compile it? (y/N)"
            )
            choice = input()
            if choice.lower() == "y":
                logger.debug("Checking if the whisper repository exists...")
                whisper_repo_path = Path("../whisper.cpp")
                if whisper_repo_path.exists() and whisper_repo_path.is_dir():
                    logger.debug(
                        "Whisper repository found at %s. No cloning needed!",
                        whisper_repo_path.resolve(),
                    )
                else:
                    logger.debug("Cloning the whisper repository...")
                    subprocess.run(
                        [
                            "git",
                            "clone",
                            "https://github.com/ggerganov/whisper.cpp.git",
                        ],
                        cwd=Path(".."),
                        check=True,
                        capture_output=True,
                    )
                logger.debug("Compiling the whisper executable...")
                subprocess.run(
                    ["make"],
                    cwd=Path("../whisper.cpp"),
                    check=True,
                    capture_output=True,
                )
                whisper_path = Path("../whisper.cpp/main")
                if not whisper_path.exists() or not whisper_path.is_file():
                    logger.error("Compilation failed.")
                    exit(1)
                else:
                    logger.info(
                        "Compilation successful. Continuing with the transcription."
                    )
            else:
                logger.info(
                    "User chose not to clone and compile the whisper repository, exiting."
                )
                exit(1)

        # Check if the input file exists
        input_file_path = Path(input_file)
        if not input_file_path.exists() or not input_file_path.is_file():
            logger.error("File not found: %s", input_file_path)
            exit(1)

        # Create the output file name by replacing the extension
        x_input_file = input_file_path.stem
        output_file = f"./tmp/{x_input_file}.wav"
        if not Path(output_file).parent.exists():
            os.makedirs(Path(output_file).parent, exist_ok=True)

        ffmpeg = FFmpeg()
        ffmpeg.option("y")
        ffmpeg.input(input_file_path)
        ffmpeg.output(output_file, ar=16000)
        ffmpeg.execute()

        # Check if the conversion was successful
        if not os.path.isfile(output_file):
            logger.error("Conversion failed. %s", ffmpeg)
            exit(1)

        # Transcribe the output file
        output_files_path = input_file_path.parent.parent / "outputs" / x_input_file
        transcription_command = [
            str(whisper_path),
            "-m",
            model,
            "-f",
            output_file,
            "-l",
            language,
            "-ovtt",
            "-otxt",
            "-of",
            str(output_files_path),
        ]
        subprocess.run(transcription_command, check=True, capture_output=True)
        logger.debug(
            "Transcription finished. Output files: %s.vtt, %s.txt",
            output_files_path.resolve(),
            output_files_path.resolve(),
        )
    finally:
        # Clean up the temporary WAV file
        if output_file and os.path.isfile(output_file):
            logger.debug("Removing temporary file: %s", output_file)
            os.remove(output_file)
    return [output_files_path.with_suffix(sfx).resolve() for sfx in [".vtt", ".txt"]]


if __name__ == "__main__":
    args = parse_args()

    transcribe_mp3(
        args.input_file,
        language=args.language,
        model=args.model,
        whisper_path=args.whisper_path,
    )
