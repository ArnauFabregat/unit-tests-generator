from unittest.mock import patch


def test_test_generation_crew_init_default_values():
    """Test TestGenerationCrew.__init__ with default values."""
    # Mock the constant GUARDRAIL_MAX_RETRIES
    with patch("utgen.test_generation_crew.crew.GUARDRAIL_MAX_RETRIES", 3):
        from utgen.test_generation_crew.crew import TestGenerationCrew

        # Create instance with default parameters
        crew = TestGenerationCrew()

        # Check that default values are set
        assert crew._guardrail_max_retries == 3
        assert crew._verbose is False


def test_test_generation_crew_init_custom_values():
    """Test TestGenerationCrew.__init__ with custom values."""
    with patch("utgen.test_generation_crew.crew.GUARDRAIL_MAX_RETRIES", 3):
        from utgen.test_generation_crew.crew import TestGenerationCrew

        # Create instance with custom parameters
        crew = TestGenerationCrew(guardrail_max_retries=10, verbose=True)

        # Check that custom values are set
        assert crew._guardrail_max_retries == 10
        assert crew._verbose is True


def test_test_generation_crew_init_with_zero_retries():
    """Test TestGenerationCrew.__init__ with zero retries."""
    with patch("utgen.test_generation_crew.crew.GUARDRAIL_MAX_RETRIES", 3):
        from utgen.test_generation_crew.crew import TestGenerationCrew

        # Create instance with zero retries
        crew = TestGenerationCrew(guardrail_max_retries=0, verbose=False)

        assert crew._guardrail_max_retries == 0
        assert crew._verbose is False


def test_test_generation_crew_init_large_retries():
    """Test TestGenerationCrew.__init__ with large retry value."""
    with patch("utgen.test_generation_crew.crew.GUARDRAIL_MAX_RETRIES", 3):
        from utgen.test_generation_crew.crew import TestGenerationCrew

        # Create instance with large retry value
        crew = TestGenerationCrew(guardrail_max_retries=1000, verbose=True)

        assert crew._guardrail_max_retries == 1000
        assert crew._verbose is True
