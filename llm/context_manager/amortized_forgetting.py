import logging
from ii_agent.llm.base import GeneralContentBlock
from ii_agent.llm.context_manager.base import ContextManager
from ii_agent.llm.token_counter import TokenCounter


class AmortizedForgettingContextManager(ContextManager):
    """A context manager that maintains a condensed history and forgets old events when it grows too large."""

    def __init__(
        self,
        token_counter: TokenCounter,
        logger: logging.Logger,
        token_budget: int = 120_000,
        max_size: int = 100,
        keep_first: int = 1,
    ):
        """Initialize the context manager.

        Args:
            token_counter: Token counter instance
            logger: Logger instance
            token_budget: Token budget for context
            max_size: Maximum size of history before forgetting.
            keep_first: Number of initial events to always keep.

        Raises:
            ValueError: If keep_first is greater than max_size, keep_first is negative, or max_size is non-positive.
        """
        if keep_first >= max_size // 2:
            raise ValueError(
                f"keep_first ({keep_first}) must be less than half of max_size ({max_size})"
            )
        if keep_first < 0:
            raise ValueError(f"keep_first ({keep_first}) cannot be negative")
        if max_size < 1:
            raise ValueError(f"max_size ({max_size}) cannot be non-positive")

        super().__init__(token_counter, logger, token_budget)
        self.max_size = max_size
        self.keep_first = keep_first

    def should_truncate(self, message_lists: list[list[GeneralContentBlock]]) -> bool:
        """Check if condensation is needed based on the number of message lists."""
        return (len(message_lists) > self.max_size) or super().should_truncate(
            message_lists
        )

    def apply_truncation(
        self, message_lists: list[list[GeneralContentBlock]]
    ) -> list[list[GeneralContentBlock]]:
        """Apply truncation by keeping head and tail events, forgetting middle events."""

        target_size = min(self.max_size, len(message_lists)) // 2
        head = message_lists[: self.keep_first]

        events_from_tail = target_size - len(head)
        if events_from_tail <= 0:
            # If head is too large, just return head
            self.logger.warning(
                f"Head size ({len(head)}) exceeds target size ({target_size}), returning head only"
            )
            return head

        tail = (
            message_lists[-events_from_tail:]
            if events_from_tail < len(message_lists)
            else message_lists
        )

        # Calculate what we're forgetting
        forgotten_start_idx = self.keep_first
        forgotten_end_idx = len(message_lists) - events_from_tail
        forgotten_count = max(0, forgotten_end_idx - forgotten_start_idx)

        self.logger.info(
            f"Amortized forgetting: keeping {len(head)} head + {len(tail)} tail events, "
            f"forgetting {forgotten_count} middle events (indices {forgotten_start_idx}-{forgotten_end_idx - 1})"
        )

        # Combine head and tail
        condensed_messages = head + tail

        return condensed_messages
