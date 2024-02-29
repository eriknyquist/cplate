import io
import os
import configparser
from dataclasses import dataclass, field
from typing import Dict

DEFAULT_CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".cplate_config.ini")


@dataclass
class CplateConfig:
    header_comment_file: str = ''
    author: str = ''
    doxygen_comments: bool = True
    include_guards: bool = True
    blank_line_count: int = 2
    brace_style: str = "allman"
    custom_return_values: dict = field(default_factory=dict)

    @classmethod
    def from_string(cls, string):
        config = configparser.ConfigParser()
        config.read_string(string)
        ret = CplateConfig()

        if 'comments' in config:
            if 'header_comment_file' in config['comments']:
                ret.header_comment_file = config['comments']['header_comment_file'].strip()

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

            if 'include_guards' in config['code']:
                ret.include_guards = config['code'].getboolean('include_guards')

        if 'custom_return_values' in config:
            for key in config['custom_return_values']:
                ret.custom_return_values[key] = config['custom_return_values'][key]

        return ret

    @classmethod
    def from_file(cls, filename):
        with open(filename, 'r') as fh:
            return cls.from_string(fh.read())

    def to_string(self):
        config = configparser.ConfigParser()

        config['comments'] = {}
        config['comments']['header_comment_file'] = str(self.header_comment_file)
        config['comments']['author'] = str(self.author)
        config['comments']['doxygen_comments'] = str(self.doxygen_comments).lower()

        config['whitespace'] = {}
        config['whitespace']['blank_line_count'] = str(self.blank_line_count)

        config['code'] = {}
        config['code']['brace_style'] = str(self.brace_style)
        config['code']['include_guards'] = str(self.include_guards).lower()

        config['custom_return_values'] = {}
        for key in self.custom_return_values:
            config['custom_return_values'][key] = self.custom_return_values[key]

        str_fp = io.StringIO()
        config.write(str_fp)
        return str_fp.getvalue()


if __name__ == "__main__":
    cfg = CplateConfig.from_file("cplate_config.ini")
    print(cfg)
    print(cfg.to_string())
