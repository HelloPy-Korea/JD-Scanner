"""
환경변수 중앙 관리 모듈
- .env 파일 로드/저장
- 설정 검증
"""

import re
from pathlib import Path
from typing import Any, Optional


class ConfigManager:
    """환경변수 설정 관리 클래스"""

    ENV_PATH = Path(".env")

    # 환경변수 스키마 정의
    SCHEMA = {
        "DISCORD_BOT_TOKEN": {"required": False, "type": "password", "default": ""},
        "DISCORD_CHANNEL_IDS": {"required": False, "type": "text", "default": ""},
        "SMTP_SERVER": {"required": False, "type": "text", "default": "smtp.gmail.com"},
        "SMTP_PORT": {"required": False, "type": "text", "default": "587"},
        "SENDER_EMAIL": {"required": False, "type": "email", "default": ""},
        "SENDER_PASSWORD": {"required": False, "type": "password", "default": ""},
        "GITHUB_TOKEN": {"required": False, "type": "password", "default": ""},
        "GITHUB_PROFILE_URL": {"required": False, "type": "url", "default": ""},
    }

    def __init__(self):
        self.config = self.load_config()

    def load_config(self) -> dict[str, str]:
        """
        .env 파일에서 설정 로드
        파일이 없으면 기본값 사용
        """
        config = {key: schema.get("default", "") for key, schema in self.SCHEMA.items()}

        if not self.ENV_PATH.exists():
            return config

        try:
            with open(self.ENV_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()
                        if key in self.SCHEMA:
                            config[key] = value
        except Exception as e:
            print(f"Warning: .env 파일 로드 실패: {e}")

        return config

    def save_config(self, config: dict[str, str]) -> bool:
        """
        설정을 .env 파일에 저장
        기존 주석은 보존
        """
        try:
            lines = []
            existing_keys = set()

            # 기존 파일 읽기 (주석 보존)
            if self.ENV_PATH.exists():
                with open(self.ENV_PATH, "r", encoding="utf-8") as f:
                    for line in f:
                        stripped = line.strip()
                        if stripped.startswith("#") or not stripped:
                            lines.append(line.rstrip("\n"))
                        elif "=" in stripped:
                            key = stripped.split("=", 1)[0].strip()
                            if key in config:
                                lines.append(f"{key}={config[key]}")
                                existing_keys.add(key)
                            else:
                                lines.append(line.rstrip("\n"))

            # 새 키 추가
            for key, value in config.items():
                if key not in existing_keys:
                    lines.append(f"{key}={value}")

            # 파일 저장
            with open(self.ENV_PATH, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")

            self.config = config
            return True

        except Exception as e:
            print(f"Error: .env 파일 저장 실패: {e}")
            return False

    def get(self, key: str, default: Optional[str] = None) -> str:
        """설정 값 가져오기"""
        return self.config.get(key, default or self.SCHEMA.get(key, {}).get("default", ""))

    def set(self, key: str, value: str) -> None:
        """설정 값 설정"""
        self.config[key] = value

    def is_configured(self) -> bool:
        """
        최소한의 설정이 완료되었는지 확인
        최소 하나의 알림 방법(Discord 또는 Email)이 설정되어 있으면 True
        """
        # Discord 설정 확인
        discord_configured = bool(
            self.config.get("DISCORD_BOT_TOKEN") and self.config.get("DISCORD_CHANNEL_IDS")
        )

        # Email 설정 확인
        email_configured = bool(
            self.config.get("SENDER_EMAIL") and self.config.get("SENDER_PASSWORD")
        )

        return discord_configured or email_configured

    def validate_config(self, config: dict[str, str]) -> list[str]:
        """
        설정 유효성 검사
        Returns: 오류 메시지 목록 (빈 리스트면 유효)
        """
        errors = []

        for key, value in config.items():
            if key not in self.SCHEMA:
                continue

            schema = self.SCHEMA[key]
            field_type = schema.get("type", "text")

            # 빈 값은 검증 스킵 (선택 필드)
            if not value:
                continue

            # 이메일 형식 검증
            if field_type == "email":
                email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                if not re.match(email_pattern, value):
                    errors.append(f"{key}: 올바른 이메일 형식이 아닙니다.")

            # URL 형식 검증 (GitHub 프로필)
            if field_type == "url" and value:
                github_pattern = r"^https?://github\.com/[a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38}/?$"
                if not re.match(github_pattern, value):
                    errors.append(f"{key}: 올바른 GitHub 프로필 URL 형식이 아닙니다.")

        return errors

    def get_all(self) -> dict[str, str]:
        """모든 설정 값 반환"""
        return self.config.copy()
