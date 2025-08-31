"""
LangChain 체인 관리 모듈
"""

from typing import Optional, Dict, Any

from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import PromptTemplate

from .lang_prompt import PromptConfig
from .mapreduce_chain import MapReduceJobChain
from .token_counter import SimpleTokenCounter, ContentPreprocessor


class JobSummaryChain:
    """채용공고 요약을 위한 LangChain 관리 클래스"""

    def __init__(self, model_name: str, temperature: float, max_tokens: int = 2048):
        """
        체인 초기화

        Args:
            model_name: 사용할 Ollama 모델명
            temperature: LLM 온도 설정 (0.0 ~ 1.0)
            max_tokens: 최대 토큰 제한 (기본 2048)
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

        # LLM 초기화
        self.llm = self._initialize_llm()

        # 프롬프트 설정 관리자
        self.prompt_config = PromptConfig()

        # 기본 체인 생성
        self.summary_chain = self._create_summary_chain()

        # 토큰 카운터 초기화
        self.token_counter = SimpleTokenCounter(max_tokens=max_tokens)

        # Map-Reduce 체인 초기화 (지연 로딩)
        self._mapreduce_chain = None

    def _initialize_llm(self) -> OllamaLLM:
        """Ollama LLM 초기화"""
        try:
            llm = OllamaLLM(model=self.model_name, temperature=self.temperature)
            return llm
        except Exception as e:
            raise Exception(f"Ollama LLM 초기화 실패: {e}")

    def _create_summary_chain(self):
        """채용공고 요약용 체인 생성"""
        prompt = self.prompt_config.get_job_summary_prompt()
        return prompt | self.llm

    def create_custom_chain(self, custom_prompt: PromptTemplate):
        """커스텀 프롬프트로 새로운 체인 생성"""
        return custom_prompt | self.llm

    def run_summary(self, job_content: str, verbose: bool = False) -> str:
        """
        채용공고 요약 실행 (토큰 제한 자동 처리)

        Args:
            job_content: 채용공고 원문 내용
            verbose: 처리 과정 출력 여부

        Returns:
            요약된 채용공고 내용
        """
        try:
            # 1. 콘텐츠 전처리
            cleaned_content = ContentPreprocessor.clean_web_content(job_content)

            # 2. 토큰 수 검증
            validation_result = self.token_counter.validate_content_size(
                cleaned_content
            )

            if verbose:
                stats = validation_result["stats"]
                print(f"콘텐츠 분석:")
                print(f"- 문자 수: {stats.char_count:,}")
                print(f"- 추정 토큰: {stats.estimated_tokens:,}")
                print(f"- 권장 처리: {stats.recommended_action}")

            # 3. 처리 방법 결정
            if not validation_result["needs_processing"]:
                # 직접 처리 가능
                if verbose:
                    print("직접 처리 실행")
                return self.summary_chain.invoke({"input": cleaned_content})
            else:
                # Map-Reduce 처리 필요
                if verbose:
                    print("Map-Reduce 처리 실행")
                return self._run_mapreduce_summary(cleaned_content, verbose)

        except Exception as e:
            raise Exception(f"체인 실행 실패: {e}")

    def _run_mapreduce_summary(self, content: str, verbose: bool = False) -> str:
        """Map-Reduce 방식으로 대용량 콘텐츠 처리"""
        if self._mapreduce_chain is None:
            self._mapreduce_chain = MapReduceJobChain(
                model_name=self.model_name, temperature=self.temperature
            )

        return self._mapreduce_chain.process_large_content(content, verbose)

    def get_content_analysis(self, content: str) -> Dict[str, Any]:
        """콘텐츠 분석 정보 반환"""
        cleaned_content = ContentPreprocessor.clean_web_content(content)
        validation_result = self.token_counter.validate_content_size(cleaned_content)

        # Map-Reduce 체인이 필요한 경우 처리 통계 추가
        if validation_result["needs_processing"]:
            if self._mapreduce_chain is None:
                self._mapreduce_chain = MapReduceJobChain(
                    model_name=self.model_name, temperature=self.temperature
                )

            mapreduce_stats = self._mapreduce_chain.get_processing_stats(
                cleaned_content
            )
            validation_result["mapreduce_stats"] = mapreduce_stats

        return validation_result

    def run_custom_chain(self, chain, inputs: Dict[str, Any]) -> str:
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

            result = chain.invoke(inputs)
            return result
        except Exception as e:
            raise Exception(f"커스텀 체인 실행 실패: {e}")

    def update_temperature(self, new_temperature: float) -> None:
        """LLM 온도 설정 업데이트"""
        if not 0.0 <= new_temperature <= 1.0:
            raise ValueError("온도는 0.0과 1.0 사이의 값이어야 합니다.")

        self.temperature = new_temperature
        self.llm = self._initialize_llm()
        self.summary_chain = self._create_summary_chain()
