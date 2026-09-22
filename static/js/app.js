/**
 * AI Resume & Portfolio Builder - 브라우저 동작 스크립트 (app.js)
 */

document.addEventListener("DOMContentLoaded", () => {
    // 1. DOM 주요 요소(HTML 태그) 가져오기
    const resumeForm = document.getElementById("resume-form");
    const nameInput = document.getElementById("name");
    const jobTitleInput = document.getElementById("job-title");
    const toneSelect = document.getElementById("tone");
    const experienceInput = document.getElementById("experience");
    const projectsInput = document.getElementById("projects");

    const submitBtn = document.getElementById("submit-btn");
    const btnText = document.getElementById("btn-text");
    const btnSpinner = document.getElementById("btn-spinner");

    const errorBox = document.getElementById("error-box");
    const emptyState = document.getElementById("empty-state");
    const loadingState = document.getElementById("loading-state");
    const resultBox = document.getElementById("result-box");

    const resumeContent = document.getElementById("resume-content");
    const portfolioContent = document.getElementById("portfolio-content");

    const copyResumeBtn = document.getElementById("copy-resume-btn");
    const downloadResumeBtn = document.getElementById("download-resume-btn");
    const copyPortfolioBtn = document.getElementById("copy-portfolio-btn");
    const downloadPortfolioBtn = document.getElementById("download-portfolio-btn");

    // 원본 마크다운 텍스트 보관 변수 (복사 및 다운로드용)
    let currentResumeRaw = "";
    let currentPortfolioRaw = "";

    // 2. 오류 메시지 표시 함수
    function showError(message) {
        errorBox.textContent = message;
        errorBox.style.display = "block";
        errorBox.scrollIntoView({ behavior: "smooth", block: "center" });
    }

    // 3. 오류 메시지 숨김 함수
    function hideError() {
        errorBox.textContent = "";
        errorBox.style.display = "none";
    }

    // 4. 로딩 상태 전환 함수 (버튼 비활성화 및 스피너 제어)
    function setLoading(isLoading) {
        if (isLoading) {
            submitBtn.disabled = true;
            btnText.textContent = "AI가 작성 중입니다...";
            btnSpinner.style.display = "inline-block";

            emptyState.style.display = "none";
            resultBox.style.display = "none";
            loadingState.style.display = "block";
            hideError();
        } else {
            submitBtn.disabled = false;
            btnText.textContent = "✨ AI로 이력서 & 포트폴리오 생성하기";
            btnSpinner.style.display = "none";
            loadingState.style.display = "none";
        }
    }

    // 5. 폼 제출 이벤트 리스너 (생성 요청)
    resumeForm.addEventListener("submit", async (e) => {
        // 브라우저 기본 새로고침 동작 차단
        e.preventDefault();

        // 입력값 가져오기 및 공백 제거
        const name = nameInput.value.trim();
        const jobTitle = jobTitleInput.value.trim();
        const tone = toneSelect.value;
        const promptTypeRadio = document.querySelector('input[name="prompt_type"]:checked');
        const promptType = promptTypeRadio ? promptTypeRadio.value : "general";
        const experience = experienceInput.value.trim();
        const projects = projectsInput.value.trim();

        // 프론트엔드 입력값 1차 검증
        if (!name) {
            showError("이름을 입력해 주세요.");
            nameInput.focus();
            return;
        }

        if (!jobTitle) {
            showError("지원 직무를 입력해 주세요.");
            jobTitleInput.focus();
            return;
        }

        if (!experience) {
            showError("경력 사항을 입력해 주세요.");
            experienceInput.focus();
            return;
        }

        if (!projects) {
            showError("주요 프로젝트 경험을 입력해 주세요.");
            projectsInput.focus();
            return;
        }

        // 로딩 시작
        setLoading(true);

        try {
            // Flask 백엔드 /generate 엔드포인트로 비동기 POST 요청 전송
            const response = await fetch("/generate", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    name: name,
                    job_title: jobTitle,
                    tone: tone,
                    prompt_type: promptType,
                    experience: experience,
                    projects: projects
                })
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                // 서버에서 전달된 오류 메시지 출력
                throw new Error(data.error || "이력서 생성 중 서버 오류가 발생했습니다.");
            }

            // 생성 성공: 마크다운 렌더링 및 원본 보관
            currentResumeRaw = data.resume;
            currentPortfolioRaw = data.portfolio;

            if (typeof marked !== "undefined") {
                resumeContent.innerHTML = marked.parse(data.resume);
                portfolioContent.innerHTML = marked.parse(data.portfolio);
            } else {
                resumeContent.textContent = data.resume;
                portfolioContent.textContent = data.portfolio;
            }

            // 결과 영역 노출
            resultBox.style.display = "flex";
            emptyState.style.display = "none";

            // 결과 화면으로 부드럽게 스크롤
            resultBox.scrollIntoView({ behavior: "smooth", block: "start" });

        } catch (error) {
            console.error("생성 실패:", error);
            showError(error.message || "네트워크 연결 또는 서버에 문제가 발생했습니다.");
            emptyState.style.display = "block";
        } finally {
            // 로딩 종료
            setLoading(false);
        }
    });

    // 6. 클립보드 복사 헬퍼 함수
    async function copyToClipboard(text, buttonElement, defaultText) {
        if (!text) {
            alert("복사할 내용이 없습니다.");
            return;
        }

        try {
            await navigator.clipboard.writeText(text);
            buttonElement.textContent = "✅ 복사 완료!";
            buttonElement.classList.add("btn-success");

            setTimeout(() => {
                buttonElement.textContent = defaultText;
                buttonElement.classList.remove("btn-success");
            }, 2000);
        } catch (err) {
            console.error("클립보드 복사 실패:", err);
            alert("클립보드 복사에 실패했습니다. 직접 복사해 주세요.");
        }
    }

    // 이력서 복사 버튼
    copyResumeBtn.addEventListener("click", () => {
        copyToClipboard(currentResumeRaw, copyResumeBtn, "📋 복사");
    });

    // 포트폴리오 복사 버튼
    copyPortfolioBtn.addEventListener("click", () => {
        copyToClipboard(currentPortfolioRaw, copyPortfolioBtn, "📋 복사");
    });

    // 7. 마크다운(.md) 파일 다운로드 헬퍼 함수
    function downloadMarkdownFile(content, defaultFilename) {
        if (!content) {
            alert("다운로드할 내용이 없습니다.");
            return;
        }

        const applicantName = nameInput.value.trim() || "지원자";
        const filename = `${applicantName}_${defaultFilename}.md`;

        // 텍스트를 Blob 객체로 변환하여 다운로드 링크 생성
        const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
        const downloadUrl = URL.createObjectURL(blob);
        const link = document.createElement("a");

        link.href = downloadUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(downloadUrl);
    }

    // 이력서 .md 다운로드 버튼
    downloadResumeBtn.addEventListener("click", () => {
        downloadMarkdownFile(currentResumeRaw, "이력서");
    });

    // 포트폴리오 .md 다운로드 버튼
    downloadPortfolioBtn.addEventListener("click", () => {
        downloadMarkdownFile(currentPortfolioRaw, "포트폴리오");
    });
});
