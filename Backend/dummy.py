def reverse_string(string):
    return string[::-1]


def test_reverse_str():
    original_str = "HELLO"
    expected_str = "OLLEH"
    result = reverse_string(original_str)
    print(result)
    print(expected_str)
    assert result == expected_str


test_reverse_str()
