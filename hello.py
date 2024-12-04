from datetime import date

from rex import lit

from syntax_study.analysis import RepoAnalyzer, Syntax

# Define a syntax for finding question operators
question_operator = lit("?").compile()
question_mark_syntax = Syntax(pattern=question_operator, release_date=date(2016, 11, 10))

# Replace the token with your GitHub token
analyzer = (
    RepoAnalyzer.from_token(
        "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"
    )
    .add_syntax(question_mark_syntax)
    .add_file_suffix(".rs")
)

analyzer.analyze_repo("alacritty/alacritty", "alacritty/src")
