import os
import pathlib
import logging
import time
from urllib.parse import urlparse

import requests
import magic
from bs4.dammit import html_meta
from ebooklib import epub
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

LANGS = [
    "en",
    "bn",
    "zh-cn",
    "fr", "de", "hi", "id", "it", "ja", "ko", "pl", "pt-br", "ru", "es", "uk", "vi"
    ]
HOST = "https://kubernetes.io"
DOMAIN = "kubernetes.io"
IMAGES_DIR = "img"


def get_html(url):
    logger.debug(f"Getting {url}")
    resp = requests.get(url)
    if resp.status_code != 200:
        logger.warning(f"Error getting {url}, code {resp.status_code}")
        return ""

    return resp.content


def get_images(page_soup):
    images = page_soup.find_all("img")
    result = []
    failed = []
    logger.debug(f"found {len(images)}")
    for img in images:
        if not img.has_attr("src"):
            continue

        # broken html workaround
        # `zh-cn` version has malformed html source
        if img.has_attr("processed"):
            continue

        parsed = urlparse(img.attrs["src"])

        if parsed.path.startswith("/"):
            filepath = pathlib.Path(IMAGES_DIR).joinpath(pathlib.Path(parsed.path).relative_to("/"))
        else:
            filepath = pathlib.Path(IMAGES_DIR).joinpath(pathlib.Path(parsed.path))

        if not filepath.exists():
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            if not parsed.netloc:
                parsed = parsed._replace(scheme="https")
                parsed = parsed._replace(netloc=DOMAIN)
            logger.debug(f"Getting {img.attrs["src"]} from {parsed.geturl()}, saving to {filepath}")

            if parsed.geturl() in failed:
                continue

            content = get_html(parsed.geturl())
            if content == "":
                time.sleep(2)
                if parsed.geturl() not in failed:
                    failed.append(parsed.geturl())
                continue

            filepath.write_bytes(content)
            time.sleep(2)

        # ew
        img.attrs["src"] = str(filepath)
        img.attrs["processed"] = True

        if str(filepath) not in result:
            result.append(str(filepath))
    return result


def run(lang):
    logger.info(f"Language: {lang}")
    html_name = f"index.{lang}.html"
    url = "https://kubernetes.io/docs/_print/index.html"
    if lang != "en":
        url = f"https://kubernetes.io/{lang}/docs/_print/index.html"
    epub_name = f"Kubernetes_Documentation.{lang}.epub"

    f = pathlib.Path(html_name)
    if not f.exists():
        content = get_html(url)
        f.write_bytes(content)

    content = f.read_bytes()
    bs = BeautifulSoup(content, "html.parser")

    main_tag = bs.find("main")
    if main_tag is None:
        logger.error("No main tag")
        exit(1)

    pages = main_tag.find_all("div", {"class": "td-content"})
    if pages is None:
        logger.error("No pages")
        exit(1)

    os.makedirs(IMAGES_DIR, exist_ok=True)

    book = epub.EpubBook()
    book.set_language(lang)
    book.set_title("Kubernetes Documentation")
    book.add_author("Cloud Native Computing Foundation")
    book.add_author(author="unknown321", file_as="epub creator")

    css = "main.css"
    with open(css) as f:
        content = f.read()
    css_entry = epub.EpubItem(
        uid=css,
        file_name=css,
        media_type="text/css",
        content=content,
    )
    book.add_item(css_entry)

    i = 0
    # skip hugo-generated toc
    logger.info(f"Found {len(pages)} pages")
    for page in pages[1:]:
        i = i +1
        header = page.find("h1")
        if header is None:
            logger.error("No title")
            exit(1)
        title = header.text.strip()
        title = sanitize_filename(title)
        images = get_images(page)
        logger.info(f"Processing page {i}, images {len(images)}, title {title}")

        xhtmlName = title.replace(" ", "_") + ".xhtml"
        c1 = epub.EpubHtml(title=title, file_name=xhtmlName, lang=lang)
        c1.content = str(page.prettify(formatter="minimal"))
        c1.add_item(css_entry)

        for image in images:
            if book.get_item_with_id(image):
                continue
            m = magic.from_file(image, mime=True)
            img = epub.EpubImage(
                uid=image,
                file_name=image,
                media_type=m,
                content=open(image, "rb").read(),
            )
            book.add_item(img)

        book.add_item(c1)
        book.spine.append(c1)
        book.toc.append(epub.Link(xhtmlName, title, title))

    book.add_item(epub.EpubNav())
    book.add_item(epub.EpubNcx())
    if pathlib.Path(epub_name).exists():
        os.remove(epub_name)
    epub.write_epub(epub_name, book)
    logger.info(f"Generated EPUB: {epub_name}")


def main():
    logging.basicConfig(level=logging.INFO)
    logger.info('Started')
    for lang in LANGS:
        run(lang)
    logger.info('Finished')


if __name__ == '__main__':
    main()
