import click
from loguru import logger
from config.logger import init_logger

init_logger(app_name="wiki-yt-dataset",
            std_level="TRACE",
            file_level="INFO",
            log_rotation="1 day",
            log_compression="gz")


@click.group()
def cli():
    pass


@cli.command(name="wiki")
@click.option("--download", "-d", is_flag=True, help="Download wiki dumps")
@click.option("--extract", "-e", is_flag=True, help="Extract wiki dumps")
@click.option("--languages", "-l", required=True, default="en", help="Languages to download and extract")
@click.option("--date-dump", "-D", required=True, help="Date of wiki dumps to download and extract")
@click.option("--output-path", "-o", required=True, help="Output directory to save wiki dumps")
def download_wiki_dumps(download: bool, extract: bool, languages: str, date_dump: str, output_path: str):
    """
    Download and extract wiki dumps\n
    For the download and extract options, you can do not specify any of them, or specify both of them.\n
    If you do not specify any of them, both of them will be executed.\n
    """
    from download_extract_wiki import download_wiki_dumps, extract_wiki_dumps

    languages = languages.strip().split()
    logger.info(f"Languages: {languages}")

    if (download and extract) or (not download and not extract):
        logger.info("Downloading and extracting wiki dumps...")
        download_wiki_dumps(languages, date_dump, output_path)
        extract_wiki_dumps(languages, date_dump, output_path)
    elif download:
        logger.info("Downloading wiki dumps...")
        download_wiki_dumps(languages, date_dump, output_path)
    elif extract:
        logger.info("Extracting wiki dumps...")
        extract_wiki_dumps(languages, date_dump, output_path)


if __name__ == "__main__":
    cli()
