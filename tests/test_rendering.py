from pages.rendering import markdown_to_html


def test_renders_basic_markdown():
    out = markdown_to_html("# Hello\n\nWorld")
    assert "<h1>Hello</h1>" in out
    assert "<p>World</p>" in out


def test_renders_gfm_table():
    md = "| a | b |\n|---|---|\n| 1 | 2 |\n"
    out = markdown_to_html(md)
    assert "<table>" in out
    assert "<td>1</td>" in out


def test_renders_task_list():
    out = markdown_to_html("- [x] done\n- [ ] todo\n")
    assert 'type="checkbox"' in out


def test_strikethrough():
    assert "<s>" in markdown_to_html("~~gone~~")


def test_escapes_raw_html_to_prevent_xss():
    out = markdown_to_html("<script>alert(1)</script>")
    assert "<script>" not in out
