import re
from collections.abc import Iterator
from datetime import date
from pathlib import Path
from typing import Self

from github import Github
from github.Auth import Auth, Login, Token
from pydantic import BaseModel
from rex import ANY, seq
from rich.progress import track


class Syntax(BaseModel):
    """Defines a syntax for analysis"""

    pattern: re.Pattern
    release_date: date | None = None

    def find_in_text(self, text: str) -> Iterator["FoundSyntax"]:
        """Find syntax in text"""
        return find_syntax_in_text(text, self)

    def __hash__(self) -> int:
        return hash(self.pattern.pattern)


class FoundSyntax(BaseModel):
    """Information of a syntax found in a file"""

    syntax: Syntax
    path: str
    line: int
    text: str

    @property
    def release_date(self) -> date | None:
        return self.syntax.release_date


class RepoSummary(BaseModel):
    repo_name: str
    first_commit_date: date
    last_commit_date: date
    total_commits: int
    stars: int
    syntaxes: set[Syntax]

    def latest_syntax(self) -> Syntax:
        """Return the latest syntax found"""
        return sorted(self.syntaxes, key=lambda s: s.release_date or date.min)[-1]


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
        yield FoundSyntax(syntax=syntax, path="", line=line, text=text[start:end])


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
        for content_file in track(
            contents,
            description=f"Analyzing {repo_name}",
        ):
            match content_file.type:
                case "file" if content_file.name.endswith(tuple(self.file_suffixes)):
                    text = content_file.decoded_content.decode("utf-8")
                    text = remove_comments(text)
                    for syntax in self.syntaxes:
                        yield from (
                            FoundSyntax(
                                syntax=s.syntax, path=content_file.path, line=s.line, text=s.text
                            )
                            for s in find_syntax_in_text(text, syntax)
                        )

                case "dir":
                    dir_contents = repo.get_contents(content_file.path)
                    assert isinstance(dir_contents, list)
                    contents.extend(dir_contents)

    def analyze_repo(
        self,
        repo_name: str,
        root: str = "",
        output_dir: Path = Path("results"),
        force_update: bool = False,
    ) -> RepoSummary:
        """Analyze a GitHub repository"""
        assert not output_dir.is_file(), "Output directory must be a directory"
        if not output_dir.exists():
            output_dir.mkdir(parents=True)

        output_path = output_dir / f"{repo_name.replace('/', '_')}.json"
        if output_path.exists() and not force_update:
            return RepoSummary.model_validate_json(output_path.read_text())

        repo = self.github.get_repo(repo_name)
        commits = repo.get_commits()
        first_commit = commits.reversed[0]
        last_commit = commits[0]
        summary = RepoSummary(
            repo_name=repo_name,
            first_commit_date=first_commit.commit.author.date.date(),
            last_commit_date=last_commit.commit.author.date.date(),
            total_commits=repo.get_commits().totalCount,
            stars=repo.stargazers_count,
            syntaxes=set([fs.syntax for fs in self.find_syntax_in_repo(repo_name, root)]),
        )
        output_path.write_text(summary.model_dump_json(indent=2))
        return summary
