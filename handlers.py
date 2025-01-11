import logging
import os
import shutil
import subprocess
from mediatype import MediaType
from config import (
    WATCH_FOLDER,
    PUID,
    PGID,
    MOVIES_FOLDER,
    SHOWS_FOLDER,
    AUDIOBOOKS_FOLDER,
    EBOOKS_FOLDER,
    KINDLE_EMAIL,
    FROM_EMAIL,
    FROM_EMAIL_PASSWORD,
)
from email_utils import send_email_with_attachment


def change_ownership(filepath, user="", group=""):
    """Run chown command to change ownership of a folder."""
    if not user and not group:
        return
    try:
        subprocess.run(["sudo", "chown", f"{user}:{group}", "-R", filepath], check=True)
        logging.info(f"Ownership changed for: {filepath}")
    except subprocess.CalledProcessError as e:
        logging.warning(f"Error changing ownership for {filepath}: {e}")


class BaseHandler:
    FOLDER_PATHS = {
        MediaType.MOVIE: MOVIES_FOLDER,
        MediaType.TV_SHOW: SHOWS_FOLDER,
        MediaType.AUDIOBOOK: AUDIOBOOKS_FOLDER,
        MediaType.EBOOK: EBOOKS_FOLDER,
    }

    def __init__(self, media_type: MediaType):
        self.media_type = media_type

    def get_destination_path(self, file: str) -> str:
        return os.path.join(self.FOLDER_PATHS[self.media_type], file)

    def move(self, file: str):
        src_path = os.path.join(WATCH_FOLDER, file)
        dest_path = self.get_destination_path(file)
        change_ownership(src_path, PUID, PGID)
        shutil.move(src_path, dest_path)
        logging.info(f"Moved {file} to {dest_path}")

    def handle(self, file: str):
        self.move(file)

    @classmethod
    def get_handler(cls, media_type: MediaType):
        return {
            MediaType.MOVIE: MovieHandler,
            MediaType.TV_SHOW: TVShowHandler,
            MediaType.AUDIOBOOK: AudiobookHandler,
            MediaType.EBOOK: EbookHandler,
        }[media_type]()


class MovieHandler(BaseHandler):
    def __init__(self):
        super().__init__(MediaType.MOVIE)


class TVShowHandler(BaseHandler):
    def __init__(self):
        super().__init__(MediaType.TV_SHOW)


class AudiobookHandler(BaseHandler):
    def __init__(self):
        super().__init__(MediaType.AUDIOBOOK)


class EbookHandler(BaseHandler):
    def __init__(self):
        super().__init__(MediaType.EBOOK)

    def handle(self, file: str):
        super().handle(file)
        file_path = self.get_destination_path(file)
        if os.path.isdir(file_path):
            for root, _, files in os.walk(file_path):
                for f in files:
                    if f.endswith(".epub"):
                        self.send_email_with_attachment(os.path.join(root, f))
                        return
        elif file_path.endswith(".epub"):
            self.send_email_with_attachment(file_path)

    def send_email_with_attachment(self, file_path: str):
        subject = f"{os.path.basename(file_path)}"
        body = ""
        to_email = KINDLE_EMAIL
        from_email = FROM_EMAIL
        from_password = FROM_EMAIL_PASSWORD

        if not all([to_email, from_email, from_password]):
            logging.error("Email configuration is incomplete.")
            return

        logging.info(f"Sending email with attachment: {file_path}")
        send_email_with_attachment(
            subject, body, to_email, from_email, from_password, file_path
        )
