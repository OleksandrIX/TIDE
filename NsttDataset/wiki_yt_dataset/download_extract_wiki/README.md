## Info

A script to download Wikipedia dumps, extract them and concatenate into one long file.

This script needs WikiExtractor.py (in the same directory) to extract the downloaded wikipedia dumps.

It be downloaded from:

- https://raw.githubusercontent.com/attardi/wikiextractor/master/WikiExtractor.py

Flags:

- [-d] download only, only downloads the dumps
- [-e] extract only, only extracts the dumps

---

## Config

URL to dumps site, can be the main Wikipedia dumps repository or a mirror
All options are visible here https://dumps.wikimedia.org/

```python
dumps_url = "https://ftp.acc.umu.se/mirror/wikimedia.org/dumps/"
```

Array of language codes to download and process

(Wiki language code from here: https://meta.wikimedia.org/wiki/List_of_Wikipedias)

```python
download_wikis = ["en", "es", "uk"]
```

Output path where to download and extract the wikipedia dumps

```python
output_path = "/var/noise_speech_to_text/wiki_dumps"
```

Wikipedia dump date.
Make sure dumps for this date actually exist

```python
wiki_date = "20240120"
```