from langchain_core.callbacks import BaseCallbackHandler
from datetime import datetime
from logger import logger
import time


# Groq's Llama 3.3 70B pricing (approximate, per 1M tokens)
COST_PER_1M_INPUT_TOKENS = 0.59   # USD
COST_PER_1M_OUTPUT_TOKENS = 0.79  # USD


class JobLensCallbackHandler(BaseCallbackHandler):
 

    def __init__(self):
        self.start_time = None
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.chain_name = "unknown"

    def on_chain_start(self, serialized, inputs, **kwargs):
        """Fires when any chain starts."""
        self.start_time = time.time()
        self.chain_name = serialized.get("name", "unknown")
        logger.info(f"Chain started: {self.chain_name}")

    def on_chain_end(self, outputs, **kwargs):
        """Fires when a chain completes successfully."""
        if self.start_time:
            latency = round(time.time() - self.start_time, 3)
            cost = self._estimate_cost()
            logger.info(
                f"Chain completed: {self.chain_name} | "
                f"Latency: {latency}s | "
                f"Tokens: {self.prompt_tokens}in/{self.completion_tokens}out | "
                f"Est. cost: ${cost:.6f}"
            )

    def on_chain_error(self, error, **kwargs):
        """Fires when a chain throws an error."""
        logger.error(f"Chain error in {self.chain_name}: {error}")

    def on_llm_start(self, serialized, prompts, **kwargs):
        """Fires just before the LLM receives the prompt."""
        # Rough token estimate: ~4 chars per token
        for prompt in prompts:
            self.prompt_tokens += len(prompt) // 4
        logger.info(f"LLM call started | Est. prompt tokens: {self.prompt_tokens}")

    def on_llm_end(self, response, **kwargs):
        """Fires when the LLM returns its response."""
        # Extract actual token usage if available
        if hasattr(response, "llm_output") and response.llm_output:
            usage = response.llm_output.get("token_usage", {})
            self.prompt_tokens = usage.get("prompt_tokens", self.prompt_tokens)
            self.completion_tokens = usage.get("completion_tokens", 0)
        else:
            # Fallback estimate
            for gen in response.generations:
                for g in gen:
                    self.completion_tokens += len(g.text) // 4

    def on_llm_error(self, error, **kwargs):
        """Fires when the LLM throws an error."""
        logger.error(f"LLM error: {error}")

    def _estimate_cost(self) -> float:
        """Estimates cost in USD based on token counts."""
        input_cost = (self.prompt_tokens / 1_000_000) * COST_PER_1M_INPUT_TOKENS
        output_cost = (self.completion_tokens / 1_000_000) * COST_PER_1M_OUTPUT_TOKENS
        return input_cost + output_cost

    def get_summary(self) -> dict:
        """Returns a summary of this chain's execution."""
        return {
            "chain_name": self.chain_name,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "estimated_cost_usd": self._estimate_cost(),
            "latency_seconds": round(time.time() - self.start_time, 3) if self.start_time else 0
        }