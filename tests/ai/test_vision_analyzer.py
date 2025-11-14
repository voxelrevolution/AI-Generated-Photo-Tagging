import sys
import os
import pytest

# Add the project root to the Python path to allow importing from 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.ai.vision_analyzer import VisionAnalyzer

def test_build_vision_prompt():
    """
    Tests the _build_vision_prompt function to ensure it correctly constructs
    the prompt string for the vision AI model.
    """
    # The vision prompt is currently a static string, so this test validates
    # that the function returns it correctly.
    analyzer = VisionAnalyzer(config={'VISION_MODEL_PROMPT': 'Describe this image in detail.'})
    
    # The method under test is private, but we test it directly as per requirements.
    prompt = analyzer._build_vision_prompt()
    
    assert prompt == 'Describe this image in detail.'

def test_build_vision_prompt_with_different_config():
    """
    Tests that the _build_vision_prompt function correctly uses the prompt
    from the configuration provided to it.
    """
    analyzer = VisionAnalyzer(config={'VISION_MODEL_PROMPT': 'What objects are in this image?'})
    prompt = analyzer._build_vision_prompt()
    assert prompt == 'What objects are in this image?'
