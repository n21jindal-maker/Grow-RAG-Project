import time
import logging
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import config
from generation.prompts import SYSTEM_PROMPT, FEW_SHOT_EXAMPLES

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, rpm: int, tpm: int, rpd: int = 1000, tpd: int = 200000):
        self.rpm = rpm
        self.tpm = tpm
        self.rpd = rpd
        self.tpd = tpd
        self.requests = []
        self.tokens = []
        
    def _cleanup(self, now: float):
        cutoff_day = now - 86400.0
        self.requests = [t for t in self.requests if t > cutoff_day]
        self.tokens = [(t, count) for t, count in self.tokens if t > cutoff_day]

    def _current_tokens_minute(self, now: float) -> int:
        cutoff_minute = now - 60.0
        return sum(count for t, count in self.tokens if t > cutoff_minute)

    def _current_tokens_day(self) -> int:
        return sum(count for _, count in self.tokens)

    def _current_requests_minute(self, now: float) -> int:
        cutoff_minute = now - 60.0
        return sum(1 for t in self.requests if t > cutoff_minute)

    def _current_requests_day(self) -> int:
        return len(self.requests)

    def wait_if_needed(self, estimated_tokens: int = 1000):
        now = time.time()
        self._cleanup(now)
        
        while (self._current_requests_minute(now) >= self.rpm or 
               self._current_requests_day() >= self.rpd or
               (self._current_tokens_minute(now) + estimated_tokens) > self.tpm or
               (self._current_tokens_day() + estimated_tokens) > self.tpd):
            logger.info("Rate limit approached. Waiting 1s...")
            time.sleep(1.0)
            now = time.time()
            self._cleanup(now)
            
        self.requests.append(now)
        self.tokens.append((now, estimated_tokens))


class LLMGenerator:
    def __init__(self):
        self.llm = ChatGroq(
            model=config.PRIMARY_MODEL,
            temperature=config.TEMPERATURE,
            max_tokens=config.MAX_OUTPUT_TOKENS
        )
        self.rate_limiter = RateLimiter(config.RPM_LIMIT, config.TPM_LIMIT, config.RPD_LIMIT, config.TPD_LIMIT)

    def generate_response(self, query: str, assembled_context: str) -> str:
        if not assembled_context.strip():
            return "I don't have this information in my current sources. Please check the official HDFC MF website."
            
        # Prepare messages
        messages = [SystemMessage(content=SYSTEM_PROMPT)]
        
        # Add few-shot examples
        for ex in FEW_SHOT_EXAMPLES:
            messages.append(HumanMessage(content=f"Context:\n{ex['context']}\n\nQuery: {ex['query']}"))
            messages.append(AIMessage(content=ex['response']))
            
        # Add actual query
        human_prompt = f"Context:\n{assembled_context}\n\nQuery: {query}"
        messages.append(HumanMessage(content=human_prompt))
        
        # Estimate tokens (rough estimate: 4 chars per token for all text)
        total_text = "".join([m.content for m in messages])
        estimated_tokens = len(total_text) // 4 + config.MAX_OUTPUT_TOKENS
        
        self.rate_limiter.wait_if_needed(estimated_tokens)
        
        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error: {e}"
