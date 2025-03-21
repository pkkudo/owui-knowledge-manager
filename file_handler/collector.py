import os
import shutil
import subprocess
from glob import glob
from utils import settings
from utils.base_logger import logger


def collect_files(marker, filter, dir):
    """
    Prepare the list of files to be added to Open WebUI as knowledge.

    Args:
      marker: dictionary
      filter: list of file extensions to use as filter in comma-separated string provided in options.filter
      dir: directory inside the repository to start digging for files, provided in options.dir, defaults to "."

    Returns:
      files_knowledge
    """
    files_knowledge = []

    # repository path
    dest = os.path.join(settings.base_knowledge_dir, marker.get("repo"))
    # concatenate options.dir
    if dir == ".":
        pass
    else:
        dest = os.path.join(dest, dir)

    # test if the target path exists
    if os.path.exists(dest):
        logger.info(f"Start collecting knowledges in {dest}")
    else:
        logger.error(f"Could not find the specified directory, {dest}. Exiting.")
        raise

    # get list of files to add to knowledge collection
    all_files = glob(f"{dest}/**/*", recursive=True)

    # filter
    if filter != "ANY":
        # filter for files with the specified extensions
        collection_filters = [
            ".{}".format(extension) for extension in filter.split(",")
        ]
        logger.debug(f"Collector will look for these extensions: {collection_filters}")
        files_knowledge = [
            file for file in all_files if file.endswith(tuple(collection_filters))
        ]
    else:
        # exclude directories from everything picked up in all_files
        files_knowledge = [file for file in all_files if not os.path.isdir(file)]

    # log first and last three files in the list
    file_count = len(files_knowledge)
    logger.debug("List of files collected:")
    for i, file in enumerate(files_knowledge):
        if i < 3:
            logger.debug(f"- {file}")
            flag = True
        elif i > file_count - 4:
            logger.debug(f"- {file}")
        else:
            if flag:
                flag = False
                logger.debug("- ... omitting ...")

    # if pandoc is found on the host, convert rst files to markdown
    # as open webui is not accepting rst file as knowledge collection source
    if is_pandoc_installed():
        files_knowledge = rst_workaround(files_knowledge)

    # total size of files
    total_size = sum(os.path.getsize(file) for file in files_knowledge)
    logger.debug(f"Total knowledge collection size: {total_size:,}")
    logger.info(f"Collected {file_count} knowledge sources sizing {total_size:,} byte.")

    return files_knowledge


def is_pandoc_installed():
    return shutil.which("pandoc") is not None


def rst_workaround(files_knowledge):
    """
    Process list of files and convert rst files to markdown.
    This is a workaround until Open WebUI knowledge support rst format.

    Args:
      files_knowledge: list of file path collected to be uploaded and added to knowledge collection

    Returns:
      files_knowledge: updated list of file path (only if there are rst files)
    """
    new_files_knowledge = []

    for file in files_knowledge:
        if os.path.basename(file).endswith(".rst"):
            # convert the file to markdown using rst2md
            # and add the new file path to the new list
            file_out = file.replace(".rst", ".md")
            try:
                subprocess.run(
                    ["pandoc", file, "-o", file_out],
                    check=True,
                )
                logger.debug(
                    f"{os.path.basename(file)} converted to markdown file: {file_out}"
                )
                new_files_knowledge.append(file_out)
            except subprocess.CalledProcessError as e:
                logger.error(f"Error during conversion: {e}")
                logger.error(f"Standard Output: {e.stdout}")
                logger.error(f"Standard Error: {e.stderr}")
        else:
            # put the file path back as-is if it's not rst file
            new_files_knowledge.append(file)

    return new_files_knowledge


if __name__ == "__main__":
    tmpx = None
