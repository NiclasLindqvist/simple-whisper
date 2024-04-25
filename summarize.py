import argparse
import json
from pathlib import Path
import subprocess
import time

import requests
import psutil


def summarize_transcription(transcription_file):
    """
    Summarizes the content of a transcription file using Ollama.

    Args:
        transcription_file (str): The path to the transcription file.

    Returns:
        None
    """
    ollama_pid = get_ollama_pid()
    ollama_started_here = False

    # Check if --help or -h is provided or no arguments are given
    if not transcription_file:
        print("Usage: python summarize.py <transcription_file>")
        print("  <transcription_file>          The file to summarize")
        return

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

    output_path = transcription_file.parent / f"{transcription_file.stem}_summary.txt"

    with open(transcription_file, "r", encoding="utf-8") as file:
        file_content = file.read()  # .replace("\n", "|").replace('"', '\\"')

    data = {
        "model": "llama3",
        "prompt": f"Provide a summary in Swedish of the following transcript. Provide _only_ a summary, it must be in Swedish and you must not reply with anything but the summary.\n\n{file_content}",
        "options": {
            "stop": ["assistant"],
        },
    }

    response = requests.post(
        "http://localhost:11434/api/generate", json=data, stream=True
    )

    if response.status_code == 200:
        if output_path.exists():
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

    if ollama_started_here:
        print("Stopping Ollama...")
        subprocess.run(
            ["kill", str(ollama_pid)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="The file to summarize")
    args = parser.parse_args()

    summarize_transcription(args.file)
