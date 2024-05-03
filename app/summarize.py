"""
File: app.summarize.py
Description: This script summarizes the content of a transcription file using the Ollama API.
"""

import argparse
import json
import logging
import subprocess
import time
from pathlib import Path

import psutil
import requests

logger = logging.getLogger(__name__)


def summarize_transcription(transcription_file) -> str:
    """
    Summarizes the content of a transcription file using Ollama.

    Args:
        transcription_file (str): The path to the transcription file.

    Returns:
        None
    """
    ollama_started_here = False
    ollama_pid = None
    try:
        ollama_pid = get_ollama_pid()

        # Check if Ollama is running on 127.0.0.1:11434 using "lsof -i :11434"
        if not is_ollama_running():
            print("Ollama is not running. Starting in the background...")
            ollama_pid = start_ollama()
            ollama_started_here = True
            while not is_ollama_running():
                time.sleep(1)
            print(f"Ollama started with PID: {ollama_pid}")
        else:
            print(f"Ollama is running already, pid: {ollama_pid}")

        transcription_file = Path(transcription_file)
        if not transcription_file.exists():
            print(f"File not found: {transcription_file}")
            return

        output_path = (
            transcription_file.parent / f"{transcription_file.stem}_summary.txt"
        )

        with open(transcription_file, "r", encoding="utf-8") as file:
            file_content = file.read()  # .replace("\n", "|").replace('"', '\\"')

        data = {
            "model": "llama3",
            "prompt": "Provide a summary in Swedish of the following transcript. "
            "Provide _only_ a summary, it must be in Swedish and you must not reply "
            f"with anything but the summary.\n\n{file_content}",
            "options": {
                "stop": ["assistant"],
            },
        }

        response = requests.post(
            "http://localhost:11434/api/generate", json=data, stream=True, timeout=3600
        )

        if response.status_code == 200:
            if output_path.exists():
                logger.info("Removing existing summary file: %s", output_path)
                output_path.unlink()
            if not output_path.parent.exists():
                output_path.parent.mkdir(parents=True)
            with open(output_path, "a", encoding="utf-8") as output_file:
                print("Summary:")
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode("utf-8")
                        json_line = json.loads(decoded_line)
                        output_file.write(json_line.get("response", ""))
                        output_file.flush()
                        print(json_line.get("response", ""), end="", flush=True)
                print("")
            print(f"Summary saved to {output_path.resolve()}")
        else:
            print(f"Response: {response.text}")
            print("Failed to summarize transcription.")

    finally:
        if ollama_started_here:
            print("Stopping Ollama on PID:", ollama_pid)
            subprocess.run(
                ["kill", str(ollama_pid)],
                check=True,
            )

    return output_path.resolve()


def query(question: str) -> str:
    """
    Queries Ollama with a question and returns the response as a text string.

    Args:
        question (str): The question to ask Ollama.

    Returns:
        str: The response from Ollama.
    """

    ollama_started_here = False
    ollama_pid = None
    response_text = ""
    try:
        ollama_pid = get_ollama_pid()

        # Check if Ollama is running on 127.0.0.1:11434 using "lsof -i :11434"
        if not is_ollama_running():
            logger.info("Ollama is not running. Starting in the background...")
            ollama_pid = start_ollama()
            ollama_started_here = True
            while not is_ollama_running():
                time.sleep(1)
            logger.info("Ollama started with PID: %s", ollama_pid)
        else:
            logger.debug("Ollama is running already, pid: %s", ollama_pid)

        data = {
            "model": "llama3",
            "prompt": question,
            "options": {
                "stop": ["assistant"],
            },
        }

        response = requests.post(
            "http://localhost:11434/api/generate", json=data, stream=True, timeout=3600
        )

        if response.status_code == 200:
            response_text = ""
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode("utf-8")
                    json_line = json.loads(decoded_line)
                    response_text += json_line.get("response", "")
            return response_text
        else:
            logger.error("Response: %s", response.text)
            logger.error("Failed to query Ollama.")
    except Exception:  # pylint: disable=broad-except
        logger.exception("Failed to query Ollama.")
    finally:
        if ollama_started_here:
            logger.info("Stopping Ollama on PID: %s", ollama_pid)
            subprocess.run(
                ["kill", str(ollama_pid)],
                check=True,
            )

    return response_text


def get_ollama_pid() -> int:
    """
    Returns the PID of the Ollama server process.

    Returns:
        int: The PID of the Ollama server process, or None if it is not running.
    """
    for proc in psutil.process_iter(["pid", "name"]):
        if proc.info["name"] == "ollama":
            return proc.info["pid"]
    return None


def is_ollama_running() -> bool:
    """
    Checks if the Ollama service is running by checking if port 11434 is in use.

    Returns:
        bool: True if the Ollama service is running, False otherwise.
    """
    return get_ollama_pid() is not None


def start_ollama() -> int:
    """
    Starts the Ollama server.

    This function uses the `subprocess.Popen` method to start the Ollama server.
    It executes the command `ollama serve` in a new process.

    Note: Make sure the `ollama` command is available in the system's PATH.

    Returns:
        int: The process ID (PID) of the Ollama server.
    """
    process = subprocess.Popen(
        ["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    return process.pid


def parse_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="The file to summarize")

    parsed_args = parser.parse_args()

    # Print help if no arguments are provided
    if not parsed_args.file:
        parser.print_help()
        exit(1)
    return parsed_args


if __name__ == "__main__":
    args = parse_args()

    summarize_transcription(args.file)
