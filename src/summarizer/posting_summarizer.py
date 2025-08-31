from typing import Optional, Tuple

from src.langchain.chain import JobSummaryChain
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

def _slugify(value: str, max_length: int = 80) -> str:
    allowed = []
    for ch in value.lower().strip():
        if ch.isalnum():
            allowed.append(ch)
        elif ch in [" ", "-", "_"]:
            allowed.append("_")
    slug = "".join(allowed)
    while "__" in slug:
        slug = slug.replace("__", "_")
    slug = slug.strip("_")
    return slug[:max_length] or "job_posting"


class JobPostingSummarizer:
    def __init__(
        self, content: str, model_name: str = "gpt-oss:20b", temperature: float = 0.1
    ):
        """채용공고 요약기 초기화"""
        self.chain = JobSummaryChain(model_name=model_name, temperature=temperature)
        self.content = content

    def summarize_job_posting(self, content: str, verbose: bool = False) -> str:
        """채용공고 내용 요약 (토큰 제한 자동 처리)"""
        try:
            result = self.chain.run_summary(content, verbose=verbose)
            return result
        except Exception as e:
            raise Exception(f"요약 처리 실패: {e}")

    def save_summary(self, summary: str, filename: Optional[str] = None) -> str:
        """요약 결과를 파일로 저장"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            t_slug, c_slug = self._extract_title_company(summary)
            mid = f"{c_slug}_{t_slug}".strip("_") or "job_posting"
            filename = f"job_posting_{mid}_{timestamp}.md"

        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        file_path = output_dir / filename

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(summary)
            return str(file_path)
        except Exception as e:
            raise Exception(f"파일 저장 실패: {e}")

    def _extract_title_company(self, summary: str) -> Tuple[str, str]:
        title = ""
        company = ""
        for line in summary.splitlines():
            txt = line.strip()
            if not title and (
                txt.startswith("## 공고명:") or txt.startswith("## 공고명 :")
            ):
                title = txt.split(":", 1)[-1].strip()
            if not company and (
                txt.startswith("### 회사명:") or txt.startswith("### 회사명 :")
            ):
                company = txt.split(":", 1)[-1].strip()
            if title and company:
                break
        return _slugify(title), _slugify(company)