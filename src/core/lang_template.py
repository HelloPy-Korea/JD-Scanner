"""
LangChain 프롬프트 템플릿 정의 모듈
- 채용공고 요약 템플릿
- 스킬 갭 분석 템플릿
- 면접 질문 생성 템플릿
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


class SkillGapTemplate:
    """스킬 갭 분석 및 면접 질문 생성용 프롬프트 템플릿 클래스"""

    @staticmethod
    def get_skill_gap_template() -> PromptTemplate:
        """기술 갭 분석 프롬프트 템플릿"""
        template = """당신은 채용 전문가이자 기술 면접관입니다.
다음 채용공고 요구사항과 지원자의 GitHub 프로필을 비교 분석해주세요.

## 채용공고 요구사항:
{job_requirements}

## 지원자 GitHub 프로필:
{github_profile}

아래 형식으로 분석해주세요:

### 1. 기술 스킬 매칭 분석

**일치하는 기술:**
- [지원자가 보유하고 있으며 채용공고에서 요구하는 기술들]

**부족한 필수 기술:**
- [채용공고에서 요구하지만 지원자의 GitHub에서 확인되지 않는 기술들]

**지원자의 추가 기술:**
- [채용공고에서 요구하지 않지만 지원자가 보유한 관련 기술들]

### 2. 프로젝트 경험 분석
- [GitHub 프로젝트들이 채용공고의 업무와 얼마나 관련이 있는지 분석]

### 3. 기술 성숙도 평가
- [언어별, 프레임워크별 사용 빈도와 프로젝트 규모 기반 평가]

### 4. 종합 매칭 점수
- **점수:** [0-100점]
- **평가:** [간단한 종합 평가]
"""
        return PromptTemplate(
            input_variables=["job_requirements", "github_profile"],
            template=template,
        )

    @staticmethod
    def get_interview_questions_template_ko() -> PromptTemplate:
        """한국어 면접 질문 생성 프롬프트 템플릿"""
        template = """당신은 시니어 기술 면접관입니다.
다음 기술 갭 분석 결과를 바탕으로 지원자에게 맞춤화된 면접 질문을 생성해주세요.

## 기술 갭 분석 결과:
{skill_gap_analysis}

## 지원 직무: {job_title}

## 지원자 보유 기술: {candidate_technologies}

아래 카테고리별로 면접 질문을 생성해주세요:

### A. 부족한 기술에 대한 질문 (3-5개)
[요구되는 기술을 사용하지 않은 이유, 학습 계획 등을 확인하는 질문]

1. **질문:** [질문 내용]
   **의도:** [이 질문을 통해 확인하고자 하는 것]
   **좋은 답변 예시:** [면접관이 기대하는 답변 방향]

### B. 대안 기술 선택에 대한 질문 (2-3개)
[지원자가 선택한 기술 스택에 대한 이유와 장단점을 확인하는 질문]

### C. 기술 갭 극복 계획 질문 (2-3개)
[부족한 기술을 어떻게 빠르게 습득할 것인지 확인하는 질문]

### D. 프로젝트 심화 질문 (2-3개)
[GitHub 프로젝트 경험을 바탕으로 한 기술적 깊이를 확인하는 질문]

### E. 실제 업무 시나리오 질문 (2개)
[채용공고의 업무를 수행한다고 가정했을 때의 문제 해결 접근 방식 질문]
"""
        return PromptTemplate(
            input_variables=["skill_gap_analysis", "job_title", "candidate_technologies"],
            template=template,
        )

    @staticmethod
    def get_interview_questions_template_en() -> PromptTemplate:
        """영어 면접 질문 생성 프롬프트 템플릿"""
        template = """You are a senior technical interviewer.
Based on the following skill gap analysis, generate personalized interview questions for the candidate.

## Skill Gap Analysis:
{skill_gap_analysis}

## Target Position: {job_title}

## Candidate's Technologies: {candidate_technologies}

Generate interview questions for each category below:

### A. Questions About Missing Skills (3-5 questions)
[Questions about why required technologies weren't used, learning plans, etc.]

1. **Question:** [Question content]
   **Intent:** [What this question aims to verify]
   **Good Answer Example:** [Expected answer direction]

### B. Alternative Technology Choices (2-3 questions)
[Questions about why the candidate chose their tech stack and its pros/cons]

### C. Skill Gap Mitigation Plans (2-3 questions)
[Questions about how they plan to quickly learn missing skills]

### D. Project Deep-Dive Questions (2-3 questions)
[Questions exploring technical depth based on GitHub projects]

### E. Real-World Scenario Questions (2 questions)
[Problem-solving approach questions assuming they're doing the job's tasks]
"""
        return PromptTemplate(
            input_variables=["skill_gap_analysis", "job_title", "candidate_technologies"],
            template=template,
        )

    @staticmethod
    def get_requirements_extraction_template() -> PromptTemplate:
        """채용공고에서 요구사항 추출 프롬프트 템플릿"""
        template = """다음 채용공고 요약에서 기술 요구사항을 구조화된 형식으로 추출해주세요.

## 채용공고 요약:
{job_summary}

아래 JSON 형식으로만 출력해주세요 (다른 텍스트 없이 JSON만):
{{
    "job_title": "직무명",
    "required_languages": ["필수 프로그래밍 언어들"],
    "required_frameworks": ["필수 프레임워크들"],
    "required_tools": ["필수 도구/플랫폼들"],
    "preferred_skills": ["우대 기술들"],
    "experience_level": "신입/경력/무관",
    "key_responsibilities": ["주요 업무 내용들"]
}}
"""
        return PromptTemplate(
            input_variables=["job_summary"],
            template=template,
        )
