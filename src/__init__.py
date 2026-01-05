"""
JD-Scanner - AI 기반 채용공고 분석 시스템 패키지

레이어 구조:
- ui/       : 사용자 인터페이스 (Presentation)
- core/     : 핵심 비즈니스 로직 (Domain)
- services/ : 외부 서비스 연동 (Infrastructure)
- utils/    : 공통 유틸리티 (Shared)
"""

# Core 레이어
from .core.chain import JobSummaryChain, SkillGapChain
from .core.mapreduce_chain import MapReduceJobChain
from .core.lang_prompt import PromptConfig
from .core.lang_template import JobSummaryTemplate, SkillGapTemplate

# Services 레이어
from .services.discord_sender import SimpleDiscordSender
from .services.email_sender import SimpleEmailSender
from .services.github_analyzer import GitHubAnalyzer, GitHubProfile, Repository

# Utils 레이어
from .utils.config_manager import ConfigManager
from .utils.user_manager import UserManager, UserProfile
from .utils.token_counter import SimpleTokenCounter, ContentPreprocessor
from .utils.text_splitter import SmartTextSplitter, JobPostingSplitter

# UI 레이어 (tkinter 의존성으로 인해 선택적 import)
try:
    from .ui.main_ui import MainWindow
    from .ui.settings_ui import SettingsWindow
    _UI_AVAILABLE = True
except ImportError:
    MainWindow = None  # type: ignore
    SettingsWindow = None  # type: ignore
    _UI_AVAILABLE = False

__all__ = [
    # Core
    "JobSummaryChain",
    "SkillGapChain",
    "MapReduceJobChain",
    "PromptConfig",
    "JobSummaryTemplate",
    "SkillGapTemplate",
    # Services
    "SimpleDiscordSender",
    "SimpleEmailSender",
    "GitHubAnalyzer",
    "GitHubProfile",
    "Repository",
    # Utils
    "ConfigManager",
    "UserManager",
    "UserProfile",
    "SimpleTokenCounter",
    "ContentPreprocessor",
    "SmartTextSplitter",
    "JobPostingSplitter",
    # UI (optional)
    "MainWindow",
    "SettingsWindow",
]
