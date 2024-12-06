from syntax_study.analysis import RepoAnalyzer
from syntax_study.syntaxes import ALL_SYNTAXES

# Replace the token with your GitHub token
analyzer = RepoAnalyzer.from_token("github...").add_file_suffix(".rs")
for syntax in ALL_SYNTAXES:
    analyzer.add_syntax(syntax)

analyzer.analyze_repo("alacritty/alacritty", "alacritty/src", force_update=True)
