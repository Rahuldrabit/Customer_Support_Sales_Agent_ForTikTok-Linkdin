"""Unit tests for agent tools."""

from app.agent.tools import (
    extract_sentiment_indicators,
    detect_urgency,
    extract_order_number,
    format_context
)


def test_extract_sentiment_indicators():
    """Test sentiment extraction."""
    # Positive sentiment
    positive_text = "Thank you so much! This is great!"
    assert extract_sentiment_indicators(positive_text) > 0
    
    # Negative sentiment
    negative_text = "This is terrible and unacceptable!"
    assert extract_sentiment_indicators(negative_text) < 0
    
    # Neutral sentiment
    neutral_text = "I have a question about my order."
    sentiment = extract_sentiment_indicators(neutral_text)
    assert -0.5 <= sentiment <= 0.5


def test_detect_urgency():
    """Test urgency detection."""
    # Urgent message
    urgent_1 = "This is ridiculous!!! I need help NOW!"
    assert detect_urgency(urgent_1) == True
    
    urgent_2 = "I've been charged twice, this is unacceptable"
    assert detect_urgency(urgent_2) == True
    
    # Non-urgent message
    normal = "Hello, I have a question about pricing"
    assert detect_urgency(normal) == False


def test_extract_order_number():
    """Test order number extraction."""
    # With order number
    text_1 = "My order #AB123456 hasn't arrived"
    order_num = extract_order_number(text_1)
    assert order_num is not None
    assert "123456" in order_num
    
    # Without order number
    text_2 = "I have a general question"
    assert extract_order_number(text_2) is None


def test_format_context():
    """Test context formatting."""
    messages = [
        {"sender_type": "user", "content": "Hello"},
        {"sender_type": "agent", "content": "Hi there!"},
        {"sender_type": "user", "content": "I need help"}
    ]
    
    context = format_context(messages)
    assert "USER: Hello" in context
    assert "AGENT: Hi there!" in context
    assert "USER: I need help" in context
    
    # Empty messages
    assert format_context([]) == "No previous context."
