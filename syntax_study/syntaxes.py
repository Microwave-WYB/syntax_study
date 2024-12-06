import re
from datetime import date

from rex import ANY, WS, char_cls, lit, seq

from syntax_study.analysis import Syntax

NON_BRACE = char_cls("{}", negate=True)


# The `try!` macro was deprecated in Rust 1.13 and replaced by the `?` operator.
# https://blog.rust-lang.org/2016/11/10/Rust-1.13.html
try_macro_syntax = Syntax(
    name="try macro",
    pattern=lit("try!").compile(),
)
try_operator_syntax = Syntax(
    name="try operator",
    pattern=lit("?").compile(),
    release_date=date(2016, 11, 10),
)

# Rust introduced `impl Trait` syntax in version 1.26.
# https://blog.rust-lang.org/2018/05/10/Rust-1.26.html
apit_syntax = Syntax(
    name="Argument Position impl Trait",
    pattern=seq(
        "fn" | "pub fn" + WS[1:],
        ANY[1:] + WS[:],
        "(",
        char_cls(")", negate=True)[1:],
        lit("mut").optional(),
        ANY[1:] + WS[:] + ":" + WS[:],
        "impl" + WS[1:],
        ANY[1:],
        ")" + WS[:],
        "{",
    ).compile(),
    release_date=date(2018, 5, 10),
)
rpit_syntax = Syntax(
    name="Return Position impl Trait",
    pattern=seq(
        "fn" | "pub fn" + WS[1:],
        ANY[1:] + WS[:],
        "(" + ANY[:] + ")" + WS[:],
        "->" + WS[:],
        "impl" + WS[1:],
        ANY[1:],
        "{",
    ).compile(),
    release_date=date(2018, 5, 10),
)


# https://blog.rust-lang.org/2023/12/21/async-fn-rpit-in-traits.html#where-the-gaps-lie
rpitit_syntax = Syntax(
    name="Return Position impl Trait in Traits",
    pattern=seq(
        "trait" + WS[1:],
        NON_BRACE[1:] + WS[:],  # Trait name and potential generics
        "{" + WS[:],
        ANY[:],  # Other potential trait items
        "fn" + WS[1:],
        NON_BRACE[1:] + WS[:],  # Function name and parameters
        "->" + WS[:],
        "impl" + WS[1:],
        NON_BRACE[1:],  # The actual return type after impl
        ";",  # End of trait method declaration
    ).compile(),
    release_date=date(2023, 12, 21),
)
rpitit_impl_syntax = Syntax(
    name="Return Position impl Trait Implementation",
    pattern=seq(
        "impl" + WS[1:],
        NON_BRACE[1:] + WS[:],  # Trait name and potential type
        "{" + WS[:] + ANY[:],  # Other potential impl items
        "fn" + WS[1:],
        NON_BRACE[1:] + WS[:],  # Function name and parameters
        "->" + WS[:],
        "impl" + WS[1:],
        NON_BRACE[1:],  # The actual return type after impl
        "{",  # Start of implementation block
    ).compile(),
    release_date=date(2023, 12, 21),
)

# Rust introduced async/await syntax in version 1.39.
# https://blog.rust-lang.org/2019/11/07/Rust-1.39.0.html
async_syntax = Syntax(
    name="async",
    pattern=seq("async", WS[1:], "fn", ANY[:], lit("{")).compile(),
    release_date=date(2019, 11, 1),
)


# Rust introduced const generics syntax in version 1.51.
# https://blog.rust-lang.org/2021/03/25/Rust-1.51.0.html
const_generics_syntax = Syntax(
    name="const generics",
    pattern=re.compile(
        r"<(?:[^<>]|<(?:[^<>]|<[^<>]*>)*>)*\bconst\b(?:[^<>]|<(?:[^<>]|<[^<>]*>)*>)*>"
    ),
    release_date=date(2021, 3, 1),
)


# Rust introduced the new, more ergonomic syntax for atray::IntoIter in version 1.51
# This avoids the need to use `&` to dereference the iterator.
# https://blog.rust-lang.org/2021/03/25/Rust-1.51.0.html
NON_REFERENCE = char_cls("&", negate=True)
into_iterator_syntax = Syntax(
    name="IntoIter",
    pattern=seq(
        "for", WS[1:], NON_REFERENCE[1:], WS[1:], "in", WS[1:], NON_REFERENCE[1:], WS[1:], "{"
    ).compile(),
    release_date=date(2021, 3, 25),
)
legacy_into_iterator_syntax = Syntax(
    name="Legacy IntoIter",
    pattern=seq(
        "for", WS[1:], "&", ANY[1:], WS[1:], "in", WS[1:], "&", ANY[1:], WS[1:], "{"
    ).compile(),
)

# https://blog.rust-lang.org/2022/11/03/Rust-1.65.0.html#let-else-statements
let_else_syntax = Syntax(
    name="let else",
    pattern=seq(
        "let" + WS[1:],
        ANY[1:] + WS[:],
        "=" + WS[:],
        ANY[1:] + WS[:],
        "else" + WS[:],
        "{",
    ).compile(),
    release_date=date(2022, 11, 3),
)

gat_syntax = Syntax(
    name="Generic Associated Types",
    pattern=seq(
        "type" + WS[1:],
        ANY[1:] + WS[:],
        "<",
        ANY[1:],
        ">",
        WS[:] + ";",
    ).compile(),
    release_date=date(2022, 11, 1),
)

# https://blog.rust-lang.org/2024/06/13/Rust-1.79.0.html
inline_const_syntax = Syntax(
    name="Inline const expressions",
    pattern=seq("const" + WS[:], "{").compile(),
    release_date=date(2024, 6, 13),
)
# https://blog.rust-lang.org/2023/06/01/Rust-1.70.0.html
once_cell = Syntax(
    name="OnceCell",
    pattern=seq("OnceCell" + lit("<")[:1]).compile(),
    release_date=date(2023, 6, 1),
)

once_lock = Syntax(
    name="OnceLock",
    pattern=seq("OnceLock" + WS[:]).compile(),
    release_date=date(2023, 6, 1),
)

# All syntaxes defined in this module
ALL_SYNTAXES = [
    try_macro_syntax,
    try_operator_syntax,
    apit_syntax,
    rpit_syntax,
    rpitit_syntax,
    rpitit_impl_syntax,
    async_syntax,
    const_generics_syntax,
    into_iterator_syntax,
    legacy_into_iterator_syntax,
    let_else_syntax,
    gat_syntax,
    inline_const_syntax,
    once_cell,
    once_lock,
]
