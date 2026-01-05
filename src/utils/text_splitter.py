"""
텍스트 분할 모듈 - 대용량 콘텐츠 처리를 위한 청킹 기능
"""

import re
from typing import List, Optional


class SmartTextSplitter:
    """토큰 제한을 고려한 스마트 텍스트 분할기"""
    
    def __init__(
        self,
        chunk_size: int = 3000,
        chunk_overlap: int = 200,
        separators: Optional[List[str]] = None
    ):
        """
        텍스트 분할기 초기화
        
        Args:
            chunk_size: 청크 최대 크기 (문자 기준)
            chunk_overlap: 청크 간 겹치는 부분 크기
            separators: 분할 우선순위별 구분자 리스트
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # 기본 구분자 (우선순위 순)
        self.separators = separators or [
            "\n\n",  # 문단 구분
            "\n",    # 줄바꿈
            ". ",    # 문장 끝
            "! ",    # 느낌표
            "? ",    # 물음표
            "; ",    # 세미콜론
            ", ",    # 쉼표
            " ",     # 공백
            ""       # 문자 단위
        ]
    
    def split_text(self, text: str) -> List[str]:
        """
        텍스트를 청크로 분할
        
        Args:
            text: 분할할 텍스트
            
        Returns:
            분할된 텍스트 청크 리스트
        """
        if len(text) <= self.chunk_size:
            return [text]
        
        # 기본 전처리
        text = self._preprocess_text(text)
        
        chunks = []
        current_chunk = ""
        
        # 우선순위별 구분자로 분할 시도
        segments = self._split_by_separators(text)
        
        for segment in segments:
            # 현재 청크에 추가 가능한지 확인
            if len(current_chunk) + len(segment) <= self.chunk_size:
                current_chunk += segment
            else:
                # 현재 청크가 비어있지 않으면 저장
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                
                # 세그먼트가 청크 크기보다 큰 경우 강제 분할
                if len(segment) > self.chunk_size:
                    force_split_chunks = self._force_split(segment)
                    chunks.extend(force_split_chunks[:-1])
                    current_chunk = force_split_chunks[-1] if force_split_chunks else ""
                else:
                    current_chunk = segment
        
        # 마지막 청크 추가
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # 오버랩 적용
        return self._apply_overlap(chunks)
    
    def _preprocess_text(self, text: str) -> str:
        """텍스트 전처리"""
        # 연속된 공백 제거
        text = re.sub(r'\s+', ' ', text)
        # 연속된 줄바꿈 정리
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()
    
    def _split_by_separators(self, text: str) -> List[str]:
        """구분자 우선순위에 따라 텍스트 분할"""
        for separator in self.separators:
            if separator in text:
                if separator == "":
                    # 문자 단위 분할
                    return list(text)
                else:
                    parts = text.split(separator)
                    # 구분자도 포함하여 재구성
                    result = []
                    for i, part in enumerate(parts):
                        if i < len(parts) - 1:
                            result.append(part + separator)
                        else:
                            result.append(part)
                    return [p for p in result if p.strip()]
        
        return [text]
    
    def _force_split(self, text: str) -> List[str]:
        """강제로 텍스트를 청크 크기에 맞춰 분할"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # 단어 경계에서 자르기 시도
            chunk = text[start:end]
            last_space = chunk.rfind(' ')
            
            if last_space > 0:
                end = start + last_space
                chunks.append(text[start:end])
                start = end + 1
            else:
                chunks.append(chunk)
                start = end
                
        return chunks
    
    def _apply_overlap(self, chunks: List[str]) -> List[str]:
        """청크 간 오버랩 적용"""
        if len(chunks) <= 1 or self.chunk_overlap <= 0:
            return chunks
        
        overlapped_chunks = [chunks[0]]
        
        for i in range(1, len(chunks)):
            prev_chunk = chunks[i-1]
            current_chunk = chunks[i]
            
            # 이전 청크의 끝부분을 현재 청크 앞에 추가
            if len(prev_chunk) > self.chunk_overlap:
                overlap_text = prev_chunk[-self.chunk_overlap:]
                # 단어 경계에서 자르기
                space_idx = overlap_text.find(' ')
                if space_idx > 0:
                    overlap_text = overlap_text[space_idx+1:]
                
                current_chunk = overlap_text + " " + current_chunk
            
            overlapped_chunks.append(current_chunk)
        
        return overlapped_chunks
    
    def get_chunk_info(self, text: str) -> dict:
        """분할 정보 반환"""
        chunks = self.split_text(text)
        return {
            "total_length": len(text),
            "num_chunks": len(chunks),
            "avg_chunk_size": sum(len(chunk) for chunk in chunks) // len(chunks) if chunks else 0,
            "chunk_sizes": [len(chunk) for chunk in chunks]
        }


class JobPostingSplitter(SmartTextSplitter):
    """채용공고 특화 텍스트 분할기"""
    
    def __init__(self, chunk_size: int = 3000, chunk_overlap: int = 200):
        # 채용공고 특화 구분자
        job_separators = [
            "\n## ",     # 섹션 헤더
            "\n### ",    # 서브 섹션
            "\n**",      # 강조 텍스트
            "\n- ",      # 목록 항목
            "\n\n",      # 문단
            ". ",        # 문장
            "\n",        # 줄바꿈
            " ",         # 공백
            ""           # 문자
        ]
        super().__init__(chunk_size, chunk_overlap, job_separators)
    
    def split_job_posting(self, content: str) -> List[str]:
        """
        채용공고 콘텐츠를 의미 단위로 분할
        
        Args:
            content: 채용공고 원문
            
        Returns:
            의미 단위로 분할된 청크 리스트
        """
        # 채용공고 특화 전처리
        content = self._preprocess_job_content(content)
        
        return self.split_text(content)
    
    def _preprocess_job_content(self, content: str) -> str:
        """채용공고 전용 전처리"""
        # HTML 태그 잔여물 제거
        content = re.sub(r'<[^>]+>', '', content)
        
        # 특수 문자 정리
        content = re.sub(r'[^\w\s가-힣.,!?()[\]{}:;-]', ' ', content)
        
        # 연속된 공백/줄바꿈 정리
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        return content.strip()