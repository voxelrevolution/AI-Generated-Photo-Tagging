import os
import json
import piexif
import logging
from tkinter import filedialog, messagebox
from PIL import Image

from app.config import DIR_CONFIG


def select_folder_path():
    """Opens a dialog to select a folder and returns the path."""
    folder_selected = filedialog.askdirectory()
    return folder_selected


def get_image_files(folder_path):
    """Returns a sorted list of image files from a given folder."""
    if not folder_path:
        return []
    try:
        logging.info(f"Scanning for images in {folder_path}")
        files = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))
        ]
        files.sort()
        logging.info(f"Found {len(files)} image files.")
        return files
    except FileNotFoundError:
        logging.error(f"Folder not found during image scan: {folder_path}")
        messagebox.showerror("Error", f"Folder not found: {folder_path}")
        return []
    except Exception as e:
        logging.error(f"An error occurred while reading the folder: {e}", exc_info=True)
        messagebox.showerror("Error", f"An error occurred while reading the folder: {e}")
        return []


def commit_session_changes(folder_path, session_log, rotation_states):
    """
    Commits all decisions from the session log to the filesystem.

    - Moves 'kept' images to a 'kept' subfolder.
    - Moves 'deleted' images to a 'deleted' subfolder.
    - Writes tags to EXIF data for kept images.
    - Applies rotations to kept images before saving.
    - Creates a JSON log of kept files and their tags.

    Args:
        folder_path (str): The root folder for the session.
        session_log (dict): Mapping image paths to decisions and tags.
        rotation_states (dict): Mapping image paths to rotation angles.

    Returns:
        str: A summary of the operations performed.

    Raises:
        RuntimeError: If a critical error occurs during the commit process.
    """
    if not session_log:
        logging.warning("Commit called with an empty session log.")
        return "No changes to commit."

    kept_count = 0
    deleted_count = 0
    errors = []
    kept_log = {}

    try:
        kept_dir = os.path.join(folder_path, DIR_CONFIG["kept_dir_name"])
        deleted_dir = os.path.join(folder_path, DIR_CONFIG["deleted_dir_name"])
        logging.info(f"Creating output directories: '{kept_dir}' and '{deleted_dir}'")
        os.makedirs(kept_dir, exist_ok=True)
        os.makedirs(deleted_dir, exist_ok=True)

        for image_path, data in session_log.items():
            action = data.get('action')
            tags = data.get('tags', '')
            filename = os.path.basename(image_path)

            try:
                if action == 'keep':
                    logging.info(f"Processing 'keep' for {filename}")

                    # Apply rotation before saving and writing EXIF
                    rotation_angle = rotation_states.get(image_path, 0)
                    _save_with_rotation_and_tags(image_path, kept_dir, rotation_angle, tags, errors)

                    kept_log[filename] = {'tags': tags}
                    kept_count += 1

                elif action == 'delete':
                    logging.info(f"Processing 'delete' for {filename}")
                    dest_path = os.path.join(deleted_dir, filename)
                    os.rename(image_path, dest_path)
                    deleted_count += 1

            except FileNotFoundError:
                msg = f"Warning: Could not find {filename}. It may have been moved."
                logging.warning(msg)
                errors.append(msg)
            except Exception as e:
                msg = f"Error processing {filename}: {e}"
                logging.error(msg, exc_info=True)
                errors.append(msg)

        if kept_log:
            log_path = os.path.join(os.path.dirname(kept_dir), DIR_CONFIG["log_filename"])
            logging.info(f"Writing session log to {log_path}")
            with open(log_path, 'w') as f:
                json.dump(kept_log, f, indent=2)

        summary = (
            f"Commit Complete!\n"
            f"- {kept_count} kept.\n"
            f"- {deleted_count} deleted."
        )
        if errors:
            summary += "\n\nIssues:\n- " + "\n- ".join(errors)
        return summary

    except Exception as e:
        logging.error(f"A critical error occurred during commit: {e}", exc_info=True)
        raise RuntimeError(f"A critical error occurred during commit: {e}")


def _save_with_rotation_and_tags(original_path, dest_dir, angle, tags, errors):
    """
    Opens an image, applies rotation, saves it to the destination,
    and then writes EXIF tags to the new file.
    """
    filename = os.path.basename(original_path)
    dest_path = os.path.join(dest_dir, filename)
    try:
        logging.info(f"Opening {filename} for rotation and saving.")
        img = Image.open(original_path)

        if angle != 0:
            logging.info(f"Rotating {filename} by {angle} degrees.")
            # expand=True resizes canvas to fit the rotated image
            img = img.rotate(-angle, expand=True)

        logging.info(f"Saving rotated image to {dest_path}")
        img.save(dest_path)
        img.close()

        if tags:
            _write_exif_tags(dest_path, tags, errors)

        # Remove the original after a successful copy/tag
        os.remove(original_path)

    except Exception as e:
        msg = f"Failed to save/rotate/tag {filename}: {e}"
        logging.error(msg, exc_info=True)
        errors.append(msg)


def _write_exif_tags(image_path, tags, errors):
    """
    Helper function to write tags to a file's EXIF data.

    The tags are stored in the ``UserComment`` EXIF field using the
    ASCII encoding prefix required by the EXIF spec.
    """
    try:
        logging.info(f"Writing EXIF tags to {os.path.basename(image_path)}")
        # Load existing EXIF or start with an empty dict
        try:
            exif_dict = piexif.load(image_path)
        except piexif.InvalidImageDataError:
            logging.warning(
                f"No existing EXIF data in {os.path.basename(image_path)}. Creating new EXIF data."
            )
            exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}

        comment_bytes = tags.encode('utf-8')
        # EXIF UserComment format: 8-byte charset identifier + comment
        exif_dict['Exif'][piexif.ExifIFD.UserComment] = b'ASCII\x00\x00\x00' + comment_bytes

        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, image_path)

    except Exception as e:
        msg = f"Warning: Could not write EXIF data to {os.path.basename(image_path)}. Error: {e}"
        logging.warning(msg, exc_info=True)
        errors.append(msg)
