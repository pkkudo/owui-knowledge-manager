import os
import zipfile
import json
import shutil
from utils import settings
from utils.base_logger import logger


def extract_zip(zip_file_path, marker):
    """
    Extract zip file to the specified directory.

    Args:
        zip_file_path: data.zip file path
        marker: A dictionary containing information about the knowledge source,
                used to identify the target directory.

    Returns:
        0, None
    """
    try:
        dest = os.path.join(settings.base_knowledge_dir, marker.get("repo"))

        # reset the directory
        shutil.rmtree(dest)
        os.mkdir(dest)

        # insert marker file
        marker_file = settings.marker_file
        dest_marker = os.path.join(dest, marker_file)

        with open(dest_marker, "w") as salida:
            try:
                salida.write(json.dumps(marker))
                logger.debug(f"Marker data written in {dest_marker}")
            except Exception as e:
                logger.error(f"Error writing marker file: {e}")
                return None

        # test if the archive starts with directory
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            first_item = zip_ref.infolist()[0]
            if first_item.is_dir:
                dir_prefix = first_item.filename
                logger.debug(f"Directory prefix found is {dir_prefix}")
            else:
                dir_prefix = None

        # start processing
        if dir_prefix:
            with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
                for file_info in zip_ref.infolist():
                    fname = file_info.filename
                    if fname.endswith("/"):
                        dir_name = file_info.filename
                        if dir_name == dir_prefix:
                            continue
                        actual_dir = os.path.join(
                            dest, dir_name.removeprefix(dir_prefix)
                        )
                        logger.debug(f"Creating directory {actual_dir}")
                        os.makedirs(os.path.dirname(actual_dir), exist_ok=True)
                    else:
                        filename = file_info.filename
                        actual_dest = os.path.join(
                            dest, filename.removeprefix(dir_prefix)
                        )
                        logger.debug(f"Extracting file {actual_dest}")
                        with (
                            zip_ref.open(file_info) as source,
                            open(actual_dest, "wb") as target,
                        ):
                            target.write(source.read())
        else:
            try:
                zip_ref.extractall(dest)
                logger.debug(f"Data extracted under {dest} directory")
            except zipfile.BadZipFile:
                logger.error(f"Invalid zip file: {zip_file_path}")
                return None
            except Exception as e:
                logger.error(f"Error extracting zip file: {e}")
                return None

        return 0

    except FileNotFoundError:
        logger.error(f"Zip file not found: {zip_file_path}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return None


if __name__ == "__main__":
    tmpx = None
