"""
실제 데이터 빠른 분석 스크립트
"""

from sleep_analyzer import SleepAnalyzer

# 분석기 생성 (임계값 35dB로 조정)
analyzer = SleepAnalyzer(threshold_db=35)

# 실제 데이터 로드
print("실제 수면 데이터 분석 시작...\n")
analyzer.load_data('data/sleep_data_20251115.csv')

# 전처리
analyzer.preprocess_data()

# 통계 계산 및 출력
analyzer.calculate_statistics()
analyzer.print_statistics()

# 그래프 생성
print("\n그래프 생성 중...")
analyzer.plot_data(save_path='results/real_sleep_analysis_20251115.png')

# 보고서 생성
analyzer.generate_report('Real_20251115')

print("\n✅ 분석 완료!")
print("results/ 폴더에서 그래프와 보고서를 확인하세요.")
