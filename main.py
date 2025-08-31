#!/usr/bin/env python3
"""
LangChain 기반 채용공고 요약 시스템
"""

import sys
import os
import argparse
import logging

from src.discord.discord_sender import SimpleDiscordSender
from src.parser.parser_bot import WebParser
from src.summarizer.posting_summarizer import JobPostingSummarizer

LOGGER = logging.getLogger("jd_scanner")





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
    args = parser.parse_args()

    print("🧪 LangChain 기반 채용공고 요약 시스템 - MVP")
    print("=" * 50)

    url = args.url
    if not url:
        url = input("📌 채용공고 URL을 입력하세요: ").strip()

    if not url:
        print("❌ URL이 입력되지 않았습니다.")
        sys.exit(1)

    if not url.startswith("http"):
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
        summary = summarizer.summarize_job_posting(content)
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
        print("\n⚠️  사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
