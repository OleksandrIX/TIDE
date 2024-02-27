import subprocess
import shutil
from os import path, walk, mkdir
from loguru import logger


def extract_wiki_dumps(languages: list, wiki_date: str, dumps_path: str):
    """
    Extract wiki dumps
    :param languages: ["en", "es", "uk", "ru"]
    :param wiki_date: "20240120"
    :param dumps_path: /tmp/wiki_dumps
    :return: None
    """
    # mkdir(path.join(dumps_path, "extracted_dumps_json"))

    for language in languages:
        filename = f"{language}wiki-{wiki_date}-pages-articles.xml.bz2"
        file_path = path.join(dumps_path, "raw_dumps", filename)
        output_dir = path.join(dumps_path, "raw_dumps", "extracted")
        output_file = path.join(dumps_path, "extracted_dumps_json", f"{language}_wiki.extracted.txt")

        logger.info(f"Extracting {filename}...")

        try:
            subprocess.run(["wikiextractor",
                            "-o", output_dir,
                            file_path,
                            "--no-templates",
                            "--quiet",
                            "--processes", "8",
                            "--json",
                            "--output_file", output_file])

            with open(output_file, "w") as output_file:
                for root, dirs, files in walk(output_dir):
                    for file in files:
                        file_path = path.join(root, file)
                        with open(file_path, "r") as input_file:
                            output_file.write(input_file.read())
            shutil.rmtree(output_dir)
            logger.info(f"Extracted {filename}")
        except Exception as err:
            logger.error(f"{err=}")

    logger.info("Finished extracting wiki dumps")
