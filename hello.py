from datetime import date

from rex import lit

from rust_syntax_study.analysis import RepoAnalyzer, Syntax

# Define a syntax for finding question operators
question_operator = lit("?").compile()
question_mark_syntax = Syntax(question_operator, date(2016, 11, 10))

# Replace the token with your GitHub token
analyzer = RepoAnalyzer.from_token("gh_xxx").add_syntax(question_mark_syntax).add_file_suffix(".rs")
for found_syntax in analyzer.find_syntax_in_repo("alacritty/alacritty", "alacritty/src"):
    print(found_syntax)