import os
import shutil
from typing import Optional

from PIL import Image


def save_image(src: str, directory: str, i: int) -> Optional[str]:
    """Save an image file with proper format handling.

    Args:
        src:
            Source path of the image.

        directory:
            Directory to save the image to.

        i:
            Index of the image.

    Returns:
        Format of the image ('PNG' or 'TIFF') or None if format not supported.
    """
    with Image.open(src) as img:
        format = img.format

        if format == "PNG":
            suffix = "png"
        elif format == "TIFF":
            suffix = "tif"
        else:
            return None

        dest = os.path.join(directory, f"{i}.{suffix}")

        try:
            # Try to create a hard link first
            os.link(src, dest)
        except OSError:
            # If linking fails, try to copy the file
            try:
                shutil.copy2(src, dest)
            except Exception as e:
                raise RuntimeError(f"failed to copy from '{src}' to '{dest}': {str(e)}")

        return format
