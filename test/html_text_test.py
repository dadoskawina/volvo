"""Unit tests for htm_text module."""

import os

import pytest

from src.html_text import HtmlText
from test import DATA_DIRECTORY


html_test = HtmlText()


def test_load_from_file():
    html_test.load_from_file(os.path.join(DATA_DIRECTORY, "comment_hidden.html"))
    with pytest.raises(AssertionError):
        html_test.load_from_file("non_existing_file")


@pytest.mark.parametrize("filename, expected_text", [
    ("empty.html", ""),
    ("without_tags.html", "Text in document without tags."),
    ("comment_hidden.html", " \n This is a paragraph.\n "),
    ("media.html", "\n\n\n\n\n\nHeader 1\nClick on the play button to play a sound:\n\n\n\n")
])
def test_parse_document(filename: str, expected_text: str):
    html_test.load_from_file(os.path.join(DATA_DIRECTORY, filename))
    html_test.parse_document()
    assert html_test.parsed_text == expected_text


@pytest.mark.parametrize("input_text, expected_text", [
    ("", ""),
    ("Declarative sentence.", "Declarative sentence "),
    ("Jastrzębie-Zdrój", "Jastrzębie Zdrój"),
    ("world's", "worlds"),
    ("12.34", "12.34"),
    ("12.34$", "12.34$"),
    ("I won a 1,000 $ !!!!", "I won a 1,000 $     "),
    ("Hmmm...", "Hmmm "),
    ("First line\nSecond line\tNext tab", "First line Second line Next tab"),
    ("!@#$%^&*()_+-=[]{}<>,./?\\\"':;|", " @#$%^&*  _+ =    <>  / \\   |"),
    ("kitten&nbsp;9", "kitten9")
])
def test_remove_extra_characters(input_text, expected_text):
    assert html_test.remove_extra_characters(input_text) == expected_text


@pytest.mark.parametrize("input_text, expected_wordlist", [
    ("", []),
    ("To be or not to be", ["to", "be", "or", "not", "to", "be"]),
    ("Buy 1,000 items for 12.34$", ["buy", "1,000", "items", "for", "12.34$"]),
    ("hello heLLO HELLO", ["hello", "hello", "hello"])
])
def test_tokenize(input_text: str, expected_wordlist: list[str]):
    assert html_test.tokenize(input_text) == expected_wordlist


@pytest.mark.parametrize("input_wordslist, max_, expected_result", [
    ([], 10, []),
    ([""], 10, [("", 1)]),
    (["to", "be", "or", "not", "to", "be"], 10, [("be", 2), ("to", 2), ("not", 1), ("or", 1)]),
    (["to", "be", "or", "not", "to", "be"], 1, [("be", 2)]),
    (["hello", "hello", "hello"], 4, [("hello", 3)]),
    (["$", "%", "^", "&", "*", "@"], 10, [("$", 1), ("%", 1), ("&", 1), ("*", 1), ("@", 1), ("^", 1), ])
])
def test_find_most_frequent_words(input_wordslist, max_, expected_result):
    assert html_test.find_most_frequent_words(input_wordslist, max_) == expected_result
