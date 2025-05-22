#!/usr/bin/env python3
"""
LangChain 기반 채용공고 요약 시스템 - MVP
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup

from src.chain import JobSummaryChain


class JobPostingSummarizer:
    def __init__(self, model_name: str = "llama3.2"):
        """채용공고 요약기 초기화"""
        self.chain = JobSummaryChain(model_name)
    
    def extract_content_from_url(self, url: str) -> str:
        """URL에서 채용공고 내용 추출"""
        try:
            # User-Agent 헤더 추가 (일부 사이트에서 봇 차단 방지)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # HTTP 에러 발생 시 예외 발생
            
            # BeautifulSoup으로 HTML 파싱
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # script, style 태그 제거
            for script in soup(["script", "style"]):
                script.decompose()
            
            # 텍스트 추출 및 정리
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            content = ' '.join(chunk for chunk in chunks if chunk)
            
            if not content.strip():
                raise ValueError("추출된 내용이 비어있습니다.")
            
            return content
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"URL 요청 실패: {e}")
        except Exception as e:
            raise Exception(f"내용 추출 실패: {e}")
    
    def summarize_job_posting(self, content: str) -> str:
        """채용공고 내용 요약"""
        try:
            # 내용이 너무 길면 앞부분만 사용 (토큰 제한 고려)
            if len(content) > 8000:
                content = content[:8000] + "..."
            
            result = self.chain.run_summary(content)
            return result
        except Exception as e:
            raise Exception(f"요약 처리 실패: {e}")
    
    def save_summary(self, summary: str, filename: Optional[str] = None) -> str:
        """요약 결과를 파일로 저장"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"job_posting_{timestamp}.md"
        
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        file_path = output_dir / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(summary)
            return str(file_path)
        except Exception as e:
            raise Exception(f"파일 저장 실패: {e}")


def main():
    """메인 함수"""
    print("🧪 LangChain 기반 채용공고 요약 시스템 - MVP")
    print("=" * 50)
    
    # URL 입력받기
    url = input("📌 채용공고 URL을 입력하세요: ").strip()
    
    if not url:
        print("❌ URL이 입력되지 않았습니다.")
        sys.exit(1)
    
    # URL 형식 간단 검증
    if not (url.startswith('http://') or url.startswith('https://')):
        print("❌ 올바른 URL 형식이 아닙니다. (http:// 또는 https://로 시작해야 함)")
        sys.exit(1)
    
    try:
        # 요약기 초기화
        print("🔧 시스템 초기화 중...")
        summarizer = JobPostingSummarizer()
        
        # 내용 추출
        print("📄 채용공고 내용 추출 중...")
        content = summarizer.extract_content_from_url(url)
        print(f"✅ 내용 추출 완료 (길이: {len(content)} 글자)")
        
        # 요약 수행
        print("🤖 AI 요약 처리 중... (시간이 조금 걸릴 수 있습니다)")
        summary = summarizer.summarize_job_posting(content)
        
        # 결과 출력
        print("\n" + "=" * 50)
        print("📋 요약 결과:")
        print("=" * 50)
        print(summary)
        
        # 파일 저장
        print("\n💾 결과 저장 중...")
        saved_path = summarizer.save_summary(summary)
        print(f"✅ 저장 완료: {saved_path}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()