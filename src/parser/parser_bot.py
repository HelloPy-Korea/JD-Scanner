# 기존에는 브라우저를 따라하는 형태로 헤더를 보냈지만
# 정확히 봇임을 명시하도록 수정
from bs4 import BeautifulSoup
from urllib3.util.retry import Retry

import re
import requests
from requests.adapters import HTTPAdapter


def _build_requests_session() -> requests.Session:
    """네트워크 요청 실패시 재요청 하는 함수"""
    session = requests.Session()
    retries = Retry(
        total=4,
        backoff_factor=0.8,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retries, pool_connections=10, pool_maxsize=10)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


# robots.txt 만족시키는 함수 추가해야함
class WebParser:
    def __init__(self, url: str):
        """웹페이지를 파싱하는 함수
        Args:
            url : 파싱하는 사이트의 url
        """
        self.url = url

    def extract_content_from_url(self) -> str:
        """채용 공고 추출"""
        try:
            # 헤더에 봇 명시 및 설명 url 추가 / github readme에 봇의 역할을 설명하는 부분 추가하기
            # 하루 특정 시간에 작동함과 전날과 비교의 역할 등을 설명
            headers = {
                "User-Agent": "HelloPY-Bot/1.0 (https://github.com/HelloPy-Korea/JD-Scanner)"
            }

            session = _build_requests_session()

            response = session.get(self.url, headers=headers, timeout=25)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            for script in soup(["script", "style"]):
                script.decompose()

            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            content = re.sub(r"\s+", " ", " ".join(lines)).strip()

            if not content.strip():
                raise ValueError("추출된 내용이 비어있습니다.")
            return content

        except requests.exceptions.RequestException as e:
            raise Exception(f"URL 요청 실패: {e}")
        except Exception as e:
            raise Exception(f"내용 추출 실패: {e}")
