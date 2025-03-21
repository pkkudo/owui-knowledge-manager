import os
from utils import settings
from utils.base_logger import logger
import requests


class OWUIHandler:
    def __init__(self):
        logger.debug("Initializing OWUIHandler...")
        try:
            env = {}
            # load environment variables from env_file
            logger.debug(f"Loading environment variables from {settings.env_file}")
            with open(os.path.join(os.getcwd(), settings.env_file), "r") as entrada:
                logger.debug(f"Looking for OWUI_HOSTNAME and OWUI_API_KEY")
                for line in entrada:
                    line = line.strip()
                    if not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        env[key] = value
            owui_hostname = env.get("OWUI_HOSTNAME")
            owui_api_key = env.get("OWUI_API_KEY")
            self.base_url = f"https://{owui_hostname}"
            self.headers = {
                "Authorization": f"Bearer {owui_api_key}",
                "Accept": "application/json",
            }
            logger.debug("Environment variables loaded")
            self.knowledge_id = 0
        except FileNotFoundError as e:
            logger.error(f"{e}")
            raise

    def get_user_session(self):
        api_endpoint = "/api/v1/auths/"
        url = self.base_url + api_endpoint
        try:
            with requests.get(url, headers=self.headers) as response:
                if response.status_code == 200:
                    pass
        except requests.exceptions.RequestException as e:
            logger.error(f"Exception during get_user_session: {e}")
            raise

        return 0

    def get_knowledge_collections(self):
        api_endpoint = "/api/v1/knowledge/list"
        url = self.base_url + api_endpoint
        try:
            with requests.get(url, headers=self.headers) as response:
                if response.status_code == 200:
                    pass
        except requests.exceptions.RequestException as e:
            logger.error(f"Exception during get_user_session: {e}")
            raise

        return response.json()

    def prepare_collection(self, collection_name):
        data = self.get_knowledge_collections()
        lst_collection_name = [item.get("name") for item in data]
        logger.debug(f"List of existing knowledge collections: {lst_collection_name}")

        if collection_name in lst_collection_name:
            logger.info(f"Collection {collection_name} already exists")
            lst_kid = [
                item.get("id") for item in data if item.get("name") == collection_name
            ]
            self.id_knowledge = lst_kid[0]
            logger.info(f"Knowledge ID found: {self.id_knowledge}")
        else:
            self.id_knowledge = self.create_knowledge_collection(collection_name)

        return 0

    def create_knowledge_collection(self, collection_name):
        api_endpoint = "/api/v1/knowledge/create"
        url = self.base_url + api_endpoint

        # prepare payload
        description = f"Collection of knowledges about {collection_name}"
        payload = {
            "name": collection_name,
            "description": description,
        }

        # create
        try:
            with requests.post(url, headers=self.headers, json=payload) as response:
                if response.status_code == 200:
                    logger.info(f"Knowledge collection {collection_name} created")
                    id_knowledge = response.json().get("id")
        except requests.exceptions.RequestException as e:
            logger.error(f"Exception during create_knowledge_collection: {e}")
            raise
        except Exception as e:
            logger.error(f"Exception during create_knowledge_collection: {e}")
            raise

        logger.debug(f"Knowledge ID of the collection: {id_knowledge}")

        return id_knowledge

    def upload_files(self, files):
        # file upload api endpoint
        api_endpoint = "/api/v1/files/"
        url = self.base_url + api_endpoint

        file_count = len(files)
        logger.info(f"Start uploading files: {file_count}")

        # upload files
        lst_file_id = []
        for i, file in enumerate(files):
            logger.debug(f"Uploading {file}")
            with open(file, "rb") as entrada:
                upload_file = {"file": entrada}
                try:
                    with requests.post(
                        url, headers=self.headers, files=upload_file
                    ) as response:
                        if response.status_code == 200:
                            lst_file_id.append(response.json().get("id"))
                            if i % 10 == 9:
                                logger.info(f"Files uploaded: {i + 1}")
                        else:
                            logger.debug(f"Status code: {response.status_code}")
                            logger.debug(f"Response: {response.json()}")
                except Exception as e:
                    logger.error(f"Exception during file upload: {e}")
                    raise

        logger.debug(f"File ID list: {lst_file_id}")

        return lst_file_id

    def add_files_to_knowledge(self, lst_file_id):
        # file upload api endpoint
        id_knowledge = self.id_knowledge
        api_endpoint = f"/api/v1/knowledge/{id_knowledge}/file/add"
        url = self.base_url + api_endpoint
        logger.debug(f"URL is {url}")

        # headers
        headers = self.headers

        # add files one by one
        # NOTE: could not figure out 405 error with the batch adds using /api/v1/knowledge/{id}/files/batch/add
        # even though the payload was in json (list) containing dictionaries of file_id values
        for i, id in enumerate(lst_file_id):
            payload = {"file_id": id}
            logger.debug(f"Payload: {payload}")
            with requests.post(url, headers=headers, json=payload) as response:
                response.raise_for_status()
                if response.status_code == 200:
                    if i % 10 == 9:
                        logger.info(f"Files added to the collection: {i + 1}")

        return 0

    def get_files(self):
        # file list endpoint
        api_endpoint = "/api/v1/files/"
        url = self.base_url + api_endpoint

        try:
            with requests.get(url, headers=self.headers) as response:
                response.raise_for_status()
                if response.status_code == 200:
                    files = response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Exception during get_user_session: {e}")
            raise

        return files

    def cleanup_loose_files(self, collections, files):
        # file delete endpoint
        api_endpoint = "/api/v1/files/FILE_ID"
        url = self.base_url + api_endpoint

        lst_file_id = [file.get("id") for file in files]
        logger.info(f"File ID count: {len(lst_file_id)}")

        # look into each collection found
        for col in collections:
            collection_name = col.get("name")
            logger.debug(f"Working on collection {collection_name}")

            # get the list of file IDs in this knowledge collection
            lst_col_file_id = [col_file.get("id") for col_file in col.get("files")]
            col_file_count = len(lst_col_file_id)
            logger.debug(
                f"Collection {collection_name} contains {col_file_count} files"
            )

            # remove IDs found in the file ID list
            for id in lst_file_id[:]:
                if id in lst_col_file_id:
                    lst_file_id.remove(id)

        unused_file_count = len(lst_file_id)
        logger.debug(
            f"Found {unused_file_count} files not used in any knowledge collection"
        )

        # clean up DELETE requests
        for i, id in enumerate(lst_file_id):
            payload = {"id": id}
            try:
                with requests.delete(
                    url.replace("FILE_ID", id), headers=self.headers, json=payload
                ) as response:
                    response.raise_for_status()
                    if response.status_code == 200:
                        if i % 10 == 9:
                            logger.info(f"Files cleaned up: {i + 1}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Exception during get_user_session: {e}")
                raise

        return 0


if __name__ == "__main__":
    tmpx = None
