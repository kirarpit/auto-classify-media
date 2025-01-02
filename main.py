import google.generativeai as genai
import json
import logging
import os
import re
import shutil
import subprocess
import typing_extensions as typing
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv


load_dotenv()
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


COMPLETED_FOLDER = os.getenv("COMPLETED_FOLDER", "/path/to/completed")
MOVIES_FOLDER = os.getenv("MOVIES_FOLDER", "/path/to/movies")
SHOWS_FOLDER = os.getenv("SHOWS_FOLDER", "/path/to/shows")
AUDIOBOOKS_FOLDER = os.getenv("AUDIOBOOKS_FOLDER", "/path/to/audiobooks")
PUID = os.getenv("PUID", "")
PGID = os.getenv("PGID", "")
GENAI_API_KEY = os.getenv("GENAI_API_KEY")

if not GENAI_API_KEY:
    logging.error(
        "API key for Generative AI is not set. Please configure GENAI_API_KEY."
    )
    exit(1)

genai.configure(api_key=GENAI_API_KEY)


def classify_titles(titles):
    """
    Classifies a list of titles as either "movie", "tv show", or an "audiobook" using the Gemini API.

    Args:
        titles: A list of strings, where each string is a title to be classified.

    Returns:
        A list of dictionaries, where each dictionary represents a title and its classification.
        Returns an error message if any of the API calls fail.
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    results = []
    for title in titles:
        try:
            prompt = (
                f"Classify the following titles as a 'movie', 'tv show', or 'audiobook':\n\n{title}\n\n"
                "Respond only in JSON format with the keys 'title' and 'classification' where classification is either "
                "'movie', 'tv show', or 'audiobook'."
            )
            logging.info(prompt)
            response = model.generate_content(prompt)
            response_json = response.text
            logging.info(response_json)

            matches = re.findall(r"```\s*json(.*?)\s*```", response_json, re.DOTALL)
            for match in matches:
                try:
                    parsed_json = json.loads(match.strip())
                    logging.info(parsed_json)
                    results.append(parsed_json)
                except json.JSONDecodeError:
                    logging.warning(
                        f"Malformed JSON found in response: {match.strip()}"
                    )
        except Exception as e:
            logging.error(f"Error processing title '{title}': {e}")
    return results


def identify_title(folder_name):
    classification_results = classify_titles([folder_name])
    if classification_results:
        return (
            classification_results[0]["title"],
            classification_results[0]["classification"],
        )
    logging.warning(f"Failed to classify folder: {folder_name}")
    return None, "unknown"


def change_ownership(folder_path):
    """Run chown command to change ownership of a folder."""
    if not (PUID or PGID):
        return
    try:
        subprocess.run(
            ["sudo", "chown", f"{PUID}:{PGID}", "-R", folder_path], check=True
        )
        logging.info(f"Ownership changed for: {folder_path}")
    except subprocess.CalledProcessError as e:
        logging.warning(f"Error changing ownership for {folder_path}: {e}")


def move_folder(folder_name, media_type):
    """Move the folder to the appropriate directory."""
    src_path = os.path.join(COMPLETED_FOLDER, folder_name)
    dest_path = None

    if media_type == "movie":
        dest_path = os.path.join(MOVIES_FOLDER, folder_name)
    elif media_type == "tv show":
        dest_path = os.path.join(SHOWS_FOLDER, folder_name)
    elif media_type == "audiobook":
        dest_path = os.path.join(AUDIOBOOKS_FOLDER, folder_name)

    if not dest_path:
        logging.warning(f"Skipping {folder_name}: Unable to determine media type.")
        return

    change_ownership(src_path)

    if os.path.exists(dest_path):
        logging.warning(f"Destination already exists for {folder_name}, skipping.")
        return

    shutil.move(src_path, dest_path)
    logging.info(f"Moved {folder_name} to {dest_path}")


class NewFolderHandler(FileSystemEventHandler):
    """Handle new folder events."""

    def on_created(self, event):
        if event.is_directory:
            folder_name = os.path.basename(event.src_path)
            logging.info(f"New folder detected: {folder_name}")
            title, media_type = identify_title(folder_name)
            move_folder(folder_name, media_type)


def monitor_folder():
    """Monitor the 'completed' folder for new subfolders."""
    event_handler = NewFolderHandler()
    observer = Observer()
    observer.schedule(event_handler, path=COMPLETED_FOLDER, recursive=False)
    observer.start()
    logging.info(f"Monitoring '{COMPLETED_FOLDER}' for new folders...")
    try:
        observer.join()
    except KeyboardInterrupt:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    monitor_folder()
