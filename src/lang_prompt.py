"""
LangChain 프롬프트 설정 모듈
"""

from typing import Dict, Any
from langchain_core.prompts import PromptTemplate

from .lang_template import JobSummaryTemplate


class PromptConfig:
    """프롬프트 설정 관리 클래스"""
    
    def __init__(self):
        self.template_manager = JobSummaryTemplate()
    
    def get_job_summary_prompt(self) -> PromptTemplate:
        """기본 채용공고 요약 프롬프트 반환"""
        return self.template_manager.get_summary_template()
    
    def get_custom_prompt(self, format_string: str) -> PromptTemplate:
        """커스텀 포맷 프롬프트 반환"""
        return self.template_manager.get_custom_template(format_string)
    
    def format_prompt(self, prompt: PromptTemplate, **kwargs) -> str:
        """프롬프트에 변수를 대입하여 최종 문자열 반환"""
        return prompt.format(**kwargs)
    
    def validate_prompt_inputs(self, prompt: PromptTemplate, inputs: Dict[str, Any]) -> bool:
        """프롬프트 입력값 유효성 검사"""
        required_vars = prompt.input_variables
        provided_vars = set(inputs.keys())
        missing_vars = set(required_vars) - provided_vars
        
        if missing_vars:
            raise ValueError(f"필수 변수가 누락되었습니다: {missing_vars}")
        
        return True