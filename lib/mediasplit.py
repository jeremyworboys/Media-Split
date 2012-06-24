#!/usr/bin/python

"""
Media Split finds unique break-points in a CSS file and combines the contents of
each, outputting each break-point to a separate CSS file.

Usage: python mediasplit.py style.css first.css
"""
import sys
import re
from collections import OrderedDict


RE_HAS_MEDIA = re.compile("@media")
RE_FIND_MEDIA = re.compile("(@media.+?)(\{)", re.DOTALL | re.MULTILINE)
RE_MEDIA_NAME = re.compile("@media.+?((?:min|max)-width:\s+[\d\w]+)", re.DOTALL | re.MULTILINE)
RE_FILENAME = re.compile("[^\d\w]")
RE_MULTI_DASH = re.compile("-+")


class MediaSplit:
    """
    Media Split finds unique break-points in a CSS file and combines the contents of
    each, outputting each break-point to a separate CSS file.
    """

    def __init__(self):
        self._reset()

    def run(self, remaining_file="first.css"):
        # Make sure it has media queries
        if not RE_HAS_MEDIA.search(self.contents):
            return

        # Find all of the unique media queries
        self.queries = [(m.group(1).strip(), m) for m in RE_FIND_MEDIA.finditer(self.contents)]

        # Consolidate the media queries
        for (query, m) in self.queries:
            if not query in self.query_contents:
                self.query_contents[query] = []
            self.query_contents[query].append(self._get_contents(m))

        # Remove the media queries
        for contents in self.query_contents.itervalues():
            for (_, content) in contents:
                self.contents = self.contents.replace(content, "")

        # Output the consolidated media queries
        for (query, contents) in self.query_contents.iteritems():
            filename = "%s.css" % self._make_filename(query)
            file_contents = "".join([content for (content, _) in contents]).strip()
            self._put_file_contents(filename, file_contents)

        # Output the remaining styles
        self._put_file_contents(remaining_file, self.contents.strip())

    def fix(self, filename, remaining_file):
        self._reset()
        self.contents = self._get_file_contents(filename)
        self.run(remaining_file)

    def _get_file_contents(self, filename):
        fh = open(filename, "r")
        contents = fh.read()
        fh.close()
        return contents

    def _put_file_contents(self, filename, contents):
        fh = open(filename, "w")
        print >> fh, contents
        fh.close()

    def _reset(self):
        self.queries = []
        self.query_contents = OrderedDict()
        self.contents = ""

    def _make_filename(self, filename):
        m = RE_MEDIA_NAME.match(filename)
        if (m is not None):
            filename = m.group(1)
        filename = RE_FILENAME.sub("-", filename)
        filename = RE_MULTI_DASH.sub("-", filename)
        return filename

    def _get_contents(self, match):
        open_braces = 1  # we are starting the character after the first opening brace
        position = match.end()
        content = ""
        while open_braces > 0:
            c = self.contents[position]
            if c == "{":
                open_braces += 1
            if c == "}":
                open_braces -= 1
            content += c
            position += 1
        return (content[:-1].strip(), self.contents[match.start():position])  # the last closing brace gets captured, drop it


def help():
    print """
Media Split finds unique break-points in a CSS file and combines the contents of
each, outputting each break-point to a separate CSS file.

Usage: %s style.css first.css
""" % sys.argv[0]


def main():
    remaining_file = "first.css"

    if len(sys.argv) > 2:
        remaining_file = sys.argv[2]

    if len(sys.argv) > 1:
        m = MediaSplit()
        m.fix(sys.argv[1], remaining_file)
    else:
        help()


if __name__ == "__main__":
    main()
