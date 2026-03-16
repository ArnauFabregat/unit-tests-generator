from utgen.validation import validate_individual_test


def test_validate_individual_test_with_failing_test():
    """
    Test validate_individual_test with a test that should fail.
    """
    # Arrange
    import_code = "from math import sqrt"
    test_code = """
    def test_sqrt():
        assert sqrt(4) == 3  # This will fail
    """

    # Act
    result = validate_individual_test(import_code, test_code)

    # Assert
    assert result is False


def test_validate_individual_test_with_syntax_error():
    """
    Test validate_individual_test with code containing a syntax error.
    """
    # Arrange
    import_code = "from math import sqrt"
    test_code = """
    def test_sqrt():
        assert sqrt(4) == 2
    def invalid_function  # Missing colon
    """

    # Act
    result = validate_individual_test(import_code, test_code)

    # Assert
    assert result is False


def test_validate_individual_test_with_no_tests():
    """
    Test validate_individual_test with no test functions defined.
    """
    # Arrange
    import_code = "from math import sqrt"
    test_code = """
    # No test functions defined
    x = 5
    y = 10
    """

    # Act
    result = validate_individual_test(import_code, test_code)

    # Assert
    assert result is False


def test_validate_individual_test_with_import_error():
    """
    Test validate_individual_test with an import that will fail.
    """
    # Arrange
    import_code = "from nonexistent_module import something"
    test_code = """
    def test_example():
        assert True
    """

    # Act
    result = validate_individual_test(import_code, test_code)

    # Assert
    assert result is False
