"""
설정 화면 UI 모듈
- CustomTkinter 기반 설정 윈도우
- Discord, Email, GitHub 탭 구조
"""

from typing import Callable, Optional

import customtkinter as ctk

from ..utils.config_manager import ConfigManager


class SettingsWindow(ctk.CTk):
    """설정 화면 윈도우"""

    def __init__(self, on_save_callback: Optional[Callable] = None):
        super().__init__()

        self.on_save_callback = on_save_callback
        self.config_manager = ConfigManager()

        # 윈도우 설정
        self.title("JD-Scanner 설정")
        self.geometry("600x500")
        self.resizable(False, False)

        # 테마 설정
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        # 입력 필드 참조 저장
        self.entries = {}
        self.show_password_vars = {}

        self.create_widgets()
        self.load_existing_config()

    def create_widgets(self):
        """위젯 생성"""
        # 메인 프레임
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 제목
        title_label = ctk.CTkLabel(
            main_frame,
            text="JD-Scanner 설정",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title_label.pack(pady=(0, 20))

        # 탭뷰 생성
        self.tabview = ctk.CTkTabview(main_frame)
        self.tabview.pack(fill="both", expand=True)

        # 탭 추가
        self.tabview.add("Discord")
        self.tabview.add("Email")
        self.tabview.add("GitHub")

        # 각 탭 내용 생성
        self.create_discord_tab(self.tabview.tab("Discord"))
        self.create_email_tab(self.tabview.tab("Email"))
        self.create_github_tab(self.tabview.tab("GitHub"))

        # 버튼 프레임
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        # 저장 버튼
        save_btn = ctk.CTkButton(
            button_frame,
            text="저장",
            command=self.save_config,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14),
        )
        save_btn.pack(side="right", padx=(10, 0))

        # 취소 버튼
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="취소",
            command=self.on_cancel,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="gray",
            hover_color="darkgray",
        )
        cancel_btn.pack(side="right")

    def create_discord_tab(self, parent):
        """Discord 탭 생성"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Bot Token
        self.create_password_field(
            frame,
            "Discord Bot Token",
            "DISCORD_BOT_TOKEN",
            "Discord 봇 토큰을 입력하세요",
        )

        # Channel IDs
        self.create_text_field(
            frame,
            "Channel IDs (쉼표로 구분)",
            "DISCORD_CHANNEL_IDS",
            "예: 123456789,987654321",
        )

    def create_email_tab(self, parent):
        """Email 탭 생성"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # SMTP Server
        self.create_text_field(
            frame,
            "SMTP 서버",
            "SMTP_SERVER",
            "예: smtp.gmail.com",
        )

        # SMTP Port
        self.create_text_field(
            frame,
            "SMTP 포트",
            "SMTP_PORT",
            "예: 587",
        )

        # Sender Email
        self.create_text_field(
            frame,
            "발신자 이메일",
            "SENDER_EMAIL",
            "예: your-email@gmail.com",
        )

        # Sender Password
        self.create_password_field(
            frame,
            "발신자 비밀번호 (앱 비밀번호)",
            "SENDER_PASSWORD",
            "Gmail 앱 비밀번호를 입력하세요",
        )

    def create_github_tab(self, parent):
        """GitHub 탭 생성"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # GitHub Token
        self.create_password_field(
            frame,
            "GitHub Token (API 제한 해제용)",
            "GITHUB_TOKEN",
            "GitHub Personal Access Token",
        )

        # GitHub Profile URL
        self.create_text_field(
            frame,
            "GitHub 프로필 URL",
            "GITHUB_PROFILE_URL",
            "예: https://github.com/username",
        )

        # 안내 문구
        info_label = ctk.CTkLabel(
            frame,
            text="※ 스킬 갭 분석 시 사용됩니다",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        info_label.pack(anchor="w", pady=(0, 10))

    def create_text_field(
        self, parent, label: str, key: str, placeholder: str = ""
    ):
        """텍스트 입력 필드 생성"""
        label_widget = ctk.CTkLabel(
            parent,
            text=label,
            font=ctk.CTkFont(size=13),
            anchor="w",
        )
        label_widget.pack(fill="x", pady=(10, 2))

        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            height=35,
            font=ctk.CTkFont(size=13),
        )
        entry.pack(fill="x", pady=(0, 5))

        self.entries[key] = entry

    def create_password_field(
        self, parent, label: str, key: str, placeholder: str = ""
    ):
        """비밀번호 입력 필드 생성 (표시/숨김 토글)"""
        label_widget = ctk.CTkLabel(
            parent,
            text=label,
            font=ctk.CTkFont(size=13),
            anchor="w",
        )
        label_widget.pack(fill="x", pady=(10, 2))

        # 입력 필드 + 버튼 프레임
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")
        field_frame.pack(fill="x", pady=(0, 5))

        entry = ctk.CTkEntry(
            field_frame,
            placeholder_text=placeholder,
            height=35,
            font=ctk.CTkFont(size=13),
            show="*",
        )
        entry.pack(side="left", fill="x", expand=True)

        # 표시/숨김 토글 버튼
        self.show_password_vars[key] = False
        toggle_btn = ctk.CTkButton(
            field_frame,
            text="표시",
            width=50,
            height=35,
            command=lambda e=entry, k=key: self.toggle_password_visibility(e, k),
        )
        toggle_btn.pack(side="right", padx=(5, 0))

        self.entries[key] = entry

    def toggle_password_visibility(self, entry: ctk.CTkEntry, key: str):
        """비밀번호 표시/숨김 토글"""
        self.show_password_vars[key] = not self.show_password_vars[key]
        if self.show_password_vars[key]:
            entry.configure(show="")
        else:
            entry.configure(show="*")

    def load_existing_config(self):
        """기존 설정 로드"""
        config = self.config_manager.get_all()
        for key, entry in self.entries.items():
            value = config.get(key, "")
            if value:
                entry.delete(0, "end")
                entry.insert(0, value)

    def save_config(self):
        """설정 저장"""
        # 입력값 수집
        config = {}
        for key, entry in self.entries.items():
            config[key] = entry.get().strip()

        # 유효성 검사
        errors = self.config_manager.validate_config(config)
        if errors:
            self.show_error("\n".join(errors))
            return

        # 저장
        if self.config_manager.save_config(config):
            self.show_success("설정이 저장되었습니다.")
            if self.on_save_callback:
                self.destroy()
                self.on_save_callback()
        else:
            self.show_error("설정 저장에 실패했습니다.")

    def on_cancel(self):
        """취소 버튼 클릭"""
        self.destroy()

    def show_error(self, message: str):
        """에러 메시지 표시"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("오류")
        dialog.geometry("400x150")
        dialog.resizable(False, False)
        dialog.grab_set()

        # 메시지 중앙에 위치
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

    def show_success(self, message: str):
        """성공 메시지 표시"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("완료")
        dialog.geometry("300x120")
        dialog.resizable(False, False)
        dialog.grab_set()

        # 메시지 중앙에 위치
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 300) // 2
        y = self.winfo_y() + (self.winfo_height() - 120) // 2
        dialog.geometry(f"+{x}+{y}")

        label = ctk.CTkLabel(
            dialog,
            text=message,
            font=ctk.CTkFont(size=13),
        )
        label.pack(expand=True, padx=20, pady=20)

        btn = ctk.CTkButton(
            dialog,
            text="확인",
            command=dialog.destroy,
            width=100,
        )
        btn.pack(pady=(0, 20))
