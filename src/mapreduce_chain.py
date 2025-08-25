"""
Map-Reduce 패턴 기반 대용량 텍스트 처리 체인
"""

from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import time

from langchain_ollama.llms import OllamaLLM

from .text_splitter import JobPostingSplitter
from .lang_template import JobSummaryTemplate


class MapReduceJobChain:
    """Map-Reduce 패턴으로 대용량 채용공고 처리하는 체인"""
    
    def __init__(
        self,
        model_name: str = "gpt-oss:20b",
        temperature: float = 0.1,
        chunk_size: int = 3000,
        chunk_overlap: int = 200,
        max_workers: int = 3
    ):
        """
        Map-Reduce 체인 초기화
        
        Args:
            model_name: Ollama 모델명
            temperature: LLM 온도 설정
            chunk_size: 청크 최대 크기
            chunk_overlap: 청크 간 겹치는 부분
            max_workers: 병렬 처리 최대 워커 수
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_workers = max_workers
        
        # LLM 초기화
        self.llm = self._initialize_llm()
        
        # 텍스트 분할기 초기화
        self.text_splitter = JobPostingSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        # 프롬프트 템플릿 초기화
        self.map_template = JobSummaryTemplate.get_map_template()
        self.reduce_template = JobSummaryTemplate.get_reduce_template()
        
        # 체인 생성
        self.map_chain = self.map_template | self.llm
        self.reduce_chain = self.reduce_template | self.llm
    
    def _initialize_llm(self) -> OllamaLLM:
        """Ollama LLM 초기화"""
        try:
            return OllamaLLM(
                model=self.model_name,
                temperature=self.temperature,
                num_predict=2048,  # 출력 토큰 제한
                num_ctx=4096,      # 컨텍스트 토큰 제한
                timeout=120        # 타임아웃 설정
            )
        except Exception as e:
            raise Exception(f"Ollama LLM 초기화 실패: {e}")
    
    def process_large_content(self, content: str, verbose: bool = False) -> str:
        """
        대용량 콘텐츠를 Map-Reduce 방식으로 처리
        
        Args:
            content: 처리할 콘텐츠
            verbose: 진행 상황 출력 여부
            
        Returns:
            최종 요약 결과
        """
        if verbose:
            print(f"원본 콘텐츠 크기: {len(content):,} 문자")
        
        # 1. 텍스트 분할 (Map 단계 준비)
        chunks = self.text_splitter.split_job_posting(content)
        
        if verbose:
            print(f"분할된 청크 수: {len(chunks)}")
            print(f"평균 청크 크기: {sum(len(c) for c in chunks) // len(chunks):,} 문자")
        
        # 단일 청크인 경우 직접 처리
        if len(chunks) == 1:
            if verbose:
                print("단일 청크 - 직접 처리")
            return self._process_single_chunk(chunks[0])
        
        # 2. Map 단계 - 각 청크 요약
        if verbose:
            print("Map 단계 시작...")
        
        map_results = self._execute_map_phase(chunks, verbose)
        
        if verbose:
            print(f"Map 단계 완료 - {len(map_results)}개 요약 생성")
        
        # 3. Reduce 단계 - 요약들을 통합
        if verbose:
            print("Reduce 단계 시작...")
        
        final_result = self._execute_reduce_phase(map_results, verbose)
        
        if verbose:
            print("Map-Reduce 처리 완료")
        
        return final_result
    
    def _process_single_chunk(self, chunk: str) -> str:
        """단일 청크 처리"""
        try:
            # 단일 청크는 reduce 템플릿 사용
            return self.reduce_chain.invoke({"text": chunk})
        except Exception as e:
            raise Exception(f"단일 청크 처리 실패: {e}")
    
    def _execute_map_phase(self, chunks: List[str], verbose: bool = False) -> List[str]:
        """Map 단계 실행 - 각 청크를 병렬로 요약"""
        results = []
        
        # 병렬 처리로 Map 단계 실행
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            
            for i, chunk in enumerate(chunks):
                future = executor.submit(self._process_map_chunk, chunk, i, verbose)
                futures.append(future)
            
            # 결과 수집
            for i, future in enumerate(futures):
                try:
                    result = future.result(timeout=180)  # 3분 타임아웃
                    results.append(result)
                    if verbose:
                        print(f"청크 {i+1}/{len(chunks)} 처리 완료")
                except Exception as e:
                    error_msg = f"청크 {i+1} 처리 실패: {e}"
                    if verbose:
                        print(error_msg)
                    results.append(f"[처리 실패: {error_msg}]")
        
        return results
    
    def _process_map_chunk(self, chunk: str, chunk_idx: int, verbose: bool = False) -> str:
        """개별 청크 처리 (Map 단계)"""
        try:
            start_time = time.time()
            result = self.map_chain.invoke({"text": chunk})
            
            if verbose:
                elapsed = time.time() - start_time
                print(f"청크 {chunk_idx+1} 처리 시간: {elapsed:.2f}초")
            
            return result
        except Exception as e:
            raise Exception(f"청크 {chunk_idx+1} Map 처리 실패: {e}")
    
    def _execute_reduce_phase(self, map_results: List[str], verbose: bool = False) -> str:
        """Reduce 단계 실행 - 요약들을 최종 통합"""
        try:
            start_time = time.time()
            
            # 모든 Map 결과를 하나의 텍스트로 결합
            combined_text = "\n\n".join([
                f"=== 요약 {i+1} ===\n{result}" 
                for i, result in enumerate(map_results)
            ])
            
            # 결합된 텍스트가 너무 긴 경우 재귀적으로 처리
            if len(combined_text) > 8000:  # 임계값
                if verbose:
                    print("Reduce 단계 텍스트가 너무 김 - 재귀 처리")
                
                # Map 결과들을 다시 청크로 나누어 처리
                return self._recursive_reduce(map_results, verbose)
            
            # 최종 통합 요약
            final_result = self.reduce_chain.invoke({"text": combined_text})
            
            if verbose:
                elapsed = time.time() - start_time
                print(f"Reduce 단계 처리 시간: {elapsed:.2f}초")
            
            return final_result
            
        except Exception as e:
            raise Exception(f"Reduce 단계 실패: {e}")
    
    def _recursive_reduce(self, summaries: List[str], verbose: bool = False) -> str:
        """재귀적 Reduce - 요약이 너무 많은 경우"""
        if len(summaries) <= 2:
            combined = "\n\n".join(summaries)
            return self.reduce_chain.invoke({"text": combined})
        
        # 요약들을 그룹으로 나누어 처리
        group_size = 3
        intermediate_results = []
        
        for i in range(0, len(summaries), group_size):
            group = summaries[i:i+group_size]
            combined = "\n\n".join(group)
            
            try:
                result = self.reduce_chain.invoke({"text": combined})
                intermediate_results.append(result)
                
                if verbose:
                    print(f"중간 그룹 {i//group_size + 1} 처리 완료")
                    
            except Exception as e:
                if verbose:
                    print(f"중간 그룹 {i//group_size + 1} 처리 실패: {e}")
                intermediate_results.append(f"[그룹 처리 실패: {e}]")
        
        # 재귀적으로 중간 결과들을 다시 결합
        return self._recursive_reduce(intermediate_results, verbose)
    
    def get_processing_stats(self, content: str) -> Dict[str, Any]:
        """처리 예상 통계 정보 반환"""
        chunks = self.text_splitter.split_job_posting(content)
        
        return {
            "content_length": len(content),
            "estimated_chunks": len(chunks),
            "avg_chunk_size": sum(len(c) for c in chunks) // len(chunks) if chunks else 0,
            "estimated_processing_time": len(chunks) * 10,  # 청크당 10초 예상
            "recommended_max_workers": min(len(chunks), self.max_workers),
            "chunk_sizes": [len(c) for c in chunks]
        }
    
    def update_settings(
        self,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        max_workers: Optional[int] = None,
        temperature: Optional[float] = None
    ):
        """설정 업데이트"""
        if chunk_size is not None or chunk_overlap is not None:
            self.text_splitter = JobPostingSplitter(
                chunk_size=chunk_size or self.text_splitter.chunk_size,
                chunk_overlap=chunk_overlap or self.text_splitter.chunk_overlap
            )
        
        if max_workers is not None:
            self.max_workers = max_workers
        
        if temperature is not None:
            self.temperature = temperature
            self.llm = self._initialize_llm()
            self.map_chain = self.map_template | self.llm
            self.reduce_chain = self.reduce_template | self.llm
