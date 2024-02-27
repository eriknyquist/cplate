import io
import os
import configparser
from dataclasses import dataclass


DEFAULT_CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".cplate_config.ini")


@dataclass
class CplateConfig:
    header_comment: str = ''
    author: str = ''
    doxygen_comments: bool = True
    blank_line_count: int = 2
    brace_style: str = "allman"

    @classmethod
    def from_string(cls, string):
        config = configparser.ConfigParser()
        config.read_string(string)
        ret = CplateConfig()

        if 'comments' in config:
            if 'header_comment' in config['comments']:
                ret.header_comment = config['comments']['header_comment'].strip()

            if 'author' in config['comments']:
                ret.author = config['comments']['author']

            if 'doxygen_comments' in config['comments']:
                try:
                    ret.doxygen_comments = config['comments'].getboolean('doxygen_comments')
                except ValueError:
                    raise ValueError("true/false required for comments.doxygen_comments")

        if 'whitespace' in config:
            if 'blank_line_count' in config['whitespace']:
                try:
                    ret.blank_line_count = config['whitespace'].getint('blank_line_count')
                except ValueError:
                    raise ValueError("Integer required for whitespace.blank_line_count")

        if 'code' in config:
            if 'brace_style' in config['code']:
                ret.brace_style = config['code']['brace_style']

        return ret

    @classmethod
    def from_file(cls, filename):
        with open(filename, 'r') as fh:
            return cls.from_string(fh.read())

    def to_string(self):
        config = configparser.ConfigParser()

        config['comments'] = {}
        config['comments']['header_comment'] = "\n" + str(self.header_comment)
        config['comments']['author'] = str(self.author)
        config['comments']['doxygen_comments'] = str(self.doxygen_comments).lower()

        config['whitespace'] = {}
        config['whitespace']['blank_line_count'] = str(self.blank_line_count)

        config['code'] = {}
        config['code']['brace_style'] = str(self.brace_style)

        str_fp = io.StringIO()
        config.write(str_fp)
        return str_fp.getvalue()


if __name__ == "__main__":
    cfg = CplateConfig.from_file("cplate_config.ini")
    print(cfg)
    print(cfg.to_string())
