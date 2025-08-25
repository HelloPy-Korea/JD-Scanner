# 🧪 LangChain 기반 채용공고 요약 시스템 - MVP

사용자가 직접 입력한 **채용공고 URL**을 기반으로 LangChain-ollama를 활용해 핵심 정보를 자동으로 요약하고, 결과를 텍스트 형태로 저장하는 시스템입니다.  

## 📌 주요 기능

- **자동 내용 추출**: URL에서 채용공고 내용을 자동으로 스크래핑  
- **AI 기반 요약**: LangChain + Ollama(llama3.2)를 활용한 구조화된 요약  
- **결과 저장**: Markdown 형식으로 로컬 파일 저장  
- **에러 핸들링**: URL 요청 실패 시 명확한 에러 메시지 제공  

## 🎯 요약 포맷

```
## 회사명: [회사명]

### A. 회사소개 (비전, 연혁) & 직무 소개 (주요 업무)
### B. 자격요건 (필수조건) & 우대사항 (선택 요건)  
### C. 혜택 및 복지 & 기타사항
```

## ⚙️ 기술 스택

- **LLM 프레임워크**: LangChain + langchain-community  
- **LLM 모델**: Ollama (기본: gpt-oss:20b)  
- **웹 스크래핑**: requests + BeautifulSoup4  
- **패키지 관리**: uv  

## 🚀 설치 및 실행

### 1. 사전 준비
본 프로젝트는 python이 설치되어 있어야합니다.  
Recommend Python Version : 3.11.12   
  

### 2. 프로젝트 설정

프로젝트 클론
```bash
git clone https://github.com/HelloPy-Korea/JD-Scanner.git && \
cd JD-Scanner
```

프로젝트 의존설치
```bash
make install
```
Discord 봇 설정  
[discord developer](https://discord.com/developers/applications) 접속 후  
OAuth2 탭에 들어가서  
OAuth2 URL Generator 탭에서 "bot"을 선택  
이후 다음의 권한을 허용합니다.  
"Send Messages"

Discord에 메시지 보내기 설정
.env 안에 DISCORD_BOT_TOKEN, DISCORD_CHANNEL_IDS 를 각각 입력해줍니다.  

> DISCORD_BOT_TOKEN 입력 방법 
1. [discord developer](https://discord.com/developers/applications)에 접속하여 해당 봇에 접속 
2. Bots 탭에 들어갑니다.
3. Reset Token 버튼을 클릭 후 토큰을 Copy 합니다.
4. .env 파일의 "DISCORD_BOT_TOKEN"값 입력해줍니다.

> DISCORD_CHANNEL_IDS 입력 방법
1. 디스코드 방의 채널 명을 우클릭합니다.
2. "채널 ID 복사하기"를 클릭합니다.
3. .env 파일의 "DISCORD_CHANNEL_IDS"값 입력해줍니다.

### 3. 실행

- 인터랙티브 실행(기존 방식)

```bash
make run
```

- CLI 옵션으로 실행

```bash
# 기본 실행(모델/온도 기본값 사용)
uv run main.py --url "https://example.com/job-posting"

# 모델/온도 지정
uv run main.py --url "https://example.com/jd" --model gpt-oss:20b --temperature 0.2

# Discord 전송 활성화(옵션)
uv run main.py --url "https://example.com/jd" --discord

# 상세 로그 출력
uv run main.py --url "https://example.com/jd" --verbose
```

환경변수로도 설정할 수 있습니다.

```bash
# .env 또는 셸 환경 (기본값은 gpt-oss:20b)
MODEL_NAME=gpt-oss:20b
TEMPERATURE=0.1
DISCORD_ENABLED=false   # true로 설정 시 기본 전송 활성화
```

## 💡 사용 방법

- 인터랙티브: 프로그램 실행 후 URL 입력 → 요약 → 파일 저장
- CLI: `--url`로 바로 실행, 필요 시 `--discord`로 디스코드 전송
- 디스코드 전송은 기본 비활성화이며, 2000자 초과 메시지는 자동 분할 전송됩니다.

### 예시

```
🧪 LangChain 기반 채용공고 요약 시스템 - MVP  
==================================================  
📌 채용공고 URL을 입력하세요: https://example.com/job-posting  
  
🔧 시스템 초기화 중...  
📄 채용공고 내용 추출 중...  
✅ 내용 추출 완료 (길이: 3542 글자)  
🤖 AI 요약 처리 중... (시간이 조금 걸릴 수 있습니다)  
  
==================================================  
📋 요약 결과:  
==================================================  
## 회사명: ABC 테크  
  
### A. 회사소개 (비전, 연혁) & 직무 소개 (주요 업무):  
- 2010년 설립된 핀테크 스타트업으로...  
  
💾 결과 저장 중...  
✅ 저장 완료: output/job_posting_{회사}_{공고명}_{YYYYMMDD_HHMMSS}.md  
```

원문 HTML과 정제 텍스트는 디버깅을 위해 `output/raw/`에도 캐시됩니다.

## 📁 프로젝트 구조

```
job-posting-summarizer/
├── main.py              # 메인 실행 파일(CLI 옵션, 로깅, 캐시)
├── pyproject.toml       # uv 프로젝트 설정
├── README.md            # 프로젝트 가이드
├── uv.lock              # uv 잠금 파일
├── src/                 # 소스 코드 모듈
│   ├── __init__.py      # 패키지 초기화
│   ├── chain.py         # LangChain 체인 관리
│   ├── lang_prompt.py   # 프롬프트 설정 관리
│   ├── lang_template.py # 프롬프트 템플릿 정의
│   ├── mapreduce_chain.py # 대용량 처리(Map-Reduce)
│   ├── text_splitter.py   # 텍스트 청킹/오버랩
│   ├── token_counter.py   # 토큰 추정/검증
│   └── discord_sender.py  # Discord 전송(자동 분할)
└── output/              # 결과/캐시 저장 폴더
    ├── job_posting_*.md
    └── raw/             # 원문/정제 텍스트 캐시
        ├── {hash}_{timestamp}.html
        └── {hash}_{timestamp}.txt
```

## 🏗️ 모듈 구조

### `src/lang_template.py`
- 프롬프트 템플릿 정의  
- 기본 요약 템플릿 및 커스텀 템플릿 지원  

### `src/lang_prompt.py`  
- 프롬프트 설정 관리  
- 템플릿 유효성 검사 및 포맷팅  

### `src/chain.py`
- LangChain 체인 관리   
- Ollama LLM 초기화 및 체인 실행  

### `main.py`
- 메인 실행 로직 및 CLI 옵션 처리  
- URL 스크래핑(재시도/백오프) + 파일 저장/원문 캐시  

### JobSummaryChain 클래스 옵션

- `model_name`: 사용할 Ollama 모델명 (기본값: "gpt-oss:20b")  
- `temperature`: LLM 창의성 설정 (기본값: 0.1, 범위: 0.0~1.0)  

### 커스터마이징

프롬프트 템플릿을 수정하여 요약 형식을 변경할 수 있습니다:  

```python
# src/lang_template.py의 get_summary_template() 메서드 수정
# 또는 새로운 커스텀 템플릿 추가

from src.lang_template import JobSummaryTemplate
from src.chain import JobSummaryChain

# 커스텀 체인 생성 예시
template = JobSummaryTemplate.get_custom_template("원하는 포맷")
chain = JobSummaryChain()
custom_chain = chain.create_custom_chain(template)
```

## ⚠️ 주의사항

- Ollama 서버가 실행 중이어야 합니다  
- 일부 웹사이트는 봇 차단으로 접근이 제한될 수 있습니다  
- 큰 페이지의 경우 처리 시간이 오래 걸릴 수 있습니다  
- 네트워크 연결이 필요합니다  
- Discord 전송은 선택 기능이며, .env의 토큰/채널이 없으면 전송을 생략하고 프로그램은 계속 진행합니다.  

## 🐛 문제 해결

### Ollama 연결 오류
```bash
# Ollama 서비스 확인
ollama list

# Ollama 서버 재시작
ollama serve
```

### 모델 다운로드 오류
```bash
# 모델 재다운로드 (기본 모델)
ollama pull gpt-oss:20b
```

## 📈 향후 개발 계획
- 구조화 JSON 출력 + Pydantic 검증  
- 본문 추출 폴백(trafilatura/readability) 및 도메인별 규칙  
- 간단 유닛 테스트/CI 파이프라인 추가  


## 📄 라이선스
  
MIT License
