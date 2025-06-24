"""
LangChain 프롬프트 템플릿 정의 모듈
"""

from langchain_core.prompts import PromptTemplate


class JobSummaryTemplate:
    """채용공고 요약용 프롬프트 템플릿 클래스"""

    @staticmethod
    def get_summary_template() -> PromptTemplate:
        """채용공고 요약용 프롬프트 템플릿 반환"""
        template = """다음 채용 공고 내용을 핵심 정보만 정리하여 한글로 요약해 주세요:

{job_content}

아래 형식으로 정리해주세요:

## 공고명: [공고명]
### 회사명: [회사명]

**마감기한**
- [마감기한]

### A. 회사소개 (비전, 연혁) & 직무 소개 (주요 업무):
- [회사 소개 및 주요 업무 내용]

### B. 자격요건 (필수조건) & 우대사항 (선택 요건):
**필수조건:**
- [필수 자격요건들]

**우대사항:**
- [우대사항들]

### C. 혜택 및 복지 & 기타사항:
- [혜택, 복지, 기타 정보들]
"""
        return PromptTemplate(input_variables=["job_content"], template=template)
    
    @staticmethod
    def get_map_template() -> PromptTemplate:
        """Map 단계용 프롬프트 템플릿 - 각 청크 요약"""
        template = """다음 채용공고 텍스트의 핵심 내용을 간단히 요약해주세요.
영어 내용이 있다면 한국어로 번역해서 요약해주세요:

{text}

핵심 요약:"""
        return PromptTemplate(input_variables=["text"], template=template)
    
    @staticmethod
    def get_reduce_template() -> PromptTemplate:
        """Reduce 단계용 프롬프트 템플릿 - 최종 통합 요약"""
        template = """다음은 채용공고의 여러 부분을 요약한 내용들입니다.
이를 종합하여 완전한 채용공고 요약을 만들어주세요:

{text}

아래 형식으로 최종 정리해주세요:

## 공고명: [공고명]
### 회사명: [회사명]

**마감기한**
- [마감기한]

### A. 회사소개 (비전, 연혁) & 직무 소개 (주요 업무):
- [회사 소개 및 주요 업무 내용]

### B. 자격요건 (필수조건) & 우대사항 (선택 요건):
**필수조건:**
- [필수 자격요건들]

**우대사항:**
- [우대사항들]

### C. 혜택 및 복지 & 기타사항:
- [혜택, 복지, 기타 정보들]
"""
        return PromptTemplate(input_variables=["text"], template=template)

    @staticmethod
    def get_custom_template(custom_format: str) -> PromptTemplate:
        """커스텀 포맷의 프롬프트 템플릿 반환"""
        template = f"""다음 채용 공고 내용을 핵심 정보만 정리하여 요약해 주세요:

{{job_content}}

{custom_format}
"""
        return PromptTemplate(input_variables=["job_content"], template=template)
