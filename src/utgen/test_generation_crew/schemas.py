from pydantic import BaseModel, Field


class TestCase(BaseModel):
    name: str = Field(..., description="Test name, e.g., 'test_example_function'")  # TODO check if needed
    imports: str = Field(..., description="Test imports: from module import function")
    code: str = Field(..., description="Code: def test_<name>(): ...")


class LLMTestOutput(BaseModel):
    tests: dict[str, TestCase] = Field(..., description="Unit tests dict of TestCase")
