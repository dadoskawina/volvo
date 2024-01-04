"""
Present most frequent words in given HTML page.

Please, refer to README.md file for detailed task description and implementation notes.
"""

from html.parser import HTMLParser
import os
import re
from urllib import request

from src.logger import log


TAGS_TO_EXCLUDE = ('!--', 'audio', 'canvas', 'iframe', 'noscript', 'script', 'source', 'style', 'title', 'video')


class HtmlText(HTMLParser):
    """Class responsible for extracting text from HTML document and preparing words occurrence statistics."""

    def __init__(self) -> None:
        """
        Initialize HTMLParser and class attributes.

        Attributes:
        document_content - Designed to store the whole currently loaded document.
        parsed_text - Visible text extracted from the document.
        _tags - Helper attribute, used during document parsing. Stack of currently opened tags.
                Contains tuples: (tag name, is the tag hidden?)
        """
        log.debug("Initialize HTMLText class.")
        super().__init__()
        self.document_content = ""
        self._tags = [("", False)]
        self.parsed_text = ""

    def load_from_url(self, url: str) -> None:
        """Load HTML page from given url."""
        response = request.urlopen(url)
        assert response.code == 200, (f"Unable to get page from url {url}. Validate it correctness "
                                      f"and check your internet connection.")
        self.document_content = response.read().decode('utf-8')
        log.info(f"Successfully loaded document from url: {url}.")

    def load_from_file(self, path: str) -> None:
        """Load HTML document from given path."""
        assert os.path.isfile(path), f"Provided path {path} does not point to the existing file."
        with open(path, encoding="utf-8") as f:
            self.document_content = f.read()
        log.info(f"Successfully loaded document from file: {path}.")

    def parse_document(self) -> None:
        """Parse currently loaded document. Remove HTML tags and store remaining text to parsed_text attribute."""
        self._tags = [("", False)]
        self.parsed_text = ""
        self.feed(self.document_content)
        log.info(f"Text extraction done. Text contain {len(self.parsed_text)} characters.")
        log.debug(f"Text extracted from HTML document: {self.parsed_text}")

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str]]) -> None:
        """Add encountered opening tag to the stack. Used by feed method during HTML document parse."""
        hidden = True if 'hidden' in [attr[0] for attr in attrs] else False
        self._tags.append((tag, hidden))
        log.debug(f"Read opening tag: {tag} with attributes {attrs}. Current tags stack: {self._tags}")

    def handle_endtag(self, tag: str) -> None:
        """Remove encountered closing tag from the stack. Used by feed method during HTML document parse."""
        while tag != self._tags.pop()[0]:
            log.debug(f"Closing tag *{tag}* does not match to the last tag in stack.")
        log.debug(f"Read closing tag: {tag}. Current tags stack: {self._tags}")

    def handle_data(self, raw_text: str) -> None:
        """Check if data between tags is a visible text. If so, add to it parsed_text string."""
        if self._tags[-1][0] not in TAGS_TO_EXCLUDE and self._tags[-1][1] is False:
            self.parsed_text += raw_text

    @staticmethod
    def remove_extra_characters(text: str) -> str:
        """
        Remove punctuation and special characters from given text.

        1. Remove all occurrences of `&nbsp;` and apostrophe.
        2. Replace all occurrences of \n and \t special characters by space.
        3. Replace all occurrences of question mark, exclamation point, colon, semicolon, dash, hyphen, brackets,
           braces, parentheses, quotation mark, and ellipsis by space.
        4. Replace all occurrences of period and coma that are not used to represent large or float number, by space.

        Note: Returned text may contain multiple spaces between words. It is OK, as the parsed_text is only
              supposed to be subject of tokenization.
        """
        symbols_to_remove = ('&nbsp;', "'")
        for symbol in symbols_to_remove:
            text = text.replace(symbol, '')
        symbols_to_replace = ('?', '!', ':', ';', '-', '[', ']', '{', '}', '(', ')', "'", '"', '...', '\n', '\t')
        for symbol in symbols_to_replace:
            text = text.replace(symbol, ' ')
        nan_pattern = r'((?<!\d))[.,]((?!\d))'
        text = re.sub(nan_pattern, r'\1 \2', text)
        return text

    @staticmethod
    def tokenize(text: str) -> list[str]:
        """Split given text into separate words. All words are converted to lowercase."""
        words = text.split()
        words = [word.lower() for word in words]
        log.info(f"Tokenization. Page contain {len(words)} words.")
        log.debug(f"Extracted words: {words}")
        return words

    @staticmethod
    def find_most_frequent_words(words: list[str], max_: int = 10) -> list[tuple[str, int]]:
        """
        Given list of words, find the most frequent ones along with number of occurrences.

        Words are sorted by frequency in descending order. Then in lexicographic order.
        :param words: List of strings (words).
        :param max_: Maximum number of pairs (word, number of occurrences) to be returned. If given list contain
                     less unique words, all pairs are returned. Defaults to 10.
        :return: List of tuples (word, number of occurrences).
        """
        word_frequency = {word: words.count(word) for word in set(words)}
        log.info(f"Ordering by word frequency. Page contain {len(word_frequency)} unique words.")
        log.debug(f"List of extracted unique words: {word_frequency}")
        sorted_frequency = sorted(word_frequency.items(), key=lambda item: (-item[1], item[0]))
        return sorted_frequency[:min(max_, len(sorted_frequency))]

    def run(self) -> None:
        """
        Perform the whole process for loaded document.

        The most frequent words are both - displayed on screen and stored to `results.txt` file in current directory.
        """
        self.parse_document()
        text = self.remove_extra_characters(self.parsed_text)
        words = self.tokenize(text)
        sorted_frequency = self.find_most_frequent_words(words, 10)
        print("The 10 most frequent words are:")
        with open("results.txt", "w") as f:
            for i in range(len(sorted_frequency)):
                line = f"{i+1}. {sorted_frequency[i][0]} - {sorted_frequency[i][1]}"
                print(line)
                f.write(f"{line}\n")


if __name__ == "__main__":
    processor = HtmlText()
    processor.load_from_url('https://www.volvogroup.com/pl/')
    processor.run()
