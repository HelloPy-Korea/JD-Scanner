"""
토큰 카운터 및 콘텐츠 검증 모듈
"""

import re
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class TokenStats:
    """토큰 통계 정보"""
    char_count: int
    estimated_tokens: int
    word_count: int
    is_over_limit: bool
    recommended_action: str


class SimpleTokenCounter:
    """간단한 토큰 카운터 (외부 라이브러리 없이)"""
    
    def __init__(self, chars_per_token: float = 3.5, max_tokens: int = 4096):
        """
        토큰 카운터 초기화
        
        Args:
            chars_per_token: 토큰당 평균 문자 수 (한국어+영어 혼합 기준)
            max_tokens: 최대 토큰 제한
        """
        self.chars_per_token = chars_per_token
        self.max_tokens = max_tokens
    
    def count_tokens(self, text: str) -> int:
        """
        텍스트의 추정 토큰 수 계산
        
        Args:
            text: 계산할 텍스트
            
        Returns:
            추정 토큰 수
        """
        if not text:
            return 0
        
        # 기본 문자 수 기반 계산
        char_count = len(text)
        basic_estimate = char_count / self.chars_per_token
        
        # 단어 수 기반 보정
        word_count = len(text.split())
        word_estimate = word_count * 1.3  # 단어당 평균 1.3 토큰
        
        # 한국어/영어 비율 고려 보정
        korean_ratio = self._get_korean_ratio(text)
        
        # 한국어가 많으면 토큰 수 증가 (한국어는 토큰 효율이 낮음)
        ratio_multiplier = 1.0 + (korean_ratio * 0.5)
        
        # 두 추정값의 평균에 비율 보정 적용
        estimated_tokens = int(((basic_estimate + word_estimate) / 2) * ratio_multiplier)
        
        return estimated_tokens
    
    def _get_korean_ratio(self, text: str) -> float:
        """텍스트에서 한국어 비율 계산"""
        if not text:
            return 0.0
        
        korean_chars = len(re.findall(r'[가-힣]', text))
        total_chars = len(re.findall(r'[가-힣a-zA-Z]', text))
        
        if total_chars == 0:
            return 0.0
        
        return korean_chars / total_chars
    
    def get_token_stats(self, text: str) -> TokenStats:
        """텍스트의 상세 토큰 통계 반환"""
        char_count = len(text)
        estimated_tokens = self.count_tokens(text)
        word_count = len(text.split())
        is_over_limit = estimated_tokens > self.max_tokens
        
        # 권장 액션 결정
        if not is_over_limit:
            recommended_action = "직접 처리 가능"
        elif estimated_tokens < self.max_tokens * 2:
            recommended_action = "간단한 청킹 필요"
        elif estimated_tokens < self.max_tokens * 5:
            recommended_action = "Map-Reduce 처리 권장"
        else:
            recommended_action = "고급 청킹 + Map-Reduce 필수"
        
        return TokenStats(
            char_count=char_count,
            estimated_tokens=estimated_tokens,
            word_count=word_count,
            is_over_limit=is_over_limit,
            recommended_action=recommended_action
        )
    
    def validate_content_size(self, content: str, strict: bool = False) -> Dict[str, Any]:
        """
        콘텐츠 크기 검증
        
        Args:
            content: 검증할 콘텐츠
            strict: 엄격한 검증 모드
            
        Returns:
            검증 결과 딕셔너리
        """
        stats = self.get_token_stats(content)
        
        # 엄격 모드에서는 더 낮은 임계값 사용
        limit = self.max_tokens * 0.8 if strict else self.max_tokens
        
        result = {
            "is_valid": stats.estimated_tokens <= limit,
            "stats": stats,
            "limit_used": limit,
            "usage_percentage": (stats.estimated_tokens / limit) * 100,
            "needs_processing": stats.estimated_tokens > limit
        }
        
        return result


class ContentPreprocessor:
    """콘텐츠 전처리 및 최적화"""
    
    @staticmethod
    def clean_web_content(content: str) -> str:
        """웹 콘텐츠 정리"""
        # HTML 태그 제거
        content = re.sub(r'<[^>]+>', '', content)
        
        # 연속된 공백/줄바꿈 정리
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        # 특수 문자 정리 (채용공고에 불필요한 것들)
        content = re.sub(r'[^\w\s가-힣.,!?()[\]{}:;/-]', ' ', content)
        
        # 반복되는 패턴 제거 (광고, 푸터 등)
        content = ContentPreprocessor._remove_repetitive_patterns(content)
        
        return content.strip()
    
    @staticmethod
    def _remove_repetitive_patterns(content: str) -> str:
        """반복되는 패턴 제거"""
        lines = content.split('\n')
        
        # 3번 이상 반복되는 라인 제거
        seen_lines = {}
        filtered_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line in seen_lines:
                seen_lines[line] += 1
                if seen_lines[line] <= 2:  # 최대 2번까지만 허용
                    filtered_lines.append(line)
            else:
                seen_lines[line] = 1
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    @staticmethod
    def extract_key_sections(content: str) -> str:
        """핵심 섹션만 추출"""
        # 채용공고에서 중요한 키워드들
        important_keywords = [
            # 한국어
            '채용', '모집', '지원', '자격', '요건', '우대', '업무', '담당',
            '복지', '혜택', '급여', '연봉', '마감', '접수', '회사', '소개',
            '비전', '미션', '사업', '서비스', '기술', '개발', '경력', '신입',
            # 영어
            'requirements', 'qualifications', 'responsibilities', 'benefits',
            'salary', 'experience', 'skills', 'company', 'about', 'mission',
            'vision', 'role', 'position', 'job', 'career', 'apply', 'deadline'
        ]
        
        lines = content.split('\n')
        important_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 중요 키워드가 포함된 라인 우선 선택
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in important_keywords):
                important_lines.append(line)
            elif len(line) > 20:  # 너무 짧은 라인 제외
                important_lines.append(line)
        
        return '\n'.join(important_lines)
    
    @staticmethod
    def optimize_for_processing(content: str, target_size: int = 8000) -> str:
        """
        처리 최적화를 위한 콘텐츠 크기 조정
        
        Args:
            content: 원본 콘텐츠
            target_size: 목표 크기 (문자 수)
            
        Returns:
            최적화된 콘텐츠
        """
        if len(content) <= target_size:
            return content
        
        # 1단계: 기본 정리
        content = ContentPreprocessor.clean_web_content(content)
        
        if len(content) <= target_size:
            return content
        
        # 2단계: 핵심 섹션만 추출
        content = ContentPreprocessor.extract_key_sections(content)
        
        if len(content) <= target_size:
            return content
        
        # 3단계: 강제 자르기 (단어 경계에서)
        if len(content) > target_size:
            content = content[:target_size]
            last_space = content.rfind(' ')
            if last_space > target_size * 0.9:  # 90% 이상 위치의 공백
                content = content[:last_space]
            content += "..."
        
        return content