"""
File: app.__main__.py
Description: This script transcribes an MP3 file and summarizes the content of the transcription.
"""

import argparse
import logging
from pathlib import Path

import chromadb

from transcription import transcribe_mp3
from summarize import summarize_transcription, query


logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
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
        "--model",
        default="models/ggml-large-v3-q5_0.bin",
        help="The model to use for transcription",
    )

    parsed_args = parser.parse_args()
    if not parsed_args.mp3_file:
        parser.print_help()
        exit(1)

    return parsed_args


def process_transcription(
    mp3_file,
    whisper_path="../whisper.cpp/main",
    model=".models/ggml-large-v3-q5_0.bin",
):
    """
    Process transcription."""

    # outputs = transcribe_mp3(
    #     mp3_file,
    #     "sv",
    #     model,
    #     whisper_path,
    # )
    # summary_output_path = summarize_transcription(outputs[0])
    # logging.info("Summary file saved at: %s", summary_output_path)

    chroma_client = chromadb.PersistentClient(path=str(Path("db")))

    collection = None
    try:
        collection = chroma_client.get_collection("transcriptions")
    except ValueError:
        collection = chroma_client.create_collection("transcriptions")

    # with open(outputs[0], "r", encoding="utf-8") as f:
    #     collection.add(
    #         documents=[f.read()],
    #         # metadatas=[{"summary": summary_output_path}],
    #         ids=[Path(mp3_file).stem],
    #     )

    logging.info("Transcription saved to ChromaDB")
    responses = collection.query(
        query_texts=["What did the person do while contemplating GAD 7?"], n_results=1
    )
    question = (
        f"Context: {', '.join([doc[0] for doc in responses.get('documents', [])])} Question: What did the "
        + "person drink while contemplating GAD 7?"
    )
    print(query(question=question))


if __name__ == "__main__":
    args = parse_args()
    process_transcription(
        mp3_file=args.mp3_file,
        whisper_path=args.whisper_path,
        model=args.model,
    )
