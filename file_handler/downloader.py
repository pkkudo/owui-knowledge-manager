import os
import json
from utils import settings
import requests
from utils.base_logger import logger


def generate_url(options):
    """
    Parse options to generate target URL of the knowledge source.

    Args:
      options

    Returns:
      zip_url: URL of the public GitHub repository zip archive file to download
      marker: Marker used to do a quick diff check if the target knowledge source is already present on local
    """
    if options.repo is None:
        return "missing", None

    # set repo
    repo = options.repo

    # set target url
    # defaults to main branch
    if options.tag is not None:
        tag = options.tag
        zip_url = f"https://github.com/{repo}/archive/refs/tags/{tag}.zip"
        marker = {"repo": repo, "type": "tag", "target": tag}
    elif options.release is not None:
        release = options.release
        zip_url = f"https://github.com/{repo}/archive/refs/tags/{release}.zip"
        marker = {"repo": repo, "type": "release", "target": release}
    elif options.branch is not None:
        branch = options.branch
        zip_url = f"https://github.com/{repo}/archive/refs/heads/{branch}.zip"
        marker = {"repo": repo, "type": "branch", "target": branch}
    else:
        zip_url = f"https://github.com/{repo}/archive/refs/heads/main.zip"
        marker = {"repo": repo, "type": "main", "target": "main"}

    return zip_url, marker


def prepare_directory(marker):
    """
    Prepare directory for the specified knowledge source directory.

    Args:
      marker: dictionary with keys "repo", "type", and "target"

    Returns:
      0
    """
    dir_workspace = os.path.join(settings.base_knowledge_dir, marker.get("repo"))
    if not os.path.exists(dir_workspace):
        os.makedirs(dir_workspace)
        logger.debug(f"Directory created: {dir_workspace}")

    return 0


def compare_marker(marker):
    """
    Check if the knowledge source already exists locally,
    and compare its marker to see if there is any difference.

    Args:
      marker: dictionary with keys "repo", "type", and "target"

    Returns:
      data_already_exists: boolean used to tell if the data already exists
    """
    # return False by default
    data_already_exists = False

    # directories and files to work with
    dir_workspace = os.path.join(settings.base_knowledge_dir, marker.get("repo"))
    marker_file = settings.marker_file
    target_file = os.path.join(dir_workspace, marker_file)

    # see if the repository already exists locally
    # by checking the marker file
    if os.path.exists(target_file):
        logger.debug(f"Existing marker file found at {target_file}")
        with open(target_file, "r") as entrada:
            existing_marker = json.load(entrada)
        # if the file exists and the existing marker is identical
        # there is no need to download the remote knowledge source again
        if json.dumps(marker) == json.dumps(existing_marker):
            data_already_exists = True

    return data_already_exists


def download_file(url):
    """
    Download repository zip archive file.

    Args:
      url: URL of the GitHub public repository specified as knowledge source

    Returns:
    """
    zip_file_path = os.path.join(settings.base_knowledge_dir, "data.zip")

    try:
        # download the file
        response = requests.get(url, stream=True)
        response.raise_for_status()
        logger.debug("GET executed")

        # save the downloaded data
        with open(zip_file_path, "wb") as salida:
            for chunk in response.iter_content(chunk_size=8192):
                salida.write(chunk)
            logger.debug(f"Downloaded data saved in {zip_file_path}")

        return zip_file_path

    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading zip file: {e}")
        return None
    except IOError as e:
        logger.error(f"Error writing to file: {e}")
        return None
    except Exception as e:  # Catch-all
        logger.error(f"An unexpected error occurred: {e}")
        return None


if __name__ == "__main__":
    tmpx = None
