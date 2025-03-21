"""Open WebUI Knowledge Manager

This code helps to manage knowledges and collections on Open WebUI.
"""

# general imports
import sys
import logging

# module imports
from utils import settings
from utils.arguments import parse_options
from utils.base_logger import logger

from file_handler import downloader, extractor, collector

from api import client


# main function
def main():
    settings.init()
    # Process args
    options, unknown_args = parse_options()

    # Setup logger
    logger.info("Starting Open WebUI Knowledge Manager...")
    if options.debug:
        logger.setLevel(logging.DEBUG)
    logger.debug(f"Arguments failed to parse: {unknown_args}")

    if options.cleanup:
        logger.debug("Executing cleanup section")
        handler = client.OWUIHandler()

        logger.info("Retrieve knowledge collections list")
        collections = handler.get_knowledge_collections()

        logger.info("Retrieve uploaded files list")
        files = handler.get_files()

        logger.info("Clean up uploaded files not used in any collection")
        handler.cleanup_loose_files(collections, files)

    if options.download:
        logger.debug("Executing download section")
        try:
            # identify the target knowledge source
            logger.info("Generating download URL...")
            zip_url, marker = downloader.generate_url(options)
            logger.debug(f"URL of the target knowledge source: {zip_url}")
            logger.debug(f"Brief summary of the target knowledge source: {marker}")
            if zip_url == "missing":
                logger.error("Provide the target public GitHub repository in '--repo'.")
                sys.exit(1)

            # check if the target knowledge source is already present locally using the marker
            logger.debug("Prepare local directory for the specified knowledge source")
            downloader.prepare_directory(marker)

            logger.debug(
                "Check if the knowledge source repository already exists locally"
            )
            data_already_exists = downloader.compare_marker(marker)

            # download and extract repo zip data if the data is not yet downloaded
            if data_already_exists:
                logger.info("The knowledge source data is already downloaded")
            else:
                # download the remote, public, knowledge source
                logger.info(f"Downloading zip file from {zip_url}...")
                zip_file_path = downloader.download_file(zip_url)
                if zip_file_path is None:
                    if marker.get("type") == "main":
                        zip_url = zip_url.replace("heads/main.zip", "heads/master.zip")
                        zip_file_path = downloader.download_file(zip_url)
                    if zip_file_path is None:
                        logger.error(f"Failed to download from {zip_url}. Exiting...")
                        sys.exit(1)
                logger.info(f"Zip file downloaded to {zip_file_path}")

                # extract downloaded zip file
                logger.info("Extracting zip file...")
                extract_status = extractor.extract_zip(zip_file_path, marker)
                if extract_status is None:
                    logger.error("Failed to extract archive. Exiting...")
                    sys.exit(1)
                logger.info("Zip file extracted")

        except Exception as e:
            logger.error(f"An error occurred: {e}", exc_info=True)

    if options.list:
        # initialization and health check
        logger.debug("Executing list section")
        handler = client.OWUIHandler()
        handler.get_user_session()

        # get existing knowledge collections
        collections = handler.get_knowledge_collections()
        logger.debug(f"{len(collections)} collections found")

        if len(collections) > 0:
            for collection in collections:
                col_name = collection.get("name")
                if len(collection.get("files")) > 0:
                    file_count = len(collection.get("files"))
                    knowledge_size = 0
                    for file in collection.get("files"):
                        knowledge_size += int(file["meta"]["size"])
                    logger.info(f"Collection Name: {col_name}")
                    logger.info(f"File Count: {file_count}")
                    logger.info(f"Knowledge size: {knowledge_size:,}")

    if options.upload:
        logger.debug("Executing upload section")
        try:
            # ensure the collection name is provided
            # --collection_name
            if options.collection_name is None:
                logger.error(
                    "Collection name not provided in --collection_name. Exiting."
                )
                sys.exit(1)
            # double check that the requested data is already downloaded
            zip_url, marker = downloader.generate_url(options)
            if zip_url == "missing":
                logger.error("Provide the target public GitHub repository in '--repo'.")
                sys.exit(1)
            data_already_exists = downloader.compare_marker(marker)
            if not data_already_exists:
                logger.error(
                    "The requested knowledge source needs to be downloaded first. Exiting."
                )
                sys.exit(1)

            # collect target documents
            logger.info("Collecting files...")
            files_knowledge = collector.collect_files(
                marker, options.filter, options.dir
            )
            # check if the collection already exists
            # create anew if not
            logger.info("Ensuring the knowledge collection is created...")
            handler = client.OWUIHandler()
            handler.prepare_collection(options.collection_name)

            # stop here when --prepare switch is used
            if options.prepare:
                logger.info("Stopping the upload actions here when --prepare is set")
                return 0

            # upload collected files and then add them to the specified collection
            logger.info("Uploading files collected...")
            lst_file_id = handler.upload_files(files_knowledge)
            logger.info("Adding uploaded files to the knowledge collection...")
            handler.add_files_to_knowledge(lst_file_id)
        except:
            raise

    return 0


if __name__ == "__main__":
    main()
