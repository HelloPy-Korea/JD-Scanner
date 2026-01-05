"""
사용자 프로필 관리 모듈
- 이메일/GitHub URL 수집
- 로컬 JSON 파일 저장
"""

import json
import uuid
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List


class UserProfile:
    """사용자 프로필 데이터 클래스"""

    def __init__(
        self,
        email: str,
        github_url: Optional[str] = None,
        user_id: Optional[str] = None,
    ):
        self.id = user_id or str(uuid.uuid4())
        self.email = email
        self.github_url = github_url
        self.created_at = datetime.now().isoformat()
        self.last_active = datetime.now().isoformat()
        self.analysis_count = 0

    def to_dict(self) -> Dict:
        """JSON 직렬화용 딕셔너리 변환"""
        return {
            "id": self.id,
            "email": self.email,
            "github_url": self.github_url,
            "created_at": self.created_at,
            "last_active": self.last_active,
            "analysis_count": self.analysis_count,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "UserProfile":
        """딕셔너리에서 UserProfile 생성"""
        profile = cls(
            email=data["email"],
            github_url=data.get("github_url"),
            user_id=data["id"],
        )
        profile.created_at = data["created_at"]
        profile.last_active = data["last_active"]
        profile.analysis_count = data.get("analysis_count", 0)
        return profile


class UserManager:
    """사용자 데이터 관리 클래스"""

    USERS_DIR = Path("output/users")
    USERS_FILE = USERS_DIR / "users.json"

    def __init__(self):
        self._ensure_users_directory()
        self.users = self._load_users()

    def _ensure_users_directory(self) -> None:
        """users 디렉토리 생성"""
        self.USERS_DIR.mkdir(parents=True, exist_ok=True)

    def _load_users(self) -> List[UserProfile]:
        """JSON 파일에서 사용자 로드"""
        if not self.USERS_FILE.exists():
            return []

        try:
            with open(self.USERS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [UserProfile.from_dict(u) for u in data.get("users", [])]
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: 사용자 파일 로드 실패: {e}")
            return []

    def _save_users(self) -> None:
        """사용자 데이터를 JSON 파일에 저장"""
        data = {"users": [u.to_dict() for u in self.users]}
        with open(self.USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def validate_email(email: str) -> bool:
        """이메일 형식 검증"""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_github_url(url: str) -> bool:
        """GitHub 프로필 URL 형식 검증"""
        pattern = r"^https?://github\.com/[a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38}/?$"
        return bool(re.match(pattern, url))

    def find_user_by_email(self, email: str) -> Optional[UserProfile]:
        """이메일로 기존 사용자 찾기"""
        for user in self.users:
            if user.email.lower() == email.lower():
                return user
        return None

    def register_or_update_user(
        self,
        email: str,
        github_url: Optional[str] = None,
    ) -> UserProfile:
        """신규 사용자 등록 또는 기존 사용자 업데이트"""
        existing = self.find_user_by_email(email)

        if existing:
            existing.last_active = datetime.now().isoformat()
            if github_url:
                existing.github_url = github_url
            self._save_users()
            return existing

        new_user = UserProfile(email=email, github_url=github_url)
        self.users.append(new_user)
        self._save_users()
        return new_user

    def increment_analysis_count(self, user: UserProfile) -> None:
        """사용자 분석 횟수 증가"""
        user.analysis_count += 1
        user.last_active = datetime.now().isoformat()
        self._save_users()

    def collect_user_info(self) -> UserProfile:
        """CLI를 통한 사용자 정보 수집"""
        print("\n" + "=" * 50)
        print("  사용자 정보 입력")
        print("=" * 50)

        # 이메일 수집 및 검증
        while True:
            email = input("\n이메일 주소를 입력하세요: ").strip()
            if not email:
                print("이메일은 필수 입력 항목입니다.")
                continue
            if not self.validate_email(email):
                print("올바른 이메일 형식이 아닙니다. 다시 입력해주세요.")
                continue
            break

        # GitHub URL 수집 (선택)
        github_url = None
        collect_github = input("\nGitHub 프로필을 추가하시겠습니까? (y/n): ").strip().lower()
        if collect_github == "y":
            while True:
                github_url = input("GitHub 프로필 URL을 입력하세요: ").strip()
                if not github_url:
                    print("GitHub 분석을 건너뜁니다.")
                    break
                if not self.validate_github_url(github_url):
                    print("올바른 GitHub URL 형식이 아닙니다.")
                    print("예시: https://github.com/username")
                    continue
                break

        return self.register_or_update_user(email, github_url)
