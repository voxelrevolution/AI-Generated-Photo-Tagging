import sys
import os
import pytest

# Add the project root to the Python path to allow importing from 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.ai.tag_processor import TagProcessor

# Test cases for the _build_prompt function
# The function should just embed the raw text into the prompt, so the input is the expected fragment.
prompt_test_cases = [
    ("A picture of a happy dog", "A picture of a happy dog"),
    ("A photo of a man running", "A photo of a man running"),
    ("An image of the number 24", "An image of the number 24"),
    ("A snapshot of a sign that says 'Do not enter'", "A snapshot of a sign that says 'Do not enter'"),
    ("My friend Mason is in this picture", "My friend Mason is in this picture"),
    ("This is not a cat", "This is not a cat"),
    ("The event was on 2025-11-13", "The event was on 2025-11-13"),
    ("A beautiful sunset over the mountains", "A beautiful sunset over the mountains"),
    ("Two people, a man and a woman, smiling", "Two people, a man and a woman, smiling"),
    ("A close-up of a flower with a bee on it", "A close-up of a flower with a bee on it"),
]

@pytest.mark.parametrize("input_text, expected_fragment", prompt_test_cases)
def test_build_prompt(input_text, expected_fragment):
    """
    Tests the _build_prompt function to ensure it correctly formats the prompt
    by embedding the original, unmodified text from the vision AI's output.
    """
    # Instantiate the processor with a dummy config
    processor = TagProcessor(config={'TEXT_MODEL_NAME': 'dummy_model', 'TEXT_MODEL_PROMPT_TEMPLATE': 'Analyze this: {text_input}'})
    
    # The method under test is private, which is not ideal for unit testing,
    # but we are testing it directly as per requirements.
    # Accessing it using the "name mangling" syntax for private methods.
    prompt = processor._build_prompt(input_text)
    
    # The full prompt will be "Analyze this: [input_text]".
    # We check that the original input text is present in the prompt.
    assert expected_fragment in prompt
    assert "Analyze this:" in prompt

def test_build_prompt_handles_empty_string():
    """
    Tests that _build_prompt handles an empty string gracefully.
    """
    processor = TagProcessor(config={'TEXT_MODEL_NAME': 'dummy_model', 'TEXT_MODEL_PROMPT_TEMPLATE': 'Analyze this: {text_input}'})
    prompt = processor._build_prompt("")
    assert "" in prompt
    assert "Analyze this:" in prompt
