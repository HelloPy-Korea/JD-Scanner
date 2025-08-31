from typing import Optional, Tuple

from src.langchain.chain import JobSummaryChain


class JobPostingSummarizer:
    def __init__(self, model_name: str = "gpt-oss:20b", temperature: float = 0.1):
        """요약기 초기화"""
        self.chain = JobSummaryChain(model_name=model_name, temperature=temperature)
