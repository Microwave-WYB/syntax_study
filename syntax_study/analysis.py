import re
from collections.abc import Iterator
from datetime import date
from typing import Self

from github import Github
from github.Auth import Auth, Login, Token
from pydantic.dataclasses import dataclass
from rex import ANY, seq


@dataclass
class Syntax:
    """Defines a syntax for analysis"""

    pattern: re.Pattern
    release_date: date | None = None

    def find_in_text(self, text: str) -> Iterator["FoundSyntax"]:
        """Find syntax in text"""
        return find_syntax_in_text(text, self)


@dataclass
class FoundSyntax:
    """Information of a syntax found in a file"""

    syntax: Syntax
    path: str
    line: int
    text: str

    @property
    def release_date(self) -> date | None:
        return self.syntax.release_date


@dataclass
class RepoSummary:
    repo_name: str
    tags: list[str]
    first_commit_date: date
    last_commit_date: date
    total_commits: int
    stars: int
    found_syntaxes: list[FoundSyntax]

    def latest_syntax(self) -> list[FoundSyntax]:
        """Return the latest syntax found"""
        latest_date = max(
            syntax.release_date for syntax in self.found_syntaxes if syntax.release_date is not None
        )
        return [
            syntax for syntax in self.found_syntaxes if syntax.syntax.release_date == latest_date
        ]


def remove_comments(text: str) -> str:
    """
    Remove comments from source code.
    >>> remove_comments("// This is a comment")
    ''
    >>> remove_comments("/* This is a comment */")
    ''
    >>> remove_comments("let x = 42; // This is a comment")
    'let x = 42; '
    """
    comment_regex = seq("//", ANY[:]) | seq("/*", ANY[:], "*/")
    return comment_regex.sub("", text)


def find_syntax_in_text(text: str, syntax: Syntax) -> Iterator[FoundSyntax]:
    """
    Find syntax in source code.
    >>> from rex import WS, lit
    >>> list(find_syntax_in_text("let x = 42;", Syntax("let_binding", lit("let ") , date(2015, 1, 15))))
    [FoundSyntax(syntax=Syntax(name='let_binding', pattern=Pattern('let\\\\ '), release_date=datetime.date(2015, 1, 15)), path='', line=1, text='let ')]
    """
    for match in syntax.pattern.finditer(text):
        start, end = match.span()
        line = text.count("\n", 0, start) + 1
        yield FoundSyntax(syntax, "", line, text[start:end])


class RepoAnalyzer:
    """Class to analyze repositories"""

    def __init__(self, auth: Auth):
        self.github = Github(auth=auth)
        self.syntaxes: list[Syntax] = []
        self.file_suffixes: list[str] = []

    @classmethod
    def from_username_password(
        cls: type["RepoAnalyzer"], username: str, password: str
    ) -> "RepoAnalyzer":
        """Use username and password to authenticate"""
        return cls(Login(username, password))

    @classmethod
    def from_token(cls: type["RepoAnalyzer"], token: str) -> "RepoAnalyzer":
        """Use a token to authenticate"""
        return cls(Token(token))

    def add_syntax(self, syntax: Syntax) -> Self:
        """Add a syntax to the analyzer"""
        self.syntaxes.append(syntax)
        return self

    def add_file_suffix(self, suffix: str) -> Self:
        """Add a file suffix to the analyzer"""
        self.file_suffixes.append(suffix)
        return self

    def find_syntax_in_repo(self, repo_name: str, root: str = "") -> Iterator[FoundSyntax]:
        """Find syntaxes in a GitHub repository"""
        repo = self.github.get_repo(repo_name)
        contents = repo.get_contents(root)
        assert isinstance(contents, list)
        for content_file in contents:
            match content_file.type:
                case "file" if content_file.name.endswith(tuple(self.file_suffixes)):
                    text = content_file.decoded_content.decode("utf-8")
                    text = remove_comments(text)
                    for syntax in self.syntaxes:
                        yield from (
                            FoundSyntax(s.syntax, content_file.path, s.line, s.text)
                            for s in find_syntax_in_text(text, syntax)
                        )

                case "dir":
                    dir_contents = repo.get_contents(content_file.path)
                    assert isinstance(dir_contents, list)
                    contents.extend(dir_contents)
