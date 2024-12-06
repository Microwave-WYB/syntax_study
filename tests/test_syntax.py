from syntax_study.syntaxes import (
    apit_syntax,
    async_syntax,
    const_generics_syntax,
    gat_syntax,
    inline_const_syntax,
    into_iterator_syntax,
    legacy_into_iterator_syntax,
    let_else_syntax,
    once_cell,
    once_lock,
    rpit_syntax,
    rpitit_impl_syntax,
    rpitit_syntax,
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


def test_apit_syntax() -> None:
    code = """
    fn parse_csv_document(src: impl BufRead) {
        // implementation
    }
    """
    assert apit_syntax.pattern.findall(code) == ["fn parse_csv_document(src: impl BufRead) {"]


def test_rpit_syntax() -> None:
    code = """
    pub fn make_iter() -> impl Iterator<Item=i32> {
        (0..5).filter(|x| x % 2 == 0)
    }
    """
    assert rpit_syntax.pattern.findall(code) == ["pub fn make_iter() -> impl Iterator<Item=i32> {"]


def test_rpitit_syntax() -> None:
    code = """
    trait Container {
        fn items(&self) -> impl Iterator<Item = Widget>;
    }
    """
    assert rpitit_syntax.pattern.findall(code) == [
        "trait Container {\n" "        fn items(&self) -> impl Iterator<Item = Widget>;",
    ]


def test_rpitit_impl_syntax() -> None:
    code = """
    impl Container for Vec<Widget> {
        fn items(&self) -> impl Iterator<Item = Widget> {
            self.iter().cloned()
        }
    }
    """
    assert rpitit_impl_syntax.pattern.findall(code) == [
        "impl Container for Vec<Widget> {\n"
        "        fn items(&self) -> impl Iterator<Item = Widget> {",
    ]


def test_let_else_syntax() -> None:
    code = """
    let PATTERN: TYPE = EXPRESSION else {
        DIVERGING_CODE;
    };
    """
    assert let_else_syntax.pattern.findall(code) == ["let PATTERN: TYPE = EXPRESSION else {"]


def test_gat_syntax() -> None:
    code = """
    trait Foo {
        type Bar<'x>;
    }
    """
    assert gat_syntax.pattern.findall(code) == ["type Bar<'x>;"]


def test_inline_const() -> None:
    code = """
    let foo = [const { None }; 100];
    """
    assert inline_const_syntax.pattern.findall(code) == ["const {"]


def test_once_cell_syntax() -> None:
    code = """
    static WINNER: OnceCell<&str> = OnceLock::new();
    """
    assert once_cell.pattern.findall(code) == ["OnceCell<"]


def test_once_lock_syntax() -> None:
    code = """
    static WINNER: OnceCell<&str> = OnceLock::new();
    """
    assert once_lock.pattern.findall(code) == ["OnceLock"]
