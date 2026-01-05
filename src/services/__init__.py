"""
Services 레이어 - 외부 서비스 연동
GitHub API, Email SMTP, Discord 봇 등 외부 시스템과의 통신
"""

from .github_analyzer import GitHubAnalyzer, GitHubProfile, Repository
from .email_sender import SimpleEmailSender
from .discord_sender import SimpleDiscordSender

__all__ = [
    "GitHubAnalyzer",
    "GitHubProfile",
    "Repository",
    "SimpleEmailSender",
    "SimpleDiscordSender",
]
