"""
LangChain 기반 채용공고 요약 시스템 - src 패키지
"""

from .chain import JobSummaryChain
from .lang_prompt import PromptConfig
from .lang_template import JobSummaryTemplate

__all__ = [
    "JobSummaryChain",
    "PromptConfig", 
    "JobSummaryTemplate"
]