from collections import OrderedDict

import re


def split_markdown_by_headings(md_text: str) -> OrderedDict:
    """
    Splits the Markdown text into sections based on headings.

    :param md_text: The Markdown text to parse.
    :return: A dictionary with headings as keys and the following content as values.
    """
    # Regular expression to match Markdown headings
    heading_re = re.compile(r"^(#{1,8})\s*(.*)", re.MULTILINE)

    # Find all headings and their positions
    headings = [
        (match.start(), len(match.group(1)), match.group(2))
        for match in heading_re.finditer(md_text)
    ]

    # Split the text based on these headings
    sections = OrderedDict()
    for i, (pos, level, heading) in enumerate(headings):
        # Determine the end of the current section
        if i + 1 < len(headings):
            end = headings[i + 1][0]
        else:
            end = len(md_text)

        # Extract the section content
        content_start = pos + len(heading) + level + 1  # +1 for the space after '#'
        content = md_text[content_start:end].strip()

        # Use the heading as the key, assuming unique headings for simplicity
        key = ("#" * level) + " " + heading
        sections[key] = content

    # Handle any initial content before the first heading
    if headings:
        first_heading_start = headings[0][0]
        initial_content = md_text[:first_heading_start].strip()
        if initial_content:
            sections["no heading"] = initial_content

    return sections


def get_sections(file_path: str) -> OrderedDict:
    with open(file_path, "r") as f:
        content = f.read()
    sections = split_markdown_by_headings(content)
    return sections
