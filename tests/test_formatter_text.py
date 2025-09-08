import formatter_text as ft


def test_highlight_code_blocks_single():
    text = "Текст до блока\t\n\n```bash\nбла\n-бла\t-бла\n```\nТекст после"
    formatted, blocks = ft.highlight_code_blocks(text)
    assert len(blocks) == 1
    assert blocks[0].strip() == "бла\n-бла\t-бла"
    assert "[Блок #1]" in formatted
    assert "бла\n-бла\t-бла" in formatted
    assert ft.YELLOW in formatted and ft.RESET in formatted
    assert "```" not in formatted


def test_highlight_code_blocks_multiple_numbering():
    text = "\nТекст перед блоком\n ```py\nбла\n\t-бла(1)\n``` \tТекст между блоками\n\n```sh  \nбла\n\t-бла(2)\n\t``` Текст после блоков"
    formatted, blocks = ft.highlight_code_blocks(text)
    assert len(blocks) == 2
    assert blocks == ["бла\n\t-бла(1)", "бла\n\t-бла(2)"]
    assert "[Блок #1]" in formatted and "[Блок #2]" in formatted
    assert "```" not in formatted


def test_highlight_explanation_blocks():
    text = "Перед \t\n### пояснение внутри блока ### после\n\t"
    formatted = ft.highlight_explanation_blocks(text)
    assert "пояснение внутри блока" in formatted
    assert ft.GRAY_ITALIC in formatted and ft.RESET in formatted
    assert "###" not in formatted


def test_highlight_inline_code_and_bold():
    text = "Используйте `cmd --help` и **важное** слово"
    out_inline = ft.highlight_inline_code(text)
    assert ft.GREEN in out_inline and "cmd --help" in out_inline and ft.RESET in out_inline
    out_bold = ft.highlight_bold(text)
    assert ft.BOLD in out_bold and "важное" in out_bold and ft.RESET in out_bold


def test_format_answer_combined():
    text = "Перед **жирно** и `inline` ### заметка ### ```bash\necho hi\n``` после"
    formatted, blocks = ft.format_answer(text)
    # маркеры исходные должны быть убраны/заменены
    assert "```" not in formatted
    assert "`inline`" not in formatted
    assert "**жирно**" not in formatted
    # оформленные элементы и блок кода присутствуют
    assert "[Блок #1]" in formatted
    assert "echo hi" in formatted
    assert "inline" in formatted and "жирно" in formatted
    assert blocks