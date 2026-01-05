"""
이메일 발송 모듈
- Gmail SMTP를 사용한 분석 결과 발송
- discord_sender.py 패턴을 따름
"""

import os
import re
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


class SimpleEmailSender:
    """Gmail SMTP 이메일 발송 클래스"""

    def __init__(
        self,
        message: str,
        recipient_email: str,
        subject: Optional[str] = None,
    ):
        # .env 파일 로드
        env_path = Path(__file__).parent.parent / ".env"
        load_dotenv(env_path)

        # SMTP 설정 로드
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.sender_password = os.getenv("SENDER_PASSWORD")

        # 설정 검증
        if not self.sender_email:
            print("Warning: SENDER_EMAIL이 .env에 설정되지 않았습니다.")
            print("이메일 발송을 건너뜁니다.")
            self.enabled = False
            return

        if not self.sender_password:
            print("Warning: SENDER_PASSWORD가 .env에 설정되지 않았습니다.")
            print("이메일 발송을 건너뜁니다.")
            self.enabled = False
            return

        self.enabled = True
        self.message = message
        self.recipient_email = recipient_email
        self.subject = subject or "JD-Scanner 분석 결과"

    def _markdown_to_html(self, markdown_text: str) -> str:
        """마크다운을 기본 HTML로 변환"""
        html = markdown_text

        # 헤더 변환
        html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
        html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
        html = re.sub(r"^# (.+)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)

        # 굵은 글씨
        html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)

        # 링크
        html = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', html)

        # 리스트 아이템
        html = re.sub(r"^- (.+)$", r"<li>\1</li>", html, flags=re.MULTILINE)

        # 줄바꿈
        html = html.replace("\n", "<br>\n")

        # HTML 템플릿
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            padding: 20px;
            max-width: 800px;
            margin: 0 auto;
            color: #333;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }}
        a {{
            color: #3498db;
        }}
        li {{
            margin: 5px 0;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            font-size: 12px;
            color: #888;
        }}
    </style>
</head>
<body>
    {html}
    <div class="footer">
        <p>JD-Scanner - AI 기반 채용공고 분석 시스템</p>
    </div>
</body>
</html>
"""

    def _create_email_content(self) -> MIMEMultipart:
        """HTML과 텍스트 버전을 포함한 이메일 생성"""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = self.subject
        msg["From"] = self.sender_email
        msg["To"] = self.recipient_email

        # 텍스트 버전
        text_part = MIMEText(self.message, "plain", "utf-8")

        # HTML 버전
        html_content = self._markdown_to_html(self.message)
        html_part = MIMEText(html_content, "html", "utf-8")

        msg.attach(text_part)
        msg.attach(html_part)

        return msg

    def send(self) -> bool:
        """이메일 발송"""
        if not self.enabled:
            return False

        try:
            # SSL 컨텍스트 생성
            context = ssl.create_default_context()

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)

                email_content = self._create_email_content()
                server.sendmail(
                    self.sender_email,
                    self.recipient_email,
                    email_content.as_string(),
                )

            print(f"이메일 발송 완료: {self.recipient_email}")
            return True

        except smtplib.SMTPAuthenticationError:
            print("이메일 인증 실패. SENDER_EMAIL과 SENDER_PASSWORD를 확인하세요.")
            print("Gmail의 경우 앱 비밀번호를 사용해야 합니다.")
            return False
        except smtplib.SMTPException as e:
            print(f"SMTP 오류: {e}")
            return False
        except Exception as e:
            print(f"이메일 발송 실패: {e}")
            return False

    def run(self) -> None:
        """discord_sender.py 패턴과의 일관성을 위한 run 메서드"""
        self.send()
