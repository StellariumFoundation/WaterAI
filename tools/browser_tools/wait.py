import asyncio

from typing import Any, Optional
from browser.browser import Browser
from tools.base import ToolImplOutput
from .base import BrowserTool
from . import utils
from llm.message_history import MessageHistory


class BrowserWaitTool(BrowserTool):
    name = "browser_wait"
    description = "Wait for the page to load"
    input_schema = {"type": "object", "properties": {}, "required": []}

    def __init__(self, browser: Browser):
        super().__init__(browser)

    async def _run(
        self,
        tool_input: dict[str, Any],
        message_history: Optional[MessageHistory] = None,
    ) -> ToolImplOutput:
        await asyncio.sleep(1)
        state = await self.browser.update_state()
        state = await self.browser.handle_pdf_url_navigation()

        msg = "Waited for page"

        return utils.format_screenshot_tool_output(state.screenshot, msg)
