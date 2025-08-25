#!/usr/bin/env python3
"""
LangChain 기반 채용공고 요약 시스템 - MVP
개선 사항:
- CLI 옵션 도입, 환경변수 기반 구성(MODEL_NAME, TEMPERATURE, DISCORD_ENABLED)
- 로깅 표준화
- 스크래핑 재시도/백오프 + 원문/정제 텍스트 캐시(output/raw)
- Discord 전송은 옵션화(--discord) 및 메시지 분할은 sender에서 처리
"""

import sys
import os
import argparse
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

from src.chain import JobSummaryChain
from src.discord_sender import SimpleDiscordSender


LOGGER = logging.getLogger("jd_scanner")


def _slugify(value: str, max_length: int = 80) -> str:
    allowed = []
    for ch in value.lower().strip():
        if ch.isalnum():
            allowed.append(ch)
        elif ch in [" ", "-", "_"]:
            allowed.append("_")
    slug = "".join(allowed)
    while "__" in slug:
        slug = slug.replace("__", "_")
    slug = slug.strip("_")
    return slug[:max_length] or "job_posting"


def _build_requests_session() -> requests.Session:
    session = requests.Session()
    retries = Retry(
        total=4,
        backoff_factor=0.8,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retries, pool_connections=10, pool_maxsize=10)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


class JobPostingSummarizer:
    def __init__(self, model_name: str = "gpt-oss:20b", temperature: float = 0.1):
        """채용공고 요약기 초기화"""
        self.chain = JobSummaryChain(model_name=model_name, temperature=temperature)
        self.session = _build_requests_session()

    def extract_content_from_url(self, url: str) -> str:
        """URL에서 채용공고 내용 추출"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }

            response = self.session.get(url, headers=headers, timeout=25)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            for script in soup(["script", "style"]):
                script.decompose()

            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            content = " ".join(chunk for chunk in chunks if chunk)

            if not content.strip():
                raise ValueError("추출된 내용이 비어있습니다.")

            # 원문/정제 텍스트 캐시 저장
            try:
                output_raw = Path("output/raw")
                output_raw.mkdir(parents=True, exist_ok=True)
                url_hash = hashlib.sha1(url.encode("utf-8")).hexdigest()[:10]
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                with open(output_raw / f"{url_hash}_{ts}.html", "wb") as f_html:
                    f_html.write(response.content)
                with open(output_raw / f"{url_hash}_{ts}.txt", "w", encoding="utf-8") as f_txt:
                    f_txt.write(content)
            except Exception as cache_err:
                LOGGER.debug(f"원문 캐시 저장 실패: {cache_err}")

            return content

        except requests.exceptions.RequestException as e:
            raise Exception(f"URL 요청 실패: {e}")
        except Exception as e:
            raise Exception(f"내용 추출 실패: {e}")

    def summarize_job_posting(self, content: str, verbose: bool = False) -> str:
        """채용공고 내용 요약 (토큰 제한 자동 처리)"""
        try:
            result = self.chain.run_summary(content, verbose=verbose)
            return result
        except Exception as e:
            raise Exception(f"요약 처리 실패: {e}")

    def save_summary(self, summary: str, filename: Optional[str] = None) -> str:
        """요약 결과를 파일로 저장"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            t_slug, c_slug = self._extract_title_company(summary)
            mid = f"{c_slug}_{t_slug}".strip("_") or "job_posting"
            filename = f"job_posting_{mid}_{timestamp}.md"

        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        file_path = output_dir / filename

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(summary)
            return str(file_path)
        except Exception as e:
            raise Exception(f"파일 저장 실패: {e}")

    def _extract_title_company(self, summary: str) -> Tuple[str, str]:
        title = ""
        company = ""
        for line in summary.splitlines():
            txt = line.strip()
            if not title and (txt.startswith("## 공고명:") or txt.startswith("## 공고명 :")):
                title = txt.split(":", 1)[-1].strip()
            if not company and (txt.startswith("### 회사명:") or txt.startswith("### 회사명 :")):
                company = txt.split(":", 1)[-1].strip()
            if title and company:
                break
        return _slugify(title), _slugify(company)


def _configure_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="JD-Scanner: 채용공고 요약기")
    parser.add_argument("--url", help="채용공고 URL")
    parser.add_argument("--model", default=os.getenv("MODEL_NAME", "gpt-oss:20b"), help="Ollama 모델명")
    parser.add_argument("--temperature", type=float, default=float(os.getenv("TEMPERATURE", "0.1")), help="LLM temperature")
    parser.add_argument("--discord", action="store_true", default=(os.getenv("DISCORD_ENABLED", "false").lower() == "true"), help="Discord 전송 활성화")
    parser.add_argument("--verbose", action="store_true", help="자세한 로그 출력")
    args = parser.parse_args()

    _configure_logging(args.verbose)

    print("🧪 LangChain 기반 채용공고 요약 시스템 - MVP")
    print("=" * 50)

    url = args.url
    if not url:
        url = input("📌 채용공고 URL을 입력하세요: ").strip()

    if not url:
        print("❌ URL이 입력되지 않았습니다.")
        sys.exit(1)

    if not (url.startswith("http://") or url.startswith("https://")):
        print("❌ 올바른 URL 형식이 아닙니다. (http:// 또는 https://로 시작해야 함)")
        sys.exit(1)

    try:
        # 요약기 초기화
        print("🔧 시스템 초기화 중...")
        summarizer = JobPostingSummarizer(model_name=args.model, temperature=args.temperature)

        # 내용 추출
        print("📄 채용공고 내용 추출 중...")
        content = summarizer.extract_content_from_url(url)
        print(f"✅ 내용 추출 완료 (길이: {len(content)} 글자)")

        # 요약 수행
        print("🤖 AI 요약 처리 중... (시간이 조금 걸릴 수 있습니다)")
        summary = summarizer.summarize_job_posting(content, verbose=args.verbose)
        summary = f"{summary}  \n[채용공고]({url})"

        # Discord 전송 (옵션)
        if args.discord:
            sender = SimpleDiscordSender(summary)
            sender.run()
        else:
            LOGGER.info("Discord 전송 비활성화 상태입니다. --discord 플래그 또는 DISCORD_ENABLED=true 설정 시 전송합니다.")

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
