import discord
import asyncio
import os
import sys
from dotenv import load_dotenv
from pathlib import Path

class SimpleDiscordSender:
    def __init__(self, message):
        # .env 로드
        env_path = Path(__file__).parent.parent / '.env'
        load_dotenv(env_path)

        self.token = os.getenv("DISCORD_BOT_TOKEN")
        self.channel_ids_str = os.getenv("DISCORD_CHANNEL_IDS")

        if not self.token:
            print("❌ DISCORD_BOT_TOKEN이 설정되지 않았습니다. \n .env를 확인하고 토큰 값을 입력하세요.")
            sys.exit(1)

        if not self.channel_ids_str:
            print("❌ DISCORD_CHANNEL_IDS가 설정되지 않았습니다. \n .env를 확인하고 채널 IDS를 입력해주세요.")
            sys.exit(1)

        self.channel_ids = self.parse_channel_ids()

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
        raw_ids = self.channel_ids_str.split(",") # type: ignore
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
            print("❌ 유효한 채널 ID가 없습니다.")
            sys.exit(1)

        return channel_ids

    async def send_message(self, content: str):
        """여러 채널에 메시지 전송"""
        for channel_id in self.channel_ids:
            try:
                channel = await self.client.fetch_channel(channel_id)
                await channel.send(content) # type: ignore
                print(f"📨 메시지 전송 완료: 채널 {channel_id}")
            except Exception as e:
                print(f"❌ 채널 {channel_id} 전송 실패: {e}")

    def run(self):
        self.client.run(self.token) # type: ignore


def main():
    sender = SimpleDiscordSender("매개변수 메시지 체크")
    sender.run()

if __name__ == "__main__":
    main()
