# 🎯 빠른 시작 가이드

## 1단계: 환경 설정

```bash
# 프로젝트 폴더로 이동
cd sleep_analysis

# 필요한 패키지 설치
pip install -r requirements.txt
```

## 2단계: 데이터 수집

### 📱 스마트폰 앱 추천

1. **Android**: 
   - Sound Meter (by Smart Tools co.)
   - dB Meter (by dB Meter Apps)
   - Physics Toolbox Sensor Suite

2. **iOS**:
   - dB Meter - measure sound level
   - Too Noisy
   - Decibel X

### 📊 데이터 수집 체크리스트

- [ ] 앱 설치 및 CSV 내보내기 기능 확인
- [ ] 측정 간격 5초로 설정
- [ ] 폰 위치 고정 (머리맡 30cm 이내)
- [ ] 충전기 연결 (배터리 부족 방지)
- [ ] 방해 금지 모드 설정
- [ ] 알람 볼륨 고정

### 🌙 실험 수행

#### 밤 (취침 전)
1. 실험 조건 확인 (A/B/C 중 선택)
2. 앱 실행 및 로그 시작
3. 폰 고정 위치에 배치
4. `experiment_log.csv`에 기록 준비
5. 취침

#### 아침 (기상 후)
1. 로그 종료
2. CSV 파일로 내보내기
3. 파일명 변경: `sleep_data_YYMMDD_조건.csv`
4. `data/` 폴더로 복사
5. 실험 기록 작성

## 3단계: 데이터 분석

### 📁 파일 배치

```
sleep_analysis/
├── data/
│   ├── experiment_log.csv          # 실험 기록 작성
│   ├── sample_sleep_data_A.csv     # 조건 A 데이터
│   ├── sample_sleep_data_B.csv     # 조건 B 데이터
│   └── sample_sleep_data_C.csv     # 조건 C 데이터
```

### 🔍 단일 조건 분석

```bash
# sleep_analyzer.py 파일 수정
# 26번째 줄: data_file 경로 변경
data_file = 'data/sample_sleep_data_A.csv'  # 분석할 파일

# 실행
python sleep_analyzer.py
```

**출력물:**
- 통계 결과 (콘솔)
- 그래프: `results/sleep_analysis_A.png`
- 보고서: `results/report_A.txt`

### 📊 전체 가설 검증

```bash
python hypothesis_test.py
```

**출력물:**
- 조건별 비교 표 (콘솔)
- 가설 검증 결과 (콘솔)
- 비교 그래프: `results/condition_comparison.png`
- 최종 보고서: `results/hypothesis_test_report.txt`

## 4단계: 결과 해석

### 📈 주요 지표 이해

| 지표 | 의미 | 좋은 수면 | 나쁜 수면 |
|------|------|-----------|-----------|
| 소음 구간 비율 | 임계값 이상 비율 | < 1% | > 3% |
| 평균 dB | 전체 평균 음량 | 30-33 | > 35 |
| 연속 소음 구간 | 뒤척임 지속 시간 | < 10초 | > 20초 |
| 수면 초반 소음 | 입면 어려움 지표 | < 2% | > 5% |

### ✅ 가설 판정 기준

**가설 1**: 소음 구간이 관찰되는가?
- YES → 소음과 각성의 관계 확인

**가설 2**: 조건 B - 조건 A ≥ 5%p?
- YES → 가설 지지 (폰 사용이 수면 질 저하)
- NO → 가설 기각 (영향 미미 또는 표본 부족)

## 5단계: 보고서 작성

### 📝 탐구 보고서 구성

1. **서론**
   - 연구 동기 및 목적
   - 가설 제시

2. **이론적 배경**
   - 수면 단계와 소리의 관계
   - 스마트폰 사용과 수면의 관계
   - dB(데시벨) 단위 설명

3. **연구 방법**
   - 실험 설계 (조건 A/B/C)
   - 데이터 수집 방법
   - 분석 방법 (임계값, 통계 기법)

4. **연구 결과**
   - 조건별 측정 결과 표
   - 그래프 (시간-dB, 조건별 비교)
   - 통계 분석 결과

5. **논의**
   - 가설 검증 결과
   - 예상과 다른 점
   - 한계점

6. **결론**
   - 주요 발견
   - 수면 개선 제안
   - 후속 연구 방향

## 🔧 문제 해결

### CSV 파일 로드 오류

```python
# 인코딩 문제
df = pd.read_csv('data/myfile.csv', encoding='cp949')  # 또는 'euc-kr'

# 컬럼명 확인
print(df.columns)
```

### 그래프가 보이지 않음

```python
# Jupyter Notebook 사용 시
%matplotlib inline

# 그래프만 저장하고 표시 안 함
plt.savefig('output.png')
plt.close()
```

### 임계값 조정

```python
# 너무 높으면: 소음 구간이 거의 없음 (< 0.5%)
# 너무 낮으면: 대부분이 소음 구간 (> 10%)
# 추천: 35-45 dB 사이에서 실험

analyzer = SleepAnalyzer(threshold_db=38)
```

## 📚 참고 자료

### 수면과 소리 연구

- WHO 야간 소음 가이드라인: 40dB 이하 권장
- 수면 단계별 음향 민감도
- REM 수면과 각성 역치

### 스마트폰과 수면

- 블루라이트의 멜라토닌 억제 효과
- 디지털 각성과 수면 잠복기
- 수면 위생 가이드라인

## 🎓 학습 목표 달성 체크

- [ ] 소리 센서의 원리 이해 (마이크, dB 측정)
- [ ] 데이터 수집 및 전처리 경험
- [ ] Python 프로그래밍 능력 향상
- [ ] 통계 분석 기법 이해 (평균, 표준편차, 상관계수)
- [ ] 과학적 가설 검증 방법 습득
- [ ] 데이터 시각화 기술 습득
- [ ] 자신의 수면 패턴 이해

## 💡 추가 실험 아이디어

1. **온도와 수면**: 실내 온도 변화 기록
2. **조명과 수면**: 조명 상태(암막 vs 일반) 비교
3. **운동과 수면**: 운동 시간대별 비교
4. **카페인과 수면**: 섭취 시간별 영향 분석
5. **주말 vs 평일**: 수면 패턴 차이

## 🤝 도움이 필요하면

- 코드 오류: 오류 메시지 전체를 복사해서 검색
- 데이터 문제: `data/` 폴더의 CSV 파일 확인
- 분석 해석: 교사 또는 멘토에게 문의
