import requests
from os import path, mkdir
from tqdm import tqdm
from loguru import logger

DUMPS_URL = "https://ftp.acc.umu.se/mirror/wikimedia.org/dumps"


def download_wiki_dumps(download_wiki_languages: list, wiki_date: str, output_path: str) -> None:
    """
    Download wiki dumps for given languages and date
    :param download_wiki_languages: ["en", "es", "uk", "ru"]
    :param wiki_date: "20240120"
    :param output_path: /tmp/wiki_dumps
    :return: None
    """
    logger.info("Downloading wiki dumps")

    for language in download_wiki_languages:
        logger.info(f"Downloading wiki dump for {language} language and {wiki_date} date")

        filename = f"{language}wiki-{wiki_date}-pages-articles.xml.bz2"
        url = f"{DUMPS_URL}/{language}wiki/{wiki_date}/{filename}"

        response = requests.get(url, stream=True)
        total_size = int(response.headers.get("content-length", 0))
        block_size = 1024

        with tqdm(total=total_size, unit="iB", unit_scale=True, desc="Downloading", unit_divisor=1024) as progres_bar:
            with open(path.join(output_path, "raw_dumps", filename), "wb") as file:
                for data in response.iter_content(block_size):
                    file.write(data)
                    progres_bar.update(len(data))

        logger.info(f"Downloaded dump for {language} language")

    logger.info("Finished downloading wiki dumps")
