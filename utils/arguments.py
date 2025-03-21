import argparse
import sys


def parse_options():
    """
    Argparser.

    Args:
      None

    Returns:
      args, unknown_args
    """
    parser = argparse.ArgumentParser(
        add_help=True,
        description="Open WebUI Knowledge Manager",
    )

    # general arguments
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Set debug level logging",
        default=False,
    )

    # arguments on action
    parser.add_argument("--test", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--run", action="store_true", help="Run the script.")
    parser.add_argument(
        "--download", action="store_true", help="Download public knowledge source."
    )
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Upload public knowledge source to Open WebUI.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List existing knowledge collections available on Open WebUI.",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Clean up uploaded files not linked to knowledges on Open WebUI.",
    )
    parser.add_argument(
        "--prepare",
        action="store_true",
        help="Switch to stop the script before starting to upload files for --upload action.",
    )

    # arguments on knowledge source
    parser.add_argument(
        "--repo", help="public GitHub repository to obtain knowledge from."
    )
    parser.add_argument(
        "--tag", help="Target tag of the repository specified in --repo."
    )
    parser.add_argument(
        "--release", help="Target release of the repository specified in --repo."
    )
    parser.add_argument(
        "--branch", help="Target branch of the repository specified in --repo."
    )
    parser.add_argument(
        "--dir",
        default=".",
        help="Directory in the repository to obtain knowledge from.",
    )
    parser.add_argument(
        "--filter",
        default="ANY",
        help="List of comma-separated file suffixes to use to filter.",
    )

    # arguments on knowledge collection
    parser.add_argument("--knowledge_name", help="Name of the knowledge.")
    parser.add_argument("--collection_name", help="Name of the collection.")

    if len(sys.argv) > 1:
        args, unknown = parser.parse_known_args()
        return args, unknown
    else:
        parser.print_help()
        return sys.exit(1)


if __name__ == "__main__":
    options, unknown = parse_options()
    print(f"Unknown args: {unknown}")
