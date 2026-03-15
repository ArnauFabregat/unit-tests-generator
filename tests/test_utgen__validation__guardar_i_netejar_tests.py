from unittest.mock import mock_open, patch

from utgen.validation import guardar_i_netejar_tests


def test_guardar_i_netejar_tests_with_valid_tests():
    tests_valids = [("import os", "print('Hello')")]

    with (
        patch("builtins.open", mock_open()) as mock_file,
        patch("os.makedirs") as mock_makedirs,
        patch("subprocess.run") as mock_subprocess,
    ):
        guardar_i_netejar_tests(tests_valids, desti="../tests/test_generats_llm.py")

        mock_makedirs.assert_called_once_with("../tests", exist_ok=True)
        mock_file.assert_called_once_with("../tests/test_generats_llm.py", "w")

        handle = mock_file()
        handle.write.assert_called_once()

        assert mock_subprocess.call_count == 3
        mock_subprocess.assert_any_call(
            ["ruff", "check", "--select", "I", "--fix", "../tests/test_generats_llm.py"], capture_output=True
        )
        mock_subprocess.assert_any_call(
            ["ruff", "check", "--fix", "../tests/test_generats_llm.py"], capture_output=True
        )
        mock_subprocess.assert_any_call(["ruff", "format", "../tests/test_generats_llm.py"], capture_output=True)


def test_guardar_i_netejar_tests_multiple_tests():
    tests_valids = [("import os", "print('Hello')"), ("import sys", "print('World')")]

    with (
        patch("builtins.open", mock_open()) as mock_file,
        patch("os.makedirs") as mock_makedirs,
        patch("subprocess.run") as mock_subprocess,
    ):
        guardar_i_netejar_tests(tests_valids, desti="../tests/test_generats_llm.py")

        mock_makedirs.assert_called_once_with("../tests", exist_ok=True)

        handle = mock_file()
        handle.write.assert_called_once()

        written_content = handle.write.call_args[0][0]
        assert "import os" in written_content
        assert "import sys" in written_content
        assert "print('Hello')" in written_content
        assert "print('World')" in written_content

        assert mock_subprocess.call_count == 3
