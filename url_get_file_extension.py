from urllib.parse import urlsplit, unquote
from os.path import split, splitext


def get_file_extension(url):
    parsed_url = urlsplit(url)
    path = unquote(parsed_url.path)
    _, filename = split(path)
    _, extension = splitext(filename)
    return extension.lower()
