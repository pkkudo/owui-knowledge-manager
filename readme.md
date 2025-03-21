# Open WebUI Knowledge Manager

Manager... or it's rather a script to download public GitHub data and bulk upload them to Open WebUI knowledge collection.

I wanted to have this so it's more convenient to prepare knowledge collections needed to do what is described here, [Tutorial: Configuring RAG with Open WebUI Documentation](https://docs.openwebui.com/tutorials/tips/rag-tutorial).

## Setup

### short version

The only external module I used is requests, so...

```sh
pip install requests

# and the long version mentions about python@3.13 but older versions are fine too
```

### long version

```sh
# prep python>=3.13 and load venv

# upgrade pip and install latest poetry
pip install -U pip
pip install poetry

# install other requirements defined in pyproject
poetry install --no-root
```

### optional

If the host running this script has [Pandoc](https://pandoc.org/) in the path, the script will convert ".rst" files to ".md" files so that they can be added to the Open WebUI knowledge collections. The behavior may change in the future, but the Open WebUI v0.5.20 won't accept ".rst" files to be added to a knowledge collection.

## Usage

As a preparation, copy `.env.example` and create your own `.env` file with your Open WebUI hostname and API key.

There are four different tasks that can be executed by this script:

- download
- upload
- list
- cleanup

### Download

Download the zip archive of the specified public repository.

By default, it will try to download the zip archive of the main branch, and then master branch if it fails to download main. You can specify specific branch, tag, or release.

```sh
# main branch of kubernetes/website repository on GitHub
python app.py --repo kubernetes/website --download

# specify tag or release
python app.py --repo kubernetes/website --download --tag snapshot-initial-v1.32
python app.py --repo kubernetes/website --download --release snapshot-initial-v1.32

# specify branch
python app.py --repo kubernetes/website --download --branch release-1.31
```

### Upload

Upload certain set of files from the downloaded repo to the specific knowledge collection on Open WebUI.

The two example commands picks up all markdown files recursively in the specified directory, upload and add them in the knowledge collections.

With `--prepare` in the argument, the script will just show you the number of files and total size of the files to be uploaded and added to the knowledge collection.

When you omit `--dir`, the file digging starts at the repository root.

When you omit `--filter`, the collector will just pickup any file.

```sh
# assuming that the kubernetes/website main branch data is already downloaded

python app.py --repo kubernetes/website --upload \
  --collection_name kube-concept \
  --filter md \
  --dir content/en/docs/concepts

python app.py --repo kubernetes/website --upload \
  --collection_name kube-ref \
  --filter md \
  --dir content/en/docs/reference \
  --prepare
```

### List

Use `--list` to list available knowledge collections along with the file count and total size.

```sh
python app.py --list
```

### Clean Up

You are able to upload certain types of files to Open WebUI but not able to add them to the knowledge collection. In such case, the `--upload` operation did definitely upload the files collected to Open WebUI, and will be left there unused. Upon each file upload, the file is given a unique ID. The action which follows the file upload is to add the file to an existing knowledge by specifying which file ID to be linked to the knowledge collection.

- you run `--upload`
- list of files are collected
- each file gets uploaded, and the script receives the unique ID for each file uploaded
- ~~use the file ID to tell the knowledge collection it has all these file IDs to refer to~~
  - this step to link uploaded files and the knowledge collection may fail, and the uploaded files identified by the unique ID given when uploaded just stay there forever, unused

```sh
python app.py --cleanup
```
