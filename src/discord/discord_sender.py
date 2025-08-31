import discord
import asyncio
import os
import sys
import logging
from dotenv import load_dotenv
from pathlib import Path


class SimpleDiscordSender:
    def __init__(self, message):
        self.enabled = True
        # .env 로드
        env_path = Path(__file__).parent.parent / ".env"
        load_dotenv(env_path)

        self.token = os.getenv("DISCORD_BOT_TOKEN")
        self.channel_ids_str = os.getenv("DISCORD_CHANNEL_IDS")

        if not self.token:
            print(
                "⚠️  DISCORD_BOT_TOKEN이 설정되지 않았습니다. 전송을 건너뜁니다."
            )
            self.enabled = False

        if not self.channel_ids_str:
            print(
                "⚠️  DISCORD_CHANNEL_IDS가 설정되지 않았습니다. 전송을 건너뜁니다."
            )
            self.enabled = False

        self.channel_ids = self.parse_channel_ids()
        if not self.channel_ids:
            self.enabled = False

        # Discord client 설정
        intents = discord.Intents.default()
        self.client = discord.Client(intents=intents)

        # 이벤트 핸들러 등록
        @self.client.event
        async def on_ready():
            print(f"✅ 봇 로그인 성공: {self.client.user}")
            await self.send_message(message)
            await self.client.close()

    def parse_channel_ids(self):
        """환경변수에서 채널 ID 문자열을 리스트로 파싱"""
        # env에 여러 채널 id를 입력시 ","로 구분
        raw_ids = self.channel_ids_str.split(",")  # type: ignore
        channel_ids = []

        for raw_id in raw_ids:
            raw_id = raw_id.strip()
            if not raw_id:
                continue
            try:
                channel_ids.append(int(raw_id))  # int 변환 전 None 체크 필요
            except ValueError:
                print(f"⚠️  '{raw_id}'는 숫자가 아닙니다. 건너뜁니다.")

        if not channel_ids:
            print("⚠️  유효한 채널 ID가 없습니다. 전송을 건너뜁니다.")

        return channel_ids

    async def send_message(self, content: str):
        """여러 채널에 메시지 전송"""
        parts = self.split_message(content)
        total = len(parts)
        for channel_id in self.channel_ids:
            try:
                channel = await self.client.fetch_channel(channel_id)
                for idx, part in enumerate(parts, start=1):
                    suffix = f"\n({idx}/{total})" if total > 1 else ""
                    await channel.send(part + suffix)  # type: ignore
                print(f"📨 메시지 전송 완료: 채널 {channel_id}")
            except Exception as e:
                print(f"❌ 채널 {channel_id} 전송 실패: {e}")

    def run(self):
        if not self.enabled:
            print("ℹ️  Discord 설정이 유효하지 않아 전송을 생략합니다.")
            return
        self.client.run(self.token)  # type: ignore

    @staticmethod
    def split_message(content: str, limit: int = 1900):
        """Discord 2000자 제한을 고려하여 메시지 분할"""
        if len(content) <= limit:
            return [content]

        # 단락 단위 우선 분할
        paragraphs = content.split("\n\n")
        parts = []
        buffer = ""
        for para in paragraphs:
            candidate = para if not buffer else buffer + "\n\n" + para
            if len(candidate) <= limit:
                buffer = candidate
            else:
                if buffer:
                    parts.append(buffer)
                # 단락이 자체로도 너무 길면 줄 단위로 분할
                if len(para) > limit:
                    lines = para.split("\n")
                    buf2 = ""
                    for line in lines:
                        cand2 = line if not buf2 else buf2 + "\n" + line
                        if len(cand2) <= limit:
                            buf2 = cand2
                        else:
                            if buf2:
                                parts.append(buf2)
                            # 여전히 긴 라인은 강제 자르기
                            while len(line) > limit:
                                parts.append(line[:limit])
                                line = line[limit:]
                            buf2 = line
                    if buf2:
                        parts.append(buf2)
                    buffer = ""
                else:
                    buffer = para
        if buffer:
            parts.append(buffer)
        return parts
