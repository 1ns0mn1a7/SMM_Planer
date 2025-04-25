import re


def text_to_post_format(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s*([.,:;!?])', r'\1', text)
    text = re.sub(r'([«»])\s*', r'\1', text)

    text = re.sub(r'"(.*?)"', r'«\1»', text)
    text = re.sub(r"'(.*?)'", r'«\1»', text)

    text = re.sub(r'(?<=\s)-(?=\s)', '–', text)

    return text.strip()
