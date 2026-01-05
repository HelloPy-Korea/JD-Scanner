# JD-Scanner

AI 기반 채용공고 분석 및 면접 준비 시스템입니다. 채용공고 URL과 GitHub 프로필을 분석하여 스킬 갭을 파악하고, 맞춤형 면접 질문을 생성합니다.

## 주요 기능

| 기능 | 설명 |
|------|------|
| **채용공고 요약** | URL에서 채용공고 스크래핑 및 AI 요약 |
| **GitHub 분석** | 공개 레포지토리 분석 및 기술 스택 추출 |
| **스킬 갭 분석** | 채용 요구사항과 보유 기술 비교 분석 |
| **면접 질문 생성** | 한국어/영어 맞춤형 면접 질문 생성 |
| **이메일 발송** | 분석 결과 이메일 자동 발송 |
| **Discord 연동** | 요약 결과 Discord 채널 전송 |

## 동작 흐름

```
[이메일/GitHub 입력] → [채용공고 URL 입력] → [채용공고 요약]
                                                    ↓
                                         [GitHub 프로필 분석]
                                                    ↓
                                         [스킬 갭 분석]
                                                    ↓
                                    [면접 질문 생성 (한/영)]
                                                    ↓
                              [파일 저장 + 이메일/Discord 발송]
```

## 기술 스택

| 분류 | 기술 |
|------|------|
| Core | LangChain 0.3.25+ / LangChain-Ollama 0.3.3+ |
| LLM | Ollama (llama3.2) |
| 스크래핑 | BeautifulSoup4 / requests |
| 이메일 | Gmail SMTP (smtplib) |
| 연동 | discord.py 2.5.2+ |
| 설정관리 | python-dotenv |
| 패키지관리 | uv |
| Python | 3.11+ |

## 프로젝트 구조

```
JD-Scanner/
├── main.py                     # GUI 진입점
├── pyproject.toml              # 프로젝트 메타데이터
├── makefile                    # 설치/실행 자동화
├── .env                        # 환경설정
├── src/
│   ├── __init__.py             # 패키지 초기화
│   ├── ui/                     # UI 레이어 (Presentation)
│   │   ├── __init__.py
│   │   ├── main_ui.py          # 메인 분석 화면
│   │   └── settings_ui.py      # 설정 화면
│   ├── core/                   # Core 레이어 (Domain)
│   │   ├── __init__.py
│   │   ├── chain.py            # LangChain 체인 (요약 + 스킬갭)
│   │   ├── mapreduce_chain.py  # Map-Reduce 대용량 처리
│   │   ├── lang_prompt.py      # 프롬프트 설정
│   │   └── lang_template.py    # 프롬프트 템플릿
│   ├── services/               # Services 레이어 (Infrastructure)
│   │   ├── __init__.py
│   │   ├── discord_sender.py   # Discord 메시지 전송
│   │   ├── email_sender.py     # 이메일 발송
│   │   └── github_analyzer.py  # GitHub 프로필 분석
│   └── utils/                  # Utils 레이어 (Shared)
│       ├── __init__.py
│       ├── config_manager.py   # 환경변수 관리
│       ├── user_manager.py     # 사용자 정보 관리
│       ├── token_counter.py    # 토큰 카운터
│       └── text_splitter.py    # 텍스트 청킹
├── output/
│   ├── users/                  # 사용자 데이터 저장
│   └── *.md                    # 분석 결과 파일
└── test/                       # 테스트 파일
```

## 설치 및 실행

### 1. 사전 준비

- Python 3.11+ 설치
- Ollama 설치 및 실행

### 2. 프로젝트 설정

```bash
# 프로젝트 클론
git clone https://github.com/HelloPy-Korea/JD-Scanner.git
cd JD-Scanner

# 의존성 설치
make install
```

### 3. 환경 변수 설정

`.env` 파일:
```bash
# Discord (선택)
DISCORD_BOT_TOKEN=your_bot_token
DISCORD_CHANNEL_IDS=channel_id_1,channel_id_2

# 이메일 (Gmail SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password

# GitHub API (선택 - 높은 API 제한)
GITHUB_TOKEN=your_github_token
```

**Gmail 앱 비밀번호 설정:**
1. Google 계정 → 보안 → 2단계 인증 활성화
2. 앱 비밀번호 생성 → 생성된 16자리 비밀번호를 `SENDER_PASSWORD`에 입력

### 4. 실행

```bash
make run
```

## 사용 방법

```
============================================================
  JD-Scanner - AI 기반 채용공고 분석 및 면접 준비 시스템
============================================================

[Step 1/6] 사용자 정보 입력
==================================================
  사용자 정보 입력
==================================================

이메일 주소를 입력하세요: user@example.com

GitHub 프로필을 추가하시겠습니까? (y/n): y
GitHub 프로필 URL을 입력하세요: https://github.com/username

환영합니다, user@example.com!

[Step 2/6] 채용공고 입력
----------------------------------------
채용공고 URL을 입력하세요: https://example.com/job

[Step 3/6] 채용공고 분석
...

[Step 4/6] GitHub 프로필 분석
...

[Step 5/6] 스킬 갭 분석
...

[Step 6/6] 면접 질문 생성
...

============================================================
분석 완료!
============================================================
```

## 출력 형식

### 채용공고 요약
```markdown
## 공고명: [공고명]
### 회사명: [회사명]

**마감기한**
- [마감일]

### A. 회사소개 & 직무 소개
### B. 자격요건 & 우대사항
### C. 혜택 및 복지
```

### 스킬 갭 분석
```markdown
### 1. 기술 스킬 매칭 분석
- 일치하는 기술
- 부족한 필수 기술
- 지원자의 추가 기술

### 2. 프로젝트 경험 분석
### 3. 기술 성숙도 평가
### 4. 종합 매칭 점수
```

### 면접 질문 (한국어/영어)
```markdown
### A. 부족한 기술에 대한 질문
### B. 대안 기술 선택에 대한 질문
### C. 기술 갭 극복 계획 질문
### D. 프로젝트 심화 질문
### E. 실제 업무 시나리오 질문
```

## 모듈 설명

### 레이어 구조

| 레이어 | 역할 | 의존 가능 |
|--------|------|-----------|
| `ui/` | 사용자 인터페이스 | core, services, utils |
| `core/` | 핵심 비즈니스 로직 | utils |
| `services/` | 외부 서비스 연동 | utils |
| `utils/` | 공통 유틸리티 | 없음 |

### 주요 모듈

| 모듈 | 설명 |
|------|------|
| `main.py` | GUI 진입점, 설정 확인 후 윈도우 실행 |
| `src/ui/main_ui.py` | 메인 분석 화면, 분석 파이프라인 실행 |
| `src/ui/settings_ui.py` | 설정 화면 (Discord, Email, GitHub) |
| `src/core/chain.py` | JobSummaryChain, SkillGapChain |
| `src/core/mapreduce_chain.py` | 대용량 텍스트 Map-Reduce 처리 |
| `src/core/lang_template.py` | 요약/스킬갭/면접질문 템플릿 |
| `src/services/github_analyzer.py` | GitHub API 연동, 프로필 분석 |
| `src/services/email_sender.py` | Gmail SMTP 이메일 발송 |
| `src/services/discord_sender.py` | Discord 메시지 전송 |
| `src/utils/config_manager.py` | .env 환경변수 관리 |
| `src/utils/user_manager.py` | 사용자 정보 수집 및 저장 |

## 코딩 컨벤션

### 네이밍 규칙

| 구분 | 규칙 | 예시 |
|------|------|------|
| 클래스명 | PascalCase | `JobSummaryChain`, `ConfigManager` |
| 함수/메서드명 | snake_case | `run_summary`, `validate_inputs` |
| 상수 | UPPER_SNAKE_CASE | `BASE_URL`, `SCHEMA` |
| private 메서드 | underscore prefix | `_initialize_llm`, `_create_chain` |

### 파일 구조

```python
"""
모듈 설명 docstring
- 주요 기능 1
- 주요 기능 2
"""

# 표준 라이브러리
import os
import sys

# 서드파티 라이브러리
from langchain_ollama.llms import OllamaLLM

# 로컬 모듈
from ..utils.config_manager import ConfigManager
```

### 타입 힌팅

```python
from typing import Optional, Dict, List, Literal

def analyze_profile(self, github_url: str) -> Optional[GitHubProfile]:
    """GitHub 프로필 분석"""
    ...

def generate_questions(
    self,
    language: Literal["ko", "en"] = "ko"
) -> str:
    ...
```

### 레이어 의존성 규칙

```
ui/ → core/, services/, utils/ (허용)
core/ → utils/ (허용)
services/ → utils/ (허용)
하위 레이어 → 상위 레이어 (금지)
```

## 문제 해결

### Ollama 연결 오류
```bash
ollama list
ollama serve
```

### 모델 다운로드
```bash
ollama pull llama3.2
```

### Gmail 인증 오류
- 2단계 인증 활성화 확인
- 앱 비밀번호 사용 (일반 비밀번호 X)

### GitHub API 제한
- `GITHUB_TOKEN` 설정으로 제한 완화

## 버전 정보

**현재 버전:** 0.1.0

### v0.1.0 (New)
- 이메일 수집 및 발송 기능
- GitHub 프로필 분석 기능
- 스킬 갭 분석 기능
- 맞춤형 면접 질문 생성 (한국어/영어)
- 사용자 데이터 로컬 저장

### v0.0.2
- LangChain API 마이그레이션 (LCEL)
- Discord 메시지 기능
- 프롬프트 개선

## 라이선스

MIT License
