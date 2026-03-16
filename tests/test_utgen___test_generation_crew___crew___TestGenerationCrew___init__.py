from utgen.test_generation_crew.crew import GUARDRAIL_MAX_RETRIES, TestGenerationCrew


def test_init_with_default_values():
    """
    Test TestGenerationCrew.__init__ with default values.
    """
    # Arrange
    # Act
    crew = TestGenerationCrew()

    # Assert
    assert crew._guardrail_max_retries == GUARDRAIL_MAX_RETRIES
    assert crew._verbose is False


def test_init_with_custom_values():
    """
    Test TestGenerationCrew.__init__ with custom values.
    """
    # Arrange
    custom_retries = 10
    verbose = True

    # Act
    crew = TestGenerationCrew(guardrail_max_retries=custom_retries, verbose=verbose)

    # Assert
    assert crew._guardrail_max_retries == custom_retries
    assert crew._verbose is True


def test_init_with_zero_retries():
    """
    Test TestGenerationCrew.__init__ with zero retries.
    """
    # Arrange
    zero_retries = 0

    # Act
    crew = TestGenerationCrew(guardrail_max_retries=zero_retries)

    # Assert
    assert crew._guardrail_max_retries == zero_retries
    assert crew._verbose is False


def test_init_with_negative_retries():
    """
    Test TestGenerationCrew.__init__ with negative retries.
    """
    # Arrange
    negative_retries = -5

    # Act
    crew = TestGenerationCrew(guardrail_max_retries=negative_retries)

    # Assert
    assert crew._guardrail_max_retries == negative_retries
    assert crew._verbose is False


def test_init_with_large_retries():
    """
    Test TestGenerationCrew.__init__ with a large number of retries.
    """
    # Arrange
    large_retries = 1000000

    # Act
    crew = TestGenerationCrew(guardrail_max_retries=large_retries)

    # Assert
    assert crew._guardrail_max_retries == large_retries
    assert crew._verbose is False


def test_init_with_non_integer_retries():
    """
    Test TestGenerationCrew.__init__ with a non-integer retries value.
    """
    # Arrange
    non_integer_retries = 5.5

    # Act
    crew = TestGenerationCrew(guardrail_max_retries=non_integer_retries)

    # Assert
    assert crew._guardrail_max_retries == non_integer_retries
    assert crew._verbose is False
