import google.generativeai as genai
import json
import logging
import os
import re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from handlers import BaseHandler
from mediatype import MediaType
from config import WATCH_FOLDER, GENAI_API_KEY

genai.configure(api_key=GENAI_API_KEY)


def classify_titles(titles: list[str]) -> list[dict]:
    """
    Classifies a list of titles using the Gemini API.

    Args:
        titles: A list of strings, where each string is a title to be classified.

    Returns:
        A list of dictionaries, where each dictionary represents a title and its classification.
        Returns an error message if any of the API calls fail.
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    results = []
    for title in titles:
        media_types = [f"'{media.value.lower()}'" for media in MediaType]
        media_types_str = ", ".join(media_types[:-1])
        media_types_str = f"{media_types_str}, or {media_types[-1]}"

        try:
            prompt = (
                f"Classify the following titles as {media_types_str}:\n\n{title}\n\n"
                "Respond only in JSON format with the keys 'title' and 'classification' where classification is "
                "one of {media_types_str}."
            )
            logging.info(prompt)
            response_json = model.generate_content(prompt).text
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


def identify_title(file):
    classification_results = classify_titles([file])
    if classification_results:
        return (
            classification_results[0]["title"],
            classification_results[0]["classification"],
        )
    logging.warning(f"Failed to classify folder: {file}")
    return None, "unknown"


class NewFileHandler(FileSystemEventHandler):
    """Handle new file events."""

    def on_created(self, event):
        file = os.path.basename(event.src_path)
        logging.info(f"New file detected: {file}")
        _, media_type = identify_title(file)
        if not media_type or media_type.lower() not in MediaType:
            logging.warning(f"Unknown media type {media_type} for file: {file}")
            return
        handler = BaseHandler.get_handler(MediaType(media_type.lower()))
        handler.handle(file)


def monitor_folder():
    """Monitor the 'completed' folder for new files."""
    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path=WATCH_FOLDER, recursive=False)
    observer.start()
    logging.info(f"Monitoring '{WATCH_FOLDER}' for new files...")
    try:
        observer.join()
    except KeyboardInterrupt:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    monitor_folder()
