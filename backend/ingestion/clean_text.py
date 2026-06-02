import re


def clean_text(text: str) -> str:
    """Clean extracted webpage text."""

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove repeated blank lines
    text = re.sub(r"\n+", "\n", text)

    return text.strip()