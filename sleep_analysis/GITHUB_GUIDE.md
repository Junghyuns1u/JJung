# GitHub 업로드 가이드

## 방법 1: GitHub Desktop 사용 (초보자 추천)

1. **GitHub Desktop 설치**
   - https://desktop.github.com/ 에서 다운로드

2. **GitHub 계정 연결**
   - File → Options → Sign in

3. **저장소 생성**
   - File → New Repository
   - Name: `sleep-pattern-analysis`
   - Local Path: `sleep_analysis` 폴더 선택
   - Initialize with README: 체크 해제 (이미 있음)

4. **커밋 및 푸시**
   - 변경사항 확인
   - Summary 입력: "Initial commit: 수면 패턴 분석 프로젝트"
   - "Commit to main" 클릭
   - "Publish repository" 클릭
   - Public/Private 선택

## 방법 2: 명령줄 사용

```bash
# 1. sleep_analysis 폴더로 이동
cd sleep_analysis

# 2. Git 초기화
git init

# 3. 파일 추가
git add .

# 4. 첫 커밋
git commit -m "Initial commit: 수면 패턴 분석 프로젝트"

# 5. GitHub에 새 저장소 생성 (웹에서)
# https://github.com/new
# Repository name: sleep-pattern-analysis

# 6. 원격 저장소 연결
git remote add origin https://github.com/YOUR_USERNAME/sleep-pattern-analysis.git

# 7. 푸시
git branch -M main
git push -u origin main
```

## 방법 3: VS Code에서 직접

1. **소스 제어 탭 열기** (Ctrl+Shift+G)
2. **"Initialize Repository" 클릭**
3. **파일 스테이징**: 변경사항 옆 + 버튼
4. **커밋 메시지 입력**: "Initial commit"
5. **커밋** (✓ 버튼)
6. **"Publish to GitHub" 클릭**
7. Repository name 입력 및 Public/Private 선택

## 저장소 설정 (Optional)

### README.md 상단에 배지 추가

```markdown
![Python](https://img.shields.io/badge/Python-3.7+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)
```

### Topics 추가

GitHub 저장소 페이지에서:
- Settings → Topics
- 추가 추천: `sleep-analysis`, `python`, `data-science`, `health`, `research`

### About 섹션 작성

```
스마트폰 소리 센서로 수면 패턴을 분석하는 과학 탐구 프로젝트
```

## 업데이트 하기

```bash
# 변경사항 확인
git status

# 파일 추가
git add .

# 커밋
git commit -m "Update: 분석 결과 추가"

# 푸시
git push
```

## .gitignore 확인사항

개인정보가 포함된 파일은 업로드하지 마세요:
- ✅ 샘플 데이터는 OK
- ❌ 실제 수면 데이터 (개인정보)
- ❌ 실제 실험 기록 (개인 일정)

필요시 `.gitignore`에 추가:
```
data/*_real_*.csv
data/my_*.csv
```

## 저장소 공개 여부

### Private (비공개) 추천 시
- 실제 개인 데이터를 포함하는 경우
- 학교 과제 제출 전까지
- 실험 진행 중

### Public (공개) 추천 시
- 포트폴리오로 활용
- 다른 학생들과 공유
- 오픈소스 기여

## 협업하기 (Optional)

팀 프로젝트인 경우:

1. **Settings → Collaborators**
2. **팀원 GitHub ID 입력**
3. **Add collaborator**

팀원은 이메일 초대를 수락 후:
```bash
git clone https://github.com/YOUR_USERNAME/sleep-pattern-analysis.git
cd sleep-pattern-analysis
```

## 문제 해결

### Large files 오류
```bash
# 100MB 이상 파일 제거
git rm --cached large_file.csv
git commit -m "Remove large file"
```

### Push 거부 오류
```bash
# 원격 변경사항 먼저 가져오기
git pull origin main --rebase
git push
```

## 최종 체크리스트

- [ ] README.md 작성 완료
- [ ] .gitignore 설정
- [ ] 개인정보 제거 확인
- [ ] 코드 테스트 완료
- [ ] 주석 및 문서화 완료
- [ ] 저장소 이름 확인
- [ ] Public/Private 선택
- [ ] Topics 추가
- [ ] License 선택 (MIT 추천)
