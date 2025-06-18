# 간단한 Discord 메시지 전송 (연결 문제 해결)
import discord
import os
import asyncio
from dotenv import load_dotenv
from pathlib import Path

# 상위 폴더의 .env 파일 로드
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# 환경변수에서 값 가져오기
DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_IDS'))

async def send_message(message_text):
    """단순히 메시지 하나만 보내는 함수"""
    
    # Intents 설정
    intents = discord.Intents.default()
    intents.message_content = True
    
    # Client 생성
    client = discord.Client(intents=intents)
    
    try:
        @client.event
        async def on_ready():
            print(f'✅ {client.user} 로그인 완료!')
            
            # 채널 찾기
            channel = client.get_channel(CHANNEL_ID)
            if channel:
                # 메시지 보내기
                await channel.send(message_text)
                print(f'📤 메시지 전송 완료: {message_text}')
            else:
                print(f'❌ 채널을 찾을 수 없습니다. (ID: {CHANNEL_ID})')
            
            # 봇 종료
            await client.close()
        
        # 봇 시작
        await client.start(DISCORD_TOKEN)
        
    except Exception as e:
        print(f'❌ 오류 발생: {e}')
    finally:
        # 확실히 연결 종료
        if not client.is_closed():
            await client.close()

# 실행 함수
def send_discord_message(text):
    """메시지를 보내는 메인 함수"""
    try:
        # 환경변수 확인
        if not DISCORD_TOKEN:
            print("❌ DISCORD_TOKEN이 .env 파일에 없습니다!")
            return
        
        if not CHANNEL_ID:
            print("❌ CHANNEL_ID가 .env 파일에 없습니다!")
            return
        
        # 비동기 함수 실행
        asyncio.run(send_message(text))
        
    except Exception as e:
        print(f"❌ 실행 오류: {e}")

# 사용 예시
if __name__ == "__main__":
    # 여기서 보낼 메시지 변경
    message = "안녕하세요! 테스트 메시지입니다. 🤖"
    
    print("🚀 Discord 메시지 전송 시작...")
    send_discord_message(message)
    print("✨ 완료!")


# ============ 더 간단한 버전 (함수형) ============

def quick_send(message):
    """빠르게 메시지 보내기"""
    import asyncio
    
    async def _send():
        client = discord.Client(intents=discord.Intents.default())
        
        @client.event
        async def on_ready():
            channel = client.get_channel(CHANNEL_ID)
            await channel.send(message)
            await client.close()
        
        try:
            await client.start(DISCORD_TOKEN)
        except:
            pass
        finally:
            if not client.is_closed():
                await client.close()
    
    asyncio.run(_send())

# 사용법: quick_send("빠른 메시지!")


# ============ 여러 메시지 연속 전송 버전 ============

async def send_multiple_messages(messages):
    """여러 메시지를 연속으로 보내기"""
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)
    
    @client.event
    async def on_ready():
        print(f'✅ {client.user} 로그인 완료!')
        channel = client.get_channel(CHANNEL_ID)
        
        if channel:
            for i, msg in enumerate(messages, 1):
                await channel.send(msg)
                print(f'📤 메시지 {i}/{len(messages)} 전송: {msg}')
                await asyncio.sleep(1)  # 1초 간격
        
        await client.close()
    
    try:
        await client.start(DISCORD_TOKEN)
    except:
        pass
    finally:
        if not client.is_closed():
            await client.close()

# 사용법:
# messages = ["첫 번째 메시지", "두 번째 메시지", "세 번째 메시지"]
# asyncio.run(send_multiple_messages(messages))