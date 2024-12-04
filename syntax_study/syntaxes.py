import re
from datetime import date

from rex import ANY, WS, char_cls, lit, seq

from syntax_study.analysis import Syntax

# The `try!` macro was deprecated in Rust 1.13 and replaced by the `?` operator.
# https://blog.rust-lang.org/2016/11/10/Rust-1.13.html
try_macro_syntax = Syntax(pattern=lit("try!").compile())
try_operator_syntax = Syntax(pattern=lit("?").compile(), release_date=date(2016, 1, 1))

# Rust introduced `impl Trait` syntax in version 1.26.
# https://blog.rust-lang.org/2018/05/10/Rust-1.26.html
impl_trait_arg = Syntax(
    pattern=seq(
        "fn" | "pub fn" + WS[1:],
        ANY[1:] + WS[:],
        "(",
        char_cls(")", negate=True)[1:],
        lit("mut").optional(),
        ANY[1:] + WS[:] + ":" + WS[:],
        "impl" + WS[1:],
        ANY[1:],
        ")",
        WS[:],
        "{",
    ).compile(),
    release_date=date(2018, 5, 1),
)
impl_trait_return = Syntax(
    pattern=seq(
        "fn" | "pub fn" + WS[1:],
        ANY[1:] + WS[:],
        "(" + ANY[:] + ")" + WS[:],
        "->" + WS[:],
        "impl" + WS[1:],
        ANY[1:],
        "{",
    ).compile(),
    release_date=date(2018, 5, 1),
)

# Rust introduced async/await syntax in version 1.39.
# https://blog.rust-lang.org/2019/11/07/Rust-1.39.0.html
async_syntax = Syntax(
    pattern=seq("async", WS[1:], "fn", ANY[:], lit("{")).compile(),
    release_date=date(2019, 11, 1),
)


# Rust introduced const generics syntax in version 1.51.
# https://blog.rust-lang.org/2021/03/25/Rust-1.51.0.html
const_generics_syntax = Syntax(
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
    pattern=seq(
        "for", WS[1:], NON_REFERENCE[1:], WS[1:], "in", WS[1:], NON_REFERENCE[1:], WS[1:], "{"
    ).compile(),
    release_date=date(2021, 5, 1),
)
legacy_into_iterator_syntax = Syntax(
    pattern=seq(
        "for", WS[1:], "&", ANY[1:], WS[1:], "in", WS[1:], "&", ANY[1:], WS[1:], "{"
    ).compile(),
    release_date=date(2015, 1, 1),
)
