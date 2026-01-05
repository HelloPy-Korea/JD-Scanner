"""
GitHub 프로필 분석 모듈
- 공개 레포지토리 분석
- 기술 스택 추출
"""

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import requests
from dotenv import load_dotenv


@dataclass
class Repository:
    """레포지토리 데이터 클래스"""

    name: str
    description: Optional[str]
    language: Optional[str]
    languages_breakdown: Dict[str, float] = field(default_factory=dict)
    stars: int = 0
    topics: List[str] = field(default_factory=list)
    url: str = ""


@dataclass
class GitHubProfile:
    """GitHub 프로필 데이터 클래스"""

    username: str
    profile_url: str
    bio: Optional[str] = None
    public_repos_count: int = 0
    repositories: List[Repository] = field(default_factory=list)
    technologies: Dict[str, List[str]] = field(default_factory=dict)

    def get_all_languages(self) -> List[str]:
        """모든 고유 프로그래밍 언어 반환"""
        languages: Set[str] = set()
        for repo in self.repositories:
            if repo.language:
                languages.add(repo.language)
            languages.update(repo.languages_breakdown.keys())
        return sorted(list(languages))

    def to_summary_dict(self) -> Dict[str, Any]:
        """LLM 입력용 요약 딕셔너리 변환"""
        return {
            "username": self.username,
            "bio": self.bio,
            "total_repos": self.public_repos_count,
            "languages": self.get_all_languages(),
            "technologies": self.technologies,
            "top_repos": [
                {
                    "name": r.name,
                    "description": r.description,
                    "language": r.language,
                    "stars": r.stars,
                    "topics": r.topics,
                    "languages_used": list(r.languages_breakdown.keys()),
                }
                for r in sorted(
                    self.repositories, key=lambda x: x.stars, reverse=True
                )[:10]
            ],
        }


class GitHubAnalyzer:
    """GitHub 프로필 분석 클래스 - 공개 레포지토리만 분석"""

    BASE_URL = "https://api.github.com"

    # 기술 패턴 정의
    TECH_PATTERNS = {
        "frameworks": [
            "react",
            "angular",
            "vue",
            "django",
            "flask",
            "spring",
            "rails",
            "express",
            "fastapi",
            "nextjs",
            "nuxt",
            "svelte",
            "laravel",
            "flutter",
            "swiftui",
            "pytorch",
            "tensorflow",
            "nest",
            "gatsby",
            "remix",
        ],
        "tools": [
            "docker",
            "kubernetes",
            "terraform",
            "ansible",
            "jenkins",
            "github-actions",
            "gitlab-ci",
            "aws",
            "gcp",
            "azure",
            "nginx",
            "graphql",
            "rest",
            "webpack",
            "vite",
            "eslint",
            "prettier",
        ],
        "databases": [
            "postgresql",
            "mysql",
            "mongodb",
            "sqlite",
            "redis",
            "dynamodb",
            "firebase",
            "supabase",
            "prisma",
            "elasticsearch",
        ],
    }

    def __init__(self):
        # .env에서 선택적 GitHub 토큰 로드
        env_path = Path(__file__).parent.parent / ".env"
        load_dotenv(env_path)

        self.token = os.getenv("GITHUB_TOKEN")
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "JD-Scanner/1.0",
        }

        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
            print("GitHub 토큰이 설정되었습니다. (높은 API 제한)")

    @staticmethod
    def extract_username(github_url: str) -> Optional[str]:
        """GitHub URL에서 사용자명 추출"""
        pattern = r"github\.com/([a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38})"
        match = re.search(pattern, github_url)
        return match.group(1) if match else None

    def _make_request(self, endpoint: str) -> Optional[Dict]:
        """GitHub API 요청"""
        try:
            response = requests.get(
                f"{self.BASE_URL}{endpoint}",
                headers=self.headers,
                timeout=10,
            )

            if response.status_code == 404:
                return None

            if response.status_code == 403:
                print("GitHub API 제한에 도달했습니다.")
                print("GITHUB_TOKEN을 .env에 설정하면 더 많은 요청이 가능합니다.")
                return None

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"GitHub API 요청 실패: {e}")
            return None

    def fetch_user_profile(self, username: str) -> Optional[Dict]:
        """기본 사용자 프로필 가져오기"""
        return self._make_request(f"/users/{username}")

    def fetch_user_repos(self, username: str, max_repos: int = 30) -> List[Dict]:
        """사용자의 공개 레포지토리 가져오기"""
        repos = []
        page = 1
        per_page = min(max_repos, 100)

        while len(repos) < max_repos:
            data = self._make_request(
                f"/users/{username}/repos?sort=updated&per_page={per_page}&page={page}"
            )

            if not data:
                break

            repos.extend(data)

            if len(data) < per_page:
                break

            page += 1

        return repos[:max_repos]

    def fetch_repo_languages(self, username: str, repo_name: str) -> Dict[str, int]:
        """레포지토리 언어 구성 가져오기"""
        data = self._make_request(f"/repos/{username}/{repo_name}/languages")
        return data if data else {}

    def analyze_profile(self, github_url: str) -> Optional[GitHubProfile]:
        """GitHub 프로필 전체 분석"""
        username = self.extract_username(github_url)
        if not username:
            print(f"URL에서 사용자명을 추출할 수 없습니다: {github_url}")
            return None

        print(f"GitHub 프로필 분석 중: {username}")

        # 사용자 프로필 가져오기
        user_data = self.fetch_user_profile(username)
        if not user_data:
            print(f"프로필을 가져올 수 없습니다: {username}")
            return None

        profile = GitHubProfile(
            username=username,
            profile_url=github_url,
            bio=user_data.get("bio"),
            public_repos_count=user_data.get("public_repos", 0),
        )

        # 레포지토리 가져오기
        print("레포지토리 분석 중...")
        repos_data = self.fetch_user_repos(username)

        for repo_data in repos_data:
            # 포크된 레포는 제외
            if repo_data.get("fork"):
                continue

            repo = Repository(
                name=repo_data.get("name", ""),
                description=repo_data.get("description"),
                language=repo_data.get("language"),
                stars=repo_data.get("stargazers_count", 0),
                topics=repo_data.get("topics", []),
                url=repo_data.get("html_url", ""),
            )

            # 상위 레포에 대해 상세 언어 분석
            if repo.stars > 0 or len(profile.repositories) < 10:
                languages = self.fetch_repo_languages(username, repo.name)
                if languages:
                    total = sum(languages.values())
                    repo.languages_breakdown = {
                        lang: round((bytes_count / total) * 100, 1)
                        for lang, bytes_count in languages.items()
                    }

            profile.repositories.append(repo)

        # 기술 추출
        profile.technologies = self.extract_technologies(profile)

        print(f"분석 완료: {len(profile.repositories)}개 레포지토리")
        return profile

    def extract_technologies(self, profile: GitHubProfile) -> Dict[str, List[str]]:
        """프로필에서 기술 스택 추출 및 분류"""
        result: Dict[str, List[str]] = {
            "languages": profile.get_all_languages(),
            "frameworks": [],
            "tools": [],
            "databases": [],
        }

        # 토픽, 설명에서 검색
        search_text = ""
        for repo in profile.repositories:
            search_text += " ".join(repo.topics).lower() + " "
            if repo.description:
                search_text += repo.description.lower() + " "

        # 패턴 매칭
        for category, patterns in self.TECH_PATTERNS.items():
            for pattern in patterns:
                if pattern in search_text:
                    result[category].append(pattern)

        # 중복 제거 및 정렬
        for category in result:
            result[category] = sorted(list(set(result[category])))

        return result
