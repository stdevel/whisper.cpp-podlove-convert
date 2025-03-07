#!/usr/bin/python3
"""
Script for converting whisper.cpp JSON transcripts to Podlove Web Player transcripts
"""

import argparse
import logging
import os
import sys
import json

__version__ = "0.0.1"

LOGGER = logging.getLogger("converter")
"""
LOGGER: Logger instance
"""
LOG_LEVEL = None
"""
LOG_LEVEL: Logger level
"""


def convert(source, destination, speaker_id, speaker):
    """
    Convert transcript
    """
    _target = []
    _source = load_transcript(source)
    for _entry in _source["transcription"]:
        LOGGER.debug("Found entry %s", _entry)
        # TODO: Try to retrieve speaker from source?
        _target.append(
            {
                "start": _entry["timestamps"]["from"].replace(",", "."),
                "start_ms": _entry["offsets"]["from"],
                "end": _entry["timestamps"]["to"].replace(",", "."),
                "end_ms": _entry["offsets"]["to"],
                "speaker": speaker_id,
                "voice": speaker,
                "text": _entry["text"],
            }
        )
    LOGGER.debug("Converted transcript %s", _target)
    with open(destination, "w", encoding="utf-8") as f:
        json.dump(_target, f, indent=4)
    LOGGER.info("Converted transcription!")


def load_transcript(filename):
    """
    Load a transcript from filename.

    The returned report will be a dict containing transcript information.

    :param filename: The name of the file to load from.
    :type filename: str
    :rtype: {str: Host}
    :returns: The hosts from the report
    """
    transcript = json.loads(get_json(filename))
    return transcript


def get_json(filename):
    """
    Reads a JSON file and returns the whole content as one-liner.

    :param filename: the JSON filename
    :type filename: str
    """
    try:
        with open(filename, "r", encoding="utf-8") as json_file:
            json_data = json_file.read().replace("\n", "")
        return json_data
    except IOError as err:
        LOGGER.error("Unable to read file %r: %s", filename, err)
        return False


def is_valid_whisper_json(filename):
    """
    Checks whether a JSON file contains a valid whisper.cpp JSON transcript.

    :param filename: the JSON filename
    :type filename: str
    """
    if not os.path.exists(filename):
        raise ValueError(f"File {filename!r} is non-existent")

    if not os.access(filename, os.R_OK):
        raise ValueError(f"File {filename!r} is not readable")

    try:
        # check whether valid json
        json_obj = load_transcript(filename)
        # assert that required keys exist
        keys = ["systeminfo", "model", "transcription"]
        for _key in keys:
            if not json_obj[_key]:
                raise TypeError(f"The JSON lacks a required key: {_key}")

        if not json_obj:
            raise ValueError("The transcript is empty")
    except (TypeError, ValueError) as err:
        raise ValueError(
            f"File {filename} is not a valid JSON whisper.cpp transcript: {err}"
        ) from err
    except Exception as err:
        raise ValueError(f"File {filename} failed to load: {err}") from err

    return filename


def parse_options(args=None):
    """
    Parses options and arguments.
    """
    desc = """%(prog)s is used for converting whisper.cpp JSON transcripts
    to Podlove Web Player transcripts.
    """
    epilog = """Check-out the website for more details:
     http://github.com/stdevel/whisper.cpp-podlove-convert"""
    parser = argparse.ArgumentParser(description=desc, epilog=epilog)
    parser.add_argument("--version", action="version", version=__version__)

    # define option groups
    gen_opts = parser.add_argument_group("generic arguments")
    speaker_opts = parser.add_argument_group("speaker arguments")

    # -d / --debug
    gen_opts.add_argument(
        "-d",
        "--debug",
        dest="generic_debug",
        default=False,
        action="store_true",
        help="enable debugging outputs (default: no)",
    )

    # -f / --force
    gen_opts.add_argument(
        "-f",
        "--force",
        dest="generic_force",
        default=False,
        action="store_true",
        help="overwrite existing files (default: no)",
    )

    # -i / --default-speaker-id
    speaker_opts.add_argument(
        "-i",
        "--default-speaker-id",
        dest="speaker_default_id",
        default="0",
        action="store",
        help="Speaker ID if no information found in source transcript (default: 0)",
    )

    # -s / --default-speaker
    speaker_opts.add_argument(
        "-s",
        "--default-speaker",
        dest="speaker_default",
        default="simone-giertz",
        action="store",
        help="Speaker if no information found in source transcript (default: simone-giertz)",
    )

    parser.add_argument(
        "source", metavar="SOURCE", type=is_valid_whisper_json, help="Source file"
    )
    parser.add_argument("dest", metavar="DESTINATION", help="Destination file")

    # parse options and arguments
    options = parser.parse_args()

    # check source/destination files
    if options.source == options.dest:
        LOGGER.error("Source and destination file mustn't be the same!")
        sys.exit(1)
    if os.path.exists(options.dest) and not options.generic_force:
        LOGGER.error(
            "Destination file already exists and -f / --force wasn't supplied."
        )
        sys.exit(1)
    if " " in options.speaker_default:
        LOGGER.error(
            "Speaker name mustn't contain spaces - "
            " e.g. use 'simone-giertz' instead of 'Simone Giertz'."
        )
        sys.exit(1)

    return (options, args)


def main(options, args):
    """
    Main function, starts the logic based on parameters.
    """
    LOGGER.debug("Options: %s", str(options))
    LOGGER.debug("Arguments: %s", str(args))

    # convert transcript
    convert(
        options.source,
        options.dest,
        options.speaker_default_id,
        options.speaker_default,
    )


def cli():
    """
    This functions initializes the CLI interface
    """
    global LOG_LEVEL
    (options, args) = parse_options()

    # set logging level
    logging.basicConfig()
    if options.generic_debug:
        LOG_LEVEL = logging.DEBUG
    else:
        LOG_LEVEL = logging.INFO
    LOGGER.setLevel(LOG_LEVEL)

    main(options, args)


if __name__ == "__main__":
    cli()
