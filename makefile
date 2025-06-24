OS := $(shell uname)

install:
	@$(MAKE) check-ollama
	@$(MAKE) check-uv
	@$(MAKE) setup-project
	@touch .env
	@echo 'DISCORD_BOT_TOKEN=여기에_봇_토큰_붙여넣기' >> .env
	@echo 'DISCORD_CHANNEL_IDS=여기에 채널 ID 붙여넣기' >> .env

check-ollama:
	@echo "ollama 설치 여부 확인 중"
	@command -v ollama >/dev/null 2>&1 && \
		echo "✅ ollama가 이미 설치되어 있습니다." || \
		$(MAKE) install-ollama

install-ollama:
	@echo "⬇️  ollama가 설치되어 있지 않아 설치를 진행합니다."
ifeq ($(OS), Darwin)
	@echo "🔄 Ollama 설치를 시작합니다."
	@brew install ollama
else ifeq ($(OS), Linux)
	@echo "Detected Linux or others"
	@sudo apt install -y curl
	@curl -fsSL https://ollama.ai/install.sh | sh && command -v ollama >/dev/null || ( \
		echo "❌ Ollama 설치에 실패했습니다. [문의페이지](https://github.com/HelloPy-Korea/JD-Scanner/issues) issue 등록해 주세요." && exit 1 \
	)
else
	@echo "❌ 지원하지 않는 운영체제입니다."
	@exit 1
endif
	@echo "ollama 서버 구동"
	@ollama serve &
	@sleep 5
	@echo "✅ Ollama 설치 성공. 모델을 다운로드합니다..."
	@ollama pull llama3.2
	@echo "✅ Ollama 모델 다운로드 완료."

check-uv:
	@echo "uv 설치 여부 확인 중"
	@command -v uv >/dev/null 2>&1 && \
		echo "✅ uv가 이미 설치되어 있습니다." || \
		$(MAKE) install-uv

install-uv:
	@echo "⬇️  uv가 설치되어 있지 않아 설치를 진행합니다."
	@curl -LsSf https://astral.sh/uv/install.sh | sh
	@echo "✅ uv 설치 완료."

setup-project:
	@echo "JD-Scanner 구성 요소를 설치합니다."
	@uv sync
	@echo "✅ JD-Scanner 구성 요소 설치 완료."

.PHONY: install check-ollama install-ollama check-uv install-uv setup-project

run:
	@echo "ollama 실행합니다."
	@nohup ollama serve &
	@echo "JD-Scanner를 실행합니다."
	@uv run main.py
	@echo "ollama를 종료하시겠습니까? (y/n)"; \
	read answer; \
	if [ "$$answer" = "y" ] || [ "$$answer" = "Y" ]; then \
		echo "ollama를 종료합니다."; \
		ollama stop llama3.2;
	else \
		echo "ollama를 종료하지 않고 종료합니다."; \
	fi