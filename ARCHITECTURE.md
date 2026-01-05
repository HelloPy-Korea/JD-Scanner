# JD-Scanner 프로젝트 구조도

## 개요

**JD-Scanner**는 AI 기반 채용공고 분석 및 면접 준비 시스템입니다.
Ollama LLM과 LangChain을 활용하여 채용공고를 요약하고, GitHub 프로필 기반 스킬 갭 분석 및 맞춤형 면접 질문을 생성합니다.

---

## 디렉토리 구조

```
JD-Scanner/
├── main.py                    # GUI 진입점
├── .env                       # 환경변수 설정 파일
├── output/                    # 분석 결과 저장
│   ├── users/                 # 사용자 데이터
│   │   └── users.json
│   └── analysis_*.md          # 분석 결과 파일들
├── src/                       # 소스 코드
│   ├── __init__.py
│   ├── main_ui.py             # 메인 분석 화면 UI
│   ├── settings_ui.py         # 설정 화면 UI
│   ├── config_manager.py      # 환경변수 관리
│   ├── user_manager.py        # 사용자 프로필 관리
│   ├── chain.py               # LangChain 체인 관리
│   ├── mapreduce_chain.py     # Map-Reduce 대용량 처리
│   ├── lang_prompt.py         # 프롬프트 설정 관리
│   ├── lang_template.py       # 프롬프트 템플릿 정의
│   ├── token_counter.py       # 토큰 카운터/검증
│   ├── text_splitter.py       # 텍스트 청킹
│   ├── github_analyzer.py     # GitHub 프로필 분석
│   ├── email_sender.py        # 이메일 발송
│   └── discord_sender.py      # Discord 알림 발송
└── test/                      # 테스트 코드
    ├── discord_test.py
    └── discord_claude_test.py
```

---

## 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────────────┐
│                           사용자 인터페이스                           │
│  ┌─────────────────────┐    ┌─────────────────────────────────────┐ │
│  │   SettingsWindow    │───▶│          MainWindow                 │ │
│  │   (설정 화면)        │    │   (메인 분석 화면)                    │ │
│  │   - Discord 설정    │    │   - URL 입력                        │ │
│  │   - Email 설정      │    │   - 이메일 입력                      │ │
│  │   - GitHub 설정     │    │   - 분석 실행/결과 표시               │ │
│  └─────────────────────┘    └─────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           핵심 비즈니스 로직                          │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                      분석 파이프라인                          │   │
│  │                                                              │   │
│  │  1. URL 콘텐츠 추출 (BeautifulSoup)                          │   │
│  │              │                                               │   │
│  │              ▼                                               │   │
│  │  2. 토큰 검증 (SimpleTokenCounter)                           │   │
│  │              │                                               │   │
│  │      ┌───────┴───────┐                                       │   │
│  │      ▼               ▼                                       │   │
│  │  [직접 처리]    [Map-Reduce 처리]                             │   │
│  │      │               │                                       │   │
│  │      └───────┬───────┘                                       │   │
│  │              ▼                                               │   │
│  │  3. AI 요약 (JobSummaryChain)                                │   │
│  │              │                                               │   │
│  │              ▼                                               │   │
│  │  4. GitHub 분석 (GitHubAnalyzer) ──── [선택적]               │   │
│  │              │                                               │   │
│  │              ▼                                               │   │
│  │  5. 스킬 갭 분석 (SkillGapChain)                             │   │
│  │              │                                               │   │
│  │              ▼                                               │   │
│  │  6. 면접 질문 생성 (한국어/영어)                               │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           알림/저장 시스템                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐  │
│  │ SimpleDiscord   │  │ SimpleEmail     │  │    파일 저장         │  │
│  │ Sender          │  │ Sender          │  │   (output/*.md)     │  │
│  │ (Discord 알림)  │  │ (Email 발송)    │  │                     │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 모듈 상세 설명

### 1. UI 모듈

#### `main.py`
- **역할**: GUI 애플리케이션 진입점
- **기능**:
  - 설정 상태 확인 후 적절한 윈도우 실행
  - 설정 미완료 시 `SettingsWindow` → 완료 후 `MainWindow`

#### `main_ui.py` - MainWindow
- **역할**: 메인 분석 화면 (CustomTkinter 기반)
- **주요 기능**:
  - 채용공고 URL 입력
  - 수신 이메일 입력
  - 분석 실행 및 진행 상태 표시
  - 결과 표시 및 알림 발송

#### `settings_ui.py` - SettingsWindow
- **역할**: 설정 화면 (탭 구조)
- **탭 구성**:
  - Discord: Bot Token, Channel IDs
  - Email: SMTP 서버, 발신자 정보
  - GitHub: Token, Profile URL

---

### 2. 설정/데이터 관리 모듈

#### `config_manager.py` - ConfigManager
- **역할**: 환경변수 중앙 관리
- **주요 기능**:
  - `.env` 파일 로드/저장
  - 설정 유효성 검증 (이메일, URL 형식)
  - 설정 완료 상태 확인

```python
# 지원 환경변수
SCHEMA = {
    "DISCORD_BOT_TOKEN": {...},
    "DISCORD_CHANNEL_IDS": {...},
    "SMTP_SERVER": {...},
    "SMTP_PORT": {...},
    "SENDER_EMAIL": {...},
    "SENDER_PASSWORD": {...},
    "GITHUB_TOKEN": {...},
    "GITHUB_PROFILE_URL": {...},
}
```

#### `user_manager.py` - UserManager, UserProfile
- **역할**: 사용자 프로필 관리
- **저장 위치**: `output/users/users.json`
- **주요 기능**:
  - 사용자 등록/업데이트
  - 분석 횟수 추적
  - 이메일/GitHub URL 검증

---

### 3. LLM 체인 모듈

#### `chain.py` - JobSummaryChain
- **역할**: 채용공고 요약 체인 관리
- **주요 기능**:
  - Ollama LLM 초기화 (기본: llama3.2)
  - 토큰 크기에 따른 처리 방식 자동 선택
  - 직접 처리 또는 Map-Reduce 처리 분기

#### `chain.py` - SkillGapChain
- **역할**: 스킬 갭 분석 및 면접 질문 생성
- **주요 기능**:
  - 채용공고에서 요구사항 추출 (JSON 형식)
  - GitHub 프로필과 요구사항 비교 분석
  - 한국어/영어 면접 질문 생성

#### `mapreduce_chain.py` - MapReduceJobChain
- **역할**: 대용량 텍스트 Map-Reduce 처리
- **처리 흐름**:
  1. 텍스트 청킹 (JobPostingSplitter)
  2. Map 단계: 각 청크 병렬 요약
  3. Reduce 단계: 요약 통합 (재귀적 처리 지원)

```
원본 텍스트 ──▶ [청크1] [청크2] [청크3] ... ──▶ Map (병렬 요약)
                                                    │
                                                    ▼
                                            [요약1] [요약2] [요약3]
                                                    │
                                                    ▼
                                              Reduce (통합)
                                                    │
                                                    ▼
                                               최종 요약
```

---

### 4. 프롬프트 모듈

#### `lang_prompt.py` - PromptConfig
- **역할**: 프롬프트 설정 관리자
- **제공 프롬프트**:
  - 채용공고 요약
  - 스킬 갭 분석
  - 면접 질문 생성 (한국어/영어)
  - 요구사항 추출

#### `lang_template.py` - JobSummaryTemplate, SkillGapTemplate
- **역할**: 프롬프트 템플릿 정의
- **템플릿 종류**:
  - `get_summary_template()`: 기본 요약
  - `get_map_template()`: Map 단계용
  - `get_reduce_template()`: Reduce 단계용
  - `get_skill_gap_template()`: 스킬 갭 분석
  - `get_interview_questions_template_ko()`: 한국어 면접 질문
  - `get_interview_questions_template_en()`: 영어 면접 질문

---

### 5. 텍스트 처리 모듈

#### `text_splitter.py` - SmartTextSplitter, JobPostingSplitter
- **역할**: 대용량 텍스트 청킹
- **특징**:
  - 구분자 우선순위 기반 분할 (문단 → 문장 → 단어)
  - 청크 간 오버랩 지원
  - 채용공고 특화 구분자 (`## `, `### `, `**`, `- `)

#### `token_counter.py` - SimpleTokenCounter, ContentPreprocessor
- **역할**: 토큰 카운터 및 콘텐츠 전처리
- **SimpleTokenCounter 기능**:
  - 추정 토큰 수 계산 (한국어/영어 혼합 고려)
  - 토큰 제한 검증
  - 권장 처리 방식 제안

- **ContentPreprocessor 기능**:
  - HTML 태그 제거
  - 중복 라인 제거
  - 핵심 섹션 추출

---

### 6. 외부 연동 모듈

#### `github_analyzer.py` - GitHubAnalyzer, GitHubProfile, Repository
- **역할**: GitHub 프로필 분석
- **주요 기능**:
  - 사용자 프로필 조회
  - 공개 레포지토리 분석 (포크 제외)
  - 언어별 비율 계산
  - 기술 스택 추출 (frameworks, tools, databases)

```python
TECH_PATTERNS = {
    "frameworks": ["react", "angular", "vue", "django", "flask", ...],
    "tools": ["docker", "kubernetes", "terraform", ...],
    "databases": ["postgresql", "mysql", "mongodb", ...],
}
```

#### `email_sender.py` - SimpleEmailSender
- **역할**: Gmail SMTP 이메일 발송
- **주요 기능**:
  - 마크다운 → HTML 변환
  - TLS 보안 연결
  - HTML + Plain Text 멀티파트 이메일

#### `discord_sender.py` - SimpleDiscordSender
- **역할**: Discord 채널 메시지 발송
- **주요 기능**:
  - 여러 채널 동시 발송 지원
  - Bot 토큰 인증

---

## 데이터 흐름

```
사용자 입력 (URL, Email)
         │
         ▼
┌────────────────────────────────────┐
│  1. 웹 콘텐츠 추출                  │
│     requests + BeautifulSoup       │
└────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│  2. 콘텐츠 전처리                   │
│     ContentPreprocessor            │
│     - HTML 태그 제거               │
│     - 중복 제거                    │
└────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│  3. 토큰 검증                       │
│     SimpleTokenCounter             │
│     - 토큰 수 추정                  │
│     - 처리 방식 결정               │
└────────────────────────────────────┘
         │
    ┌────┴────┐
    ▼         ▼
[직접처리] [Map-Reduce]
    │         │
    └────┬────┘
         │
         ▼
┌────────────────────────────────────┐
│  4. AI 요약                        │
│     JobSummaryChain                │
│     Ollama LLM (llama3.2)          │
└────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│  5. GitHub 분석 (선택적)            │
│     GitHubAnalyzer                 │
│     - 레포지토리 분석              │
│     - 기술 스택 추출               │
└────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│  6. 스킬 갭 분석                    │
│     SkillGapChain                  │
│     - 요구사항 vs GitHub 비교       │
│     - 매칭 점수 산출               │
└────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│  7. 면접 질문 생성                  │
│     SkillGapChain                  │
│     - 한국어 질문                  │
│     - 영어 질문                    │
└────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│  8. 결과 저장 및 발송               │
│     - 파일 저장 (output/*.md)      │
│     - Discord 알림                 │
│     - Email 발송                   │
└────────────────────────────────────┘
```

---

## 기술 스택

| 분류 | 기술 |
|------|------|
| **GUI** | CustomTkinter |
| **LLM** | Ollama (llama3.2) |
| **AI Framework** | LangChain |
| **웹 스크래핑** | requests, BeautifulSoup4 |
| **이메일** | smtplib (Gmail SMTP) |
| **Discord** | discord.py |
| **GitHub API** | requests (REST API) |
| **환경변수** | python-dotenv |

---

## 출력 형식

### 채용공고 요약 형식
```markdown
## 공고명: [공고명]
### 회사명: [회사명]

**마감기한**
- [마감기한]

### A. 회사소개 & 직무 소개
- [내용]

### B. 자격요건 & 우대사항
**필수조건:**
- [내용]

**우대사항:**
- [내용]

### C. 혜택 및 복지 & 기타사항
- [내용]
```

### 스킬 갭 분석 형식
```markdown
### 1. 기술 스킬 매칭 분석
**일치하는 기술:** [...]
**부족한 필수 기술:** [...]
**지원자의 추가 기술:** [...]

### 2. 프로젝트 경험 분석
[...]

### 3. 기술 성숙도 평가
[...]

### 4. 종합 매칭 점수
- **점수:** [0-100점]
- **평가:** [...]
```

---

## 환경 설정

### 필수 환경변수 (.env)
```env
# Discord 설정 (선택)
DISCORD_BOT_TOKEN=your_bot_token
DISCORD_CHANNEL_IDS=123456789,987654321

# Email 설정 (선택)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your@email.com
SENDER_PASSWORD=your_app_password

# GitHub 설정 (선택 - 스킬 갭 분석용)
GITHUB_TOKEN=your_github_token
GITHUB_PROFILE_URL=https://github.com/username
```

### 최소 설정 요건
- Discord 또는 Email 중 하나 이상 설정 필요
- GitHub 설정은 스킬 갭 분석 기능 사용 시에만 필요
