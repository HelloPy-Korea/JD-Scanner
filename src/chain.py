"""
LangChain 체인 관리 모듈
"""

from typing import Optional, Dict, Any

from langchain_ollama.llms import OllamaLLM
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate

from .lang_prompt import PromptConfig


class JobSummaryChain:
    """채용공고 요약을 위한 LangChain 관리 클래스"""
    
    def __init__(self, model_name: str = "llama3.2", temperature: float = 0.1):
        """
        체인 초기화
        
        Args:
            model_name: 사용할 Ollama 모델명
            temperature: LLM 온도 설정 (0.0 ~ 1.0)
        """
        self.model_name = model_name
        self.temperature = temperature
        
        # LLM 초기화
        self.llm = self._initialize_llm()
        
        # 프롬프트 설정 관리자
        self.prompt_config = PromptConfig()
        
        # 기본 체인 생성
        self.summary_chain = self._create_summary_chain()
    
    def _initialize_llm(self) -> OllamaLLM:
        """Ollama LLM 초기화"""
        try:
            llm = OllamaLLM(
                model=self.model_name,
                temperature=self.temperature
            )
            return llm
        except Exception as e:
            raise Exception(f"Ollama LLM 초기화 실패: {e}")
    
    def _create_summary_chain(self) -> LLMChain:
        """채용공고 요약용 체인 생성"""
        prompt = self.prompt_config.get_job_summary_prompt()
        return LLMChain(llm=self.llm, prompt=prompt)
    
    def create_custom_chain(self, custom_prompt: PromptTemplate) -> LLMChain:
        """커스텀 프롬프트로 새로운 체인 생성"""
        return LLMChain(llm=self.llm, prompt=custom_prompt)
    
    def run_summary(self, job_content: str) -> str:
        """
        채용공고 요약 실행
        
        Args:
            job_content: 채용공고 원문 내용
            
        Returns:
            요약된 채용공고 내용
        """
        try:
            result = self.summary_chain.run(job_content=job_content)
            return result
        except Exception as e:
            raise Exception(f"체인 실행 실패: {e}")
    
    def run_custom_chain(self, chain: LLMChain, inputs: Dict[str, Any]) -> str:
        """
        커스텀 체인 실행
        
        Args:
            chain: 실행할 LLMChain
            inputs: 체인 입력값 딕셔너리
            
        Returns:
            체인 실행 결과
        """
        try:
            # 입력값 유효성 검사
            self.prompt_config.validate_prompt_inputs(chain.prompt, inputs)
            
            result = chain.run(**inputs)
            return result
        except Exception as e:
            raise Exception(f"커스텀 체인 실행 실패: {e}")
    
    def get_chain_info(self) -> Dict[str, Any]:
        """현재 체인 정보 반환"""
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "prompt_template": self.summary_chain.prompt.template,
            "input_variables": self.summary_chain.prompt.input_variables
        }
    
    def update_temperature(self, new_temperature: float) -> None:
        """LLM 온도 설정 업데이트"""
        if not 0.0 <= new_temperature <= 1.0:
            raise ValueError("온도는 0.0과 1.0 사이의 값이어야 합니다.")
        
        self.temperature = new_temperature
        self.llm = self._initialize_llm()
        self.summary_chain = self._create_summary_chain()