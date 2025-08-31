#!/usr/bin/env python3
"""
LangChain 기반 채용공고 요약 시스템
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

from src.langchain.chain import JobSummaryChain
from src.discord.discord_sender import SimpleDiscordSender
from src.parser.parser_bot import WebParser

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


class JobPostingSummarizer:
    def __init__(
        self, content: str, model_name: str = "gpt-oss:20b", temperature: float = 0.1
    ):
        """채용공고 요약기 초기화"""
        self.chain = JobSummaryChain(model_name=model_name, temperature=temperature)
        self.content = content

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
            if not title and (
                txt.startswith("## 공고명:") or txt.startswith("## 공고명 :")
            ):
                title = txt.split(":", 1)[-1].strip()
            if not company and (
                txt.startswith("### 회사명:") or txt.startswith("### 회사명 :")
            ):
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
    parser.add_argument(
        "--model", default=os.getenv("MODEL_NAME", "gpt-oss:20b"), help="Ollama 모델명"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=float(os.getenv("TEMPERATURE", "0.1")),
        help="LLM temperature",
    )
    parser.add_argument(
        "--discord",
        action="store_true",
        default=(os.getenv("DISCORD_ENABLED", "false").lower() == "true"),
        help="Discord 전송 활성화",
    )
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
        webparser = WebParser(url=url)

        # 내용 추출
        print("📄 채용공고 내용 추출 중...")
        content = webparser.extract_content_from_url()
        print(f"✅ 내용 추출 완료 (길이: {len(content)} 글자)")

        # 요약 수행
        print("🤖 AI 요약 처리 중... (시간이 조금 걸릴 수 있습니다)")
        summarizer = JobPostingSummarizer(
            content=content, model_name=args.model, temperature=args.temperature
        )
        summary = summarizer.summarize_job_posting(content, verbose=args.verbose)
        summary = f"{summary}  \n[채용공고]({url})"

        # Discord 전송 (옵션)
        if args.discord:
            sender = SimpleDiscordSender(summary)
            sender.run()
        else:
            LOGGER.info(
                "Discord 전송 비활성화 상태입니다. --discord 플래그 또는 DISCORD_ENABLED=true 설정 시 전송합니다."
            )

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
