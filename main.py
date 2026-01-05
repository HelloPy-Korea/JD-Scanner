#!/usr/bin/env python3
"""
JD-Scanner - AI 기반 채용공고 분석 및 면접 준비 시스템
GUI 진입점
"""

import sys

from src.utils.config_manager import ConfigManager
from src.ui.main_ui import MainWindow
from src.ui.settings_ui import SettingsWindow


def launch_main_window():
    """메인 윈도우 실행"""
    app = MainWindow()
    app.mainloop()


def main():
    """메인 함수 - GUI 플로우"""
    try:
        # 설정 상태 확인
        config_manager = ConfigManager()

        # 설정 미완료 시 설정 화면 먼저 표시
        if not config_manager.is_configured():
            settings = SettingsWindow(on_save_callback=launch_main_window)
            settings.mainloop()
        else:
            # 설정 완료 시 바로 메인 화면 표시
            launch_main_window()

    except KeyboardInterrupt:
        print("\n사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
