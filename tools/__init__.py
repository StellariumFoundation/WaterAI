from .bash_tool import BashTool
from .sequential_thinking_tool import SequentialThinkingTool
from .str_replace_tool_relative import StrReplaceEditorTool
from .tool_manager import AgentToolManager, get_system_tools
from .visit_webpage_tool import VisitWebpageTool

# Tools that need input truncation (ToolCall)
TOOLS_NEED_INPUT_TRUNCATION = {
    SequentialThinkingTool.name: ["thought"],
    StrReplaceEditorTool.name: ["file_text", "old_str", "new_str"],
    BashTool.name: ["command"],
}

# Tools that need output truncation with file save (ToolFormattedResult)
TOOLS_NEED_OUTPUT_FILE_SAVE = {VisitWebpageTool.name}

__all__ = [
    "AgentToolManager",
    "TOOLS_NEED_INPUT_TRUNCATION",
    "TOOLS_NEED_OUTPUT_FILE_SAVE",
    "get_system_tools",
]
