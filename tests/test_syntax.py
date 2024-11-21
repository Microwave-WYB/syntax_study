from syntax_study.syntaxes import (
    async_syntax,
    const_generics_syntax,
    impl_trait_arg,
    impl_trait_return,
    into_iterator_syntax,
    legacy_into_iterator_syntax,
)


def test_async_syntax() -> None:
    code = """
    async fn fetch() -> String {
        "data".to_string()
    }
    let data = fetch().await;
    """
    assert async_syntax.pattern.findall(code) == ["async fn fetch() -> String {"]


def test_const_generics_syntax() -> None:
    code = """
    struct Matrix<T, const N: usize> {
        data: [T; N],
    }
    """
    assert const_generics_syntax.pattern.findall(code) == ["<T, const N: usize>"]


def test_into_iterator_syntax() -> None:
    code = """
    for x in vec {
        println!("{}", x);
    }
    """
    legacy_code = """
    for &x in &vec {
        println!("{}", x);
    }
    """
    assert into_iterator_syntax.pattern.findall(code) == ["for x in vec {"]
    assert into_iterator_syntax.pattern.findall(legacy_code) == []
    assert legacy_into_iterator_syntax.pattern.findall(legacy_code) == ["for &x in &vec {"]
    assert legacy_into_iterator_syntax.pattern.findall(code) == []


def test_impl_trait_arg() -> None:
    code = """
    fn parse_csv_document(src: impl BufRead) {
        // implementation
    }
    """
    assert impl_trait_arg.pattern.findall(code) == ["fn parse_csv_document(src: impl BufRead) {"]


def test_impl_trait_return() -> None:
    code = """
    pub fn make_iter() -> impl Iterator<Item=i32> {
        (0..5).filter(|x| x % 2 == 0)
    }
    """
    assert impl_trait_return.pattern.findall(code) == [
        "pub fn make_iter() -> impl Iterator<Item=i32> {"
    ]
