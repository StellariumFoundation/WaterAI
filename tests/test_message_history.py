import pytest
from ii_agent.llm.base import (
    TextPrompt,
    TextResult,
    ToolCall,
    ToolFormattedResult,
)
from ii_agent.llm.message_history import MessageHistory


@pytest.fixture
def message_history():
    return MessageHistory(
        context_manager=None
    )  # Context manager not needed for these tests


class TestToolCallIntegrity:
    def test_ensure_tool_call_integrity_empty_list(self, message_history):
        """Test that empty message list is handled correctly."""
        result = MessageHistory._ensure_tool_call_integrity([])
        assert result == []

    def test_ensure_tool_call_integrity_no_tool_calls(self, message_history):
        """Test that messages without tool calls are unchanged."""
        messages = [
            [TextPrompt(text="Hello")],
            [TextResult(text="Hi there")],
            [TextPrompt(text="How are you?")],
        ]
        result = MessageHistory._ensure_tool_call_integrity(messages)
        assert result == messages

    def test_ensure_tool_call_integrity_matched_tool_calls(self, message_history):
        """Test that matched tool calls and results are preserved."""
        messages = [
            [TextPrompt(text="Run ls")],
            [ToolCall(tool_call_id="123", tool_name="ls", tool_input="{}")],
            [
                ToolFormattedResult(
                    tool_call_id="123",
                    tool_name="ls",
                    tool_output="file1.txt\nfile2.txt",
                )
            ],
            [TextResult(text="Here are your files")],
        ]
        result = MessageHistory._ensure_tool_call_integrity(messages)
        assert result == messages

    def test_ensure_tool_call_integrity_unmatched_tool_calls(self, message_history):
        """Test that unmatched tool calls are removed."""
        messages = [
            [TextPrompt(text="Run commands")],
            [
                ToolCall(tool_call_id="123", tool_name="ls", tool_input="{}"),
                ToolCall(tool_call_id="456", tool_name="pwd", tool_input="{}"),
            ],
            [
                ToolFormattedResult(
                    tool_call_id="123", tool_name="ls", tool_output="file1.txt"
                )
            ],  # Only one result
            [TextResult(text="Done")],
        ]
        result = MessageHistory._ensure_tool_call_integrity(messages)
        expected = [
            [TextPrompt(text="Run commands")],
            [ToolCall(tool_call_id="123", tool_name="ls", tool_input="{}")],
            [
                ToolFormattedResult(
                    tool_call_id="123", tool_name="ls", tool_output="file1.txt"
                )
            ],
            [TextResult(text="Done")],
        ]
        assert result == expected

    def test_ensure_tool_call_integrity_unmatched_results(self, message_history):
        """Test that unmatched tool results are removed."""
        messages = [
            [TextPrompt(text="Run ls")],
            [ToolCall(tool_call_id="123", tool_name="ls", tool_input="{}")],
            [
                ToolFormattedResult(
                    tool_call_id="123", tool_name="ls", tool_output="file1.txt"
                ),
                ToolFormattedResult(
                    tool_call_id="456", tool_name="pwd", tool_output="/home"
                ),  # Unmatched result
            ],
            [TextResult(text="Done")],
        ]
        result = MessageHistory._ensure_tool_call_integrity(messages)
        expected = [
            [TextPrompt(text="Run ls")],
            [ToolCall(tool_call_id="123", tool_name="ls", tool_input="{}")],
            [
                ToolFormattedResult(
                    tool_call_id="123", tool_name="ls", tool_output="file1.txt"
                )
            ],
            [TextResult(text="Done")],
        ]
        assert result == expected
