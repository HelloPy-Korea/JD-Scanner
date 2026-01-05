"""
메인 분석 화면 UI 모듈
- CustomTkinter 기반 메인 윈도우
- 채용공고 분석 실행
"""

import re
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional

import customtkinter as ctk
import requests
from bs4 import BeautifulSoup

from ..core.chain import JobSummaryChain, SkillGapChain
from ..utils.config_manager import ConfigManager
from ..services.discord_sender import SimpleDiscordSender
from ..services.email_sender import SimpleEmailSender
from ..services.github_analyzer import GitHubAnalyzer
from ..utils.user_manager import UserManager


class MainWindow(ctk.CTk):
    """메인 분석 화면 윈도우"""

    def __init__(self):
        super().__init__()

        self.config_manager = ConfigManager()
        self.user_manager = UserManager()

        # 윈도우 설정
        self.title("JD-Scanner - AI 채용공고 분석")
        self.geometry("700x700")
        self.resizable(True, True)
        self.minsize(600, 600)

        # 테마 설정
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        # 분석 상태
        self.is_analyzing = False

        self.create_widgets()

    def create_widgets(self):
        """위젯 생성"""
        # 메인 프레임
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 헤더 프레임
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        # 제목
        title_label = ctk.CTkLabel(
            header_frame,
            text="JD-Scanner",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        title_label.pack(side="left")

        # 설정 버튼
        settings_btn = ctk.CTkButton(
            header_frame,
            text="설정",
            command=self.open_settings,
            width=80,
            height=35,
            font=ctk.CTkFont(size=13),
        )
        settings_btn.pack(side="right")

        # 입력 폼 프레임
        form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        form_frame.pack(fill="x")

        # 이메일 입력
        email_label = ctk.CTkLabel(
            form_frame,
            text="이메일 주소 *",
            font=ctk.CTkFont(size=14),
            anchor="w",
        )
        email_label.pack(fill="x", pady=(0, 5))

        self.email_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="분석 결과를 받을 이메일 주소",
            height=40,
            font=ctk.CTkFont(size=13),
        )
        self.email_entry.pack(fill="x", pady=(0, 15))

        # 채용공고 URL 입력
        url_label = ctk.CTkLabel(
            form_frame,
            text="채용공고 URL *",
            font=ctk.CTkFont(size=14),
            anchor="w",
        )
        url_label.pack(fill="x", pady=(0, 5))

        self.url_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="https://example.com/job-posting",
            height=40,
            font=ctk.CTkFont(size=13),
        )
        self.url_entry.pack(fill="x", pady=(0, 20))

        # 분석 시작 버튼
        self.analyze_btn = ctk.CTkButton(
            form_frame,
            text="분석 시작",
            command=self.start_analysis,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.analyze_btn.pack(fill="x", pady=(0, 20))

        # 진행 상태 프레임
        status_frame = ctk.CTkFrame(main_frame)
        status_frame.pack(fill="x", pady=(0, 15))

        self.status_label = ctk.CTkLabel(
            status_frame,
            text="대기 중...",
            font=ctk.CTkFont(size=13),
            anchor="w",
        )
        self.status_label.pack(fill="x", padx=15, pady=10)

        self.progress_bar = ctk.CTkProgressBar(status_frame)
        self.progress_bar.pack(fill="x", padx=15, pady=(0, 10))
        self.progress_bar.set(0)

        # 결과 표시 영역
        result_label = ctk.CTkLabel(
            main_frame,
            text="결과:",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        )
        result_label.pack(fill="x", pady=(0, 5))

        self.result_textbox = ctk.CTkTextbox(
            main_frame,
            font=ctk.CTkFont(size=12),
            wrap="word",
        )
        self.result_textbox.pack(fill="both", expand=True)
        self.result_textbox.insert("0.0", "(분석 결과가 여기 표시됩니다)")
        self.result_textbox.configure(state="disabled")

    def open_settings(self):
        """설정 창 열기"""
        from .settings_ui import SettingsWindow

        # 설정 창을 모달로 열기
        settings = ctk.CTkToplevel(self)
        settings.title("JD-Scanner 설정")
        settings.geometry("600x500")
        settings.resizable(False, False)
        settings.grab_set()

        # 메인 윈도우 중앙에 위치
        settings.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 600) // 2
        y = self.winfo_y() + (self.winfo_height() - 500) // 2
        settings.geometry(f"+{x}+{y}")

        # 설정 UI 컨텐츠 추가
        self._create_settings_content(settings)

    def _create_settings_content(self, parent):
        """설정 창 내용 생성"""
        config_manager = ConfigManager()
        entries = {}
        show_password_vars = {}

        # 메인 프레임
        main_frame = ctk.CTkFrame(parent)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 제목
        title_label = ctk.CTkLabel(
            main_frame,
            text="설정",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title_label.pack(pady=(0, 15))

        # 탭뷰
        tabview = ctk.CTkTabview(main_frame)
        tabview.pack(fill="both", expand=True)

        tabview.add("Discord")
        tabview.add("Email")
        tabview.add("GitHub")

        def create_text_field(parent_frame, label, key, placeholder):
            lbl = ctk.CTkLabel(parent_frame, text=label, font=ctk.CTkFont(size=12), anchor="w")
            lbl.pack(fill="x", pady=(8, 2))
            entry = ctk.CTkEntry(parent_frame, placeholder_text=placeholder, height=32)
            entry.pack(fill="x", pady=(0, 5))
            entries[key] = entry

        def create_password_field(parent_frame, label, key, placeholder):
            lbl = ctk.CTkLabel(parent_frame, text=label, font=ctk.CTkFont(size=12), anchor="w")
            lbl.pack(fill="x", pady=(8, 2))
            field_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
            field_frame.pack(fill="x", pady=(0, 5))
            entry = ctk.CTkEntry(field_frame, placeholder_text=placeholder, height=32, show="*")
            entry.pack(side="left", fill="x", expand=True)
            show_password_vars[key] = False

            def toggle():
                show_password_vars[key] = not show_password_vars[key]
                entry.configure(show="" if show_password_vars[key] else "*")

            toggle_btn = ctk.CTkButton(field_frame, text="표시", width=45, height=32, command=toggle)
            toggle_btn.pack(side="right", padx=(5, 0))
            entries[key] = entry

        # Discord 탭
        discord_frame = ctk.CTkFrame(tabview.tab("Discord"), fg_color="transparent")
        discord_frame.pack(fill="both", expand=True, padx=10, pady=10)
        create_password_field(discord_frame, "Discord Bot Token", "DISCORD_BOT_TOKEN", "토큰 입력")
        create_text_field(discord_frame, "Channel IDs (쉼표 구분)", "DISCORD_CHANNEL_IDS", "123,456")

        # Email 탭
        email_frame = ctk.CTkFrame(tabview.tab("Email"), fg_color="transparent")
        email_frame.pack(fill="both", expand=True, padx=10, pady=10)
        create_text_field(email_frame, "SMTP 서버", "SMTP_SERVER", "smtp.gmail.com")
        create_text_field(email_frame, "SMTP 포트", "SMTP_PORT", "587")
        create_text_field(email_frame, "발신자 이메일", "SENDER_EMAIL", "your@email.com")
        create_password_field(email_frame, "발신자 비밀번호", "SENDER_PASSWORD", "앱 비밀번호")

        # GitHub 탭
        github_frame = ctk.CTkFrame(tabview.tab("GitHub"), fg_color="transparent")
        github_frame.pack(fill="both", expand=True, padx=10, pady=10)
        create_password_field(github_frame, "GitHub Token", "GITHUB_TOKEN", "Personal Access Token")
        create_text_field(github_frame, "GitHub 프로필 URL", "GITHUB_PROFILE_URL", "https://github.com/username")
        info_lbl = ctk.CTkLabel(github_frame, text="※ 스킬 갭 분석 시 사용됩니다", font=ctk.CTkFont(size=11), text_color="gray")
        info_lbl.pack(anchor="w")

        # 기존 설정 로드
        config = config_manager.get_all()
        for key, entry in entries.items():
            value = config.get(key, "")
            if value:
                entry.delete(0, "end")
                entry.insert(0, value)

        # 버튼 프레임
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(15, 0))

        def save():
            new_config = {k: e.get().strip() for k, e in entries.items()}
            errors = config_manager.validate_config(new_config)
            if errors:
                self.show_message("오류", "\n".join(errors))
                return
            if config_manager.save_config(new_config):
                self.show_message("완료", "설정이 저장되었습니다.")
                parent.destroy()

        save_btn = ctk.CTkButton(btn_frame, text="저장", command=save, width=100, height=35)
        save_btn.pack(side="right", padx=(10, 0))
        cancel_btn = ctk.CTkButton(btn_frame, text="취소", command=parent.destroy, width=100, height=35, fg_color="gray")
        cancel_btn.pack(side="right")

    def validate_inputs(self) -> tuple[bool, str]:
        """입력값 유효성 검사"""
        email = self.email_entry.get().strip()
        url = self.url_entry.get().strip()

        if not email:
            return False, "이메일 주소를 입력해주세요."

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            return False, "올바른 이메일 형식이 아닙니다."

        if not url:
            return False, "채용공고 URL을 입력해주세요."

        if not (url.startswith("http://") or url.startswith("https://")):
            return False, "올바른 URL 형식이 아닙니다. (http:// 또는 https://로 시작)"

        return True, ""

    def start_analysis(self):
        """분석 시작"""
        if self.is_analyzing:
            return

        # 입력값 검증
        valid, error = self.validate_inputs()
        if not valid:
            self.show_message("입력 오류", error)
            return

        # 분석 시작
        self.is_analyzing = True
        self.analyze_btn.configure(state="disabled", text="분석 중...")
        self.progress_bar.set(0)
        self.update_status("분석 시작...")

        # 결과 영역 초기화
        self.result_textbox.configure(state="normal")
        self.result_textbox.delete("0.0", "end")
        self.result_textbox.configure(state="disabled")

        # 별도 스레드에서 분석 실행
        thread = threading.Thread(target=self._run_analysis)
        thread.daemon = True
        thread.start()

    def _run_analysis(self):
        """분석 실행 (별도 스레드)"""
        try:
            email = self.email_entry.get().strip()
            url = self.url_entry.get().strip()

            # 사용자 등록/업데이트
            github_url = self.config_manager.get("GITHUB_PROFILE_URL")
            user = self.user_manager.register_or_update_user(email, github_url if github_url else None)

            # Step 1: 내용 추출
            self.update_status("채용공고 내용 추출 중...")
            self.progress_bar.set(0.1)
            content = self._extract_content_from_url(url)

            # Step 2: AI 요약
            self.update_status("AI 요약 처리 중... (시간이 걸릴 수 있습니다)")
            self.progress_bar.set(0.2)
            chain = JobSummaryChain()
            summary = chain.run_summary(content, verbose=True)
            summary_with_link = f"{summary}\n\n[원본 채용공고]({url})"

            # 결과 변수 초기화
            skill_gap_report = None
            interview_questions_ko = None
            interview_questions_en = None
            full_report = summary_with_link

            # Step 3-5: GitHub 분석 (설정된 경우)
            if github_url:
                self.update_status("GitHub 프로필 분석 중...")
                self.progress_bar.set(0.4)

                github_analyzer = GitHubAnalyzer()
                github_profile = github_analyzer.analyze_profile(github_url)

                if github_profile:
                    self.update_status("스킬 갭 분석 중...")
                    self.progress_bar.set(0.5)

                    skill_gap_chain = SkillGapChain()
                    requirements = skill_gap_chain.extract_requirements(summary)

                    profile_summary = github_profile.to_summary_dict()
                    skill_gap_report = skill_gap_chain.analyze_skill_gap(
                        requirements, profile_summary
                    )

                    self.update_status("면접 질문 생성 중...")
                    self.progress_bar.set(0.6)

                    job_title = requirements.get("job_title", "Software Developer")
                    candidate_techs = github_profile.get_all_languages()

                    interview_questions_ko = skill_gap_chain.generate_interview_questions(
                        skill_gap_report, job_title, candidate_techs, "ko"
                    )
                    interview_questions_en = skill_gap_chain.generate_interview_questions(
                        skill_gap_report, job_title, candidate_techs, "en"
                    )

                    full_report = f"""# 채용공고 분석 리포트

## 채용공고 요약
{summary_with_link}

---

## 스킬 갭 분석
{skill_gap_report}

---

## 면접 준비 질문 (한국어)
{interview_questions_ko}

---

## Interview Preparation Questions (English)
{interview_questions_en}
"""

            # 결과 저장
            self.update_status("결과 저장 중...")
            self.progress_bar.set(0.7)
            self._save_result(full_report, url)

            # 알림 발송
            self.update_status("알림 발송 중...")
            self.progress_bar.set(0.8)

            # Discord 알림
            try:
                discord_sender = SimpleDiscordSender(summary_with_link)
                discord_sender.run()
            except Exception:
                pass

            # Email 알림
            try:
                email_sender = SimpleEmailSender(
                    message=full_report,
                    recipient_email=email,
                    subject=f"JD-Scanner 분석 결과: {url[:50]}...",
                )
                email_sender.run()
            except Exception:
                pass

            # 분석 횟수 업데이트
            self.user_manager.increment_analysis_count(user)

            # 완료
            self.progress_bar.set(1.0)
            self.update_status("분석 완료!")
            self._display_result(full_report)

        except Exception as e:
            self.update_status(f"오류 발생: {e}")
            self._display_result(f"오류가 발생했습니다:\n\n{e}")

        finally:
            self.is_analyzing = False
            self.after(0, lambda: self.analyze_btn.configure(state="normal", text="분석 시작"))

    def _extract_content_from_url(self, url: str) -> str:
        """URL에서 채용공고 내용 추출"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        for script in soup(["script", "style"]):
            script.decompose()

        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        content = " ".join(chunk for chunk in chunks if chunk)

        if not content.strip():
            raise ValueError("추출된 내용이 비어있습니다.")

        return content

    def _save_result(self, content: str, url: str):
        """결과 저장"""
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_{timestamp}.md"
        file_path = output_dir / filename

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _display_result(self, content: str):
        """결과 표시"""
        def update():
            self.result_textbox.configure(state="normal")
            self.result_textbox.delete("0.0", "end")
            self.result_textbox.insert("0.0", content)
            self.result_textbox.configure(state="disabled")

        self.after(0, update)

    def update_status(self, message: str):
        """상태 업데이트 (스레드 안전)"""
        self.after(0, lambda: self.status_label.configure(text=message))

    def show_message(self, title: str, message: str):
        """메시지 다이얼로그 표시"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("400x150")
        dialog.resizable(False, False)
        dialog.grab_set()

        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 400) // 2
        y = self.winfo_y() + (self.winfo_height() - 150) // 2
        dialog.geometry(f"+{x}+{y}")

        label = ctk.CTkLabel(
            dialog,
            text=message,
            font=ctk.CTkFont(size=13),
            wraplength=350,
        )
        label.pack(expand=True, padx=20, pady=20)

        btn = ctk.CTkButton(
            dialog,
            text="확인",
            command=dialog.destroy,
            width=100,
        )
        btn.pack(pady=(0, 20))
