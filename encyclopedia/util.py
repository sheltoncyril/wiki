import re
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from markdown2 import Markdown  # pylint: disable=import-error


def list_entries():
    """
    Returns a list of all names of encyclopedia entries.
    """
    _, filenames = default_storage.listdir("entries")
    return list(
        sorted((re.sub(r"\.md$", "", filename)
                for filename in filenames if re.match(r".*\.md$", filename)),
               key=str.casefold)
    )  # Using re as it is much faster than .endswith or .startswith


def search_entries(query):
    """
    Returns a list of all names of encyclopedia entries.
    """
    _, filenames = default_storage.listdir("entries")
    return list(
        sorted(
            re.sub(r"\.md$", "", filename) for filename in filenames if
            re.match(r".*\.md$", filename) and re.match(query, filename, re.I))
    )  # Using re as it is much faster than .endswith or .startswith


def save_entry(title, content):
    """
    Saves an encyclopedia entry, given its title and Markdown
    content. If an existing entry with the same title already exists,
    it is replaced.
    """
    filename = f"entries/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
    default_storage.save(filename, ContentFile(content))


def get_entry(title):
    """
    Retrieves an encyclopedia entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(f"entries/{title}.md")
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None


def mdparse(rawstr):
    markdowner = Markdown()
    return (markdowner.convert(rawstr))
