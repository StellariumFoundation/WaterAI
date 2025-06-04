import logging
from ii_agent.llm.base import GeneralContentBlock
from ii_agent.llm.context_manager.base import ContextManager
from ii_agent.llm.token_counter import TokenCounter


class PipelineContextManager(ContextManager):
    """Combines multiple context managers into a single context manager.

    This is useful for creating a pipeline of context managers that can be chained together
    to achieve very specific condensation aims. Each context manager is run in sequence,
    passing the output of one to the next, until we reach the end.
    """

    def __init__(
        self,
        token_counter: TokenCounter,
        logger: logging.Logger,
        token_budget: int = 120_000,
        context_managers: list[ContextManager] = [],
    ):
        """Initialize the pipeline context manager.

        Args:
            token_counter: Token counter instance
            logger: Logger instance
            token_budget: Token budget for context
            *context_managers: Variable number of context managers to chain
        """
        super().__init__(token_counter, logger, token_budget)
        self.context_managers = list(context_managers)

        if not self.context_managers:
            raise ValueError(
                "At least one context manager must be provided to the pipeline"
            )

    def apply_truncation(
        self, message_lists: list[list[GeneralContentBlock]]
    ) -> list[list[GeneralContentBlock]]:
        """Apply truncation by running each context manager in sequence."""
        result = message_lists

        for i, context_manager in enumerate(self.context_managers):
            self.logger.debug(
                f"Running context manager {i + 1}/{len(self.context_managers)}: {type(context_manager).__name__}"
            )

            # Apply the context manager's truncation logic
            prev_count = len(result)
            result = context_manager.apply_truncation_if_needed(result)
            new_count = len(result)

            if new_count != prev_count:
                self.logger.info(
                    f"Context manager {type(context_manager).__name__} reduced message count from {prev_count} to {new_count}"
                )

            # If we've reduced to an acceptable size, we can stop early
            current_tokens = self.count_tokens(result)
            if current_tokens <= self._token_budget:
                self.logger.debug(
                    f"Token budget satisfied after context manager {i + 1}, stopping pipeline early"
                )
                break

        final_tokens = self.count_tokens(result)
        original_tokens = self.count_tokens(message_lists)

        self.logger.info(
            f"Pipeline completed: {len(message_lists)} -> {len(result)} messages, "
            f"{original_tokens} -> {final_tokens} tokens"
        )

        return result
