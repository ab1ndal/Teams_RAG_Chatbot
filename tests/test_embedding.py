from app.embedding import embed_text
import pytest

TEST_CASES = [
    ("Basic English", "Hello, world!",None),
    ("Engineering definition", "A footing is the part of a foundation that directly transfers load to the soil.", None),
    ("Technical sentence", "Load combinations in structural design ensure safety under various conditions.", None),
    ("Long input", "This is a very long input. " * 100, None),
    ("Numbers only", "1234567890",None),
    ("Alphanumeric", "abc123XYZ", None),
    ("Whitespace", "   \t\n\r  ", ValueError),
    ("Punctuation", "Hello! How are you?", None),
    ("Special characters", "!@#$%^&*()_+", None),
    ("Mixed case", "HelloWorld123", None),
    ("Empty string", "", ValueError),
    ("Whitespace only", "  ", ValueError),
    ("Single character", "A", None),
    ("Multiple spaces", "This  is  a  test.", None),
    ("Tab characters", "This\tis\ta\ttest.", None),
    ("Newline characters", "This\nis\na\ntest.", None),
    ("Unicode characters", "こんにちは世界", None),
    ("Symbols", "@#$%^&*()_+=-", None),
    ("Non-English – Hindi", "यह एक नींव का उदाहरण है।", None),
    ("Non-English – Chinese", "这是一种结构基础。", None)
]

@pytest.mark.parametrize("label,text,expected", TEST_CASES)
def test_embedding(label, text, expected):
    if expected is ValueError:
        with pytest.raises(ValueError):
            embed_text(text)
    else:
        embedding = embed_text(text)
        assert isinstance(embedding, list), f"{label}: Output is not a list"
        assert len(embedding) == 1536, f"{label}: Unexpected embedding length"
        assert all(isinstance(i, float) for i in embedding), f"{label}: Not all elements are floats"
        assert any(abs(x) > 1e-8 for x in embedding), f"{label}: Embedding is all near-zero"

