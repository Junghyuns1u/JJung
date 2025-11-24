"""
가설 검증 및 조건별 비교 분석
조건 A(평소), B(취침 전 폰 사용), C(폰 사용 최소) 비교
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import os
from sleep_analyzer import SleepAnalyzer


class HypothesisTest:
    """가설 검증 클래스"""
    
    def __init__(self, threshold_db=40):
        self.threshold_db = threshold_db
        self.results = {}
        self.condition_stats = {}
        
    def analyze_condition(self, csv_file, condition_name, experiment_info=None):
        """
        특정 조건의 데이터 분석
        
        Parameters:
        -----------
        csv_file : str
            CSV 파일 경로
        condition_name : str
            조건 이름 (A, B, C)
        experiment_info : dict, optional
            실험 정보 (폰 사용 시간 등)
        
        Returns:
        --------
        dict : 분석 결과
        """
        print(f"\n--- 조건 {condition_name} 분석 중 ---")
        
        analyzer = SleepAnalyzer(threshold_db=self.threshold_db)
        analyzer.load_data(csv_file)
        analyzer.preprocess_data()
        stats_result = analyzer.calculate_statistics()
        
        # 실험 정보 추가
        if experiment_info:
            stats_result['폰_사용_시간_분'] = experiment_info.get('폰사용시간(분)', 0)
            stats_result['게임_시간_분'] = experiment_info.get('게임시간(분)', 0)
        
        self.condition_stats[condition_name] = stats_result
        self.results[condition_name] = analyzer
        
        return stats_result
    
    def compare_conditions(self):
        """
        조건별 비교 분석
        
        Returns:
        --------
        pd.DataFrame : 비교 결과 테이블
        """
        if len(self.condition_stats) < 2:
            print("✗ 비교할 조건이 충분하지 않습니다 (최소 2개 필요)")
            return None
        
        # 결과를 DataFrame으로 변환
        comparison_df = pd.DataFrame(self.condition_stats).T
        
        # 주요 지표만 선택
        key_metrics = [
            '소음_구간_비율_%',
            '평균_dB',
            '최대_dB',
            '연속_소음_구간_평균_길이_초',
            '수면초반1시간_소음비율_%',
            '폰_사용_시간_분'
        ]
        
        available_metrics = [m for m in key_metrics if m in comparison_df.columns]
        comparison_df = comparison_df[available_metrics]
        
        print("\n" + "="*80)
        print("조건별 비교 결과")
        print("="*80)
        print(comparison_df.to_string())
        print("="*80 + "\n")
        
        return comparison_df
    
    def test_hypothesis1(self):
        """
        가설1 검증: 수면 중 dB 값이 높은 구간은 뒤척임·각성 가능성이 높다
        
        Returns:
        --------
        dict : 검증 결과
        """
        print("\n" + "="*80)
        print("가설 1 검증: dB 값과 각성 가능성")
        print("="*80)
        
        results = {
            '가설': '수면 중 dB 값이 높은 구간은 뒤척임·각성 가능성이 높다',
            '검증_방법': f'임계값({self.threshold_db}dB) 이상 구간을 소음/각성 구간으로 분류',
            '조건별_소음비율': {}
        }
        
        for condition, stats in self.condition_stats.items():
            noise_ratio = stats['소음_구간_비율_%']
            results['조건별_소음비율'][condition] = noise_ratio
            print(f"조건 {condition}: 소음 구간 비율 = {noise_ratio:.2f}%")
        
        # 평균 소음 비율
        avg_noise_ratio = np.mean(list(results['조건별_소음비율'].values()))
        results['평균_소음비율_%'] = avg_noise_ratio
        
        print(f"\n평균 소음 구간 비율: {avg_noise_ratio:.2f}%")
        print(f"→ 임계값({self.threshold_db}dB) 이상 구간이 수면 중 약 {avg_noise_ratio:.1f}% 발생")
        print("\n결론: 소음 구간(높은 dB)이 일정 비율로 관찰되며,")
        print("      이는 뒤척임이나 각성과 관련이 있을 것으로 추정됩니다.")
        print("="*80 + "\n")
        
        return results
    
    def test_hypothesis2(self, significance_threshold=5.0):
        """
        가설2 검증: 취침 전 스마트폰/게임 시간이 길수록 소음 구간 비율이 증가
        
        Parameters:
        -----------
        significance_threshold : float
            유의미한 차이로 간주할 임계값 (기본값: 5%p)
        
        Returns:
        --------
        dict : 검증 결과
        """
        print("\n" + "="*80)
        print("가설 2 검증: 취침 전 폰 사용과 소음 구간의 관계")
        print("="*80)
        
        # 데이터 추출
        phone_times = []
        noise_ratios = []
        
        for condition, stats in self.condition_stats.items():
            if '폰_사용_시간_분' in stats:
                phone_times.append(stats['폰_사용_시간_분'])
                noise_ratios.append(stats['소음_구간_비율_%'])
                print(f"조건 {condition}: 폰 사용 {stats['폰_사용_시간_분']}분 → "
                      f"소음 비율 {stats['소음_구간_비율_%']:.2f}%")
        
        results = {
            '가설': '취침 전 스마트폰/게임 시간이 길수록 소음 구간 비율이 증가한다',
            '검증_기준': f'조건별 소음 비율 차이가 {significance_threshold}%p 이상이면 가설 지지',
            '데이터': {
                '폰_사용_시간_분': phone_times,
                '소음_구간_비율_%': noise_ratios
            }
        }
        
        # 상관계수 계산 (피어슨)
        if len(phone_times) >= 2:
            from scipy.stats import pearsonr
            correlation, p_value = pearsonr(phone_times, noise_ratios)
            results['피어슨_상관계수'] = correlation
            results['p_value'] = p_value
            
            print(f"\n피어슨 상관계수 (r): {correlation:.3f}")
            print(f"p-value: {p_value:.3f}")
            
            if p_value < 0.05:
                print("→ 통계적으로 유의미한 상관관계가 있습니다 (p < 0.05)")
            else:
                print("→ 통계적으로 유의미하지 않습니다 (p ≥ 0.05)")
                print("  (표본 크기가 작아 유의성이 낮을 수 있음)")
        
        # 조건 A와 B 비교
        if 'A' in self.condition_stats and 'B' in self.condition_stats:
            noise_A = self.condition_stats['A']['소음_구간_비율_%']
            noise_B = self.condition_stats['B']['소음_구간_비율_%']
            difference = noise_B - noise_A
            
            results['조건A_소음비율'] = noise_A
            results['조건B_소음비율'] = noise_B
            results['차이_%p'] = difference
            
            print(f"\n조건 A(평소) vs 조건 B(취침 전 2시간 폰 사용)")
            print(f"  조건 A 소음 비율: {noise_A:.2f}%")
            print(f"  조건 B 소음 비율: {noise_B:.2f}%")
            print(f"  차이: {difference:+.2f}%p")
            
            if abs(difference) >= significance_threshold:
                print(f"\n결론: 차이가 {significance_threshold}%p 이상이므로 가설2를 지지합니다.")
                results['가설_판정'] = '지지'
            else:
                print(f"\n결론: 차이가 {significance_threshold}%p 미만이므로 가설2를 기각합니다.")
                results['가설_판정'] = '기각'
        
        print("="*80 + "\n")
        
        return results
    
    def plot_comparison(self, save_path=None):
        """
        조건별 비교 그래프
        
        Parameters:
        -----------
        save_path : str, optional
            그래프 저장 경로
        """
        if len(self.condition_stats) < 2:
            print("✗ 비교할 조건이 충분하지 않습니다")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        conditions = list(self.condition_stats.keys())
        
        # 1. 소음 구간 비율 비교
        noise_ratios = [self.condition_stats[c]['소음_구간_비율_%'] for c in conditions]
        axes[0, 0].bar(conditions, noise_ratios, color=['green', 'orange', 'blue'])
        axes[0, 0].set_ylabel('Noise Ratio (%)')
        axes[0, 0].set_title('Noise Ratio by Condition')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. 평균 dB 비교
        avg_dbs = [self.condition_stats[c]['평균_dB'] for c in conditions]
        axes[0, 1].bar(conditions, avg_dbs, color=['green', 'orange', 'blue'])
        axes[0, 1].set_ylabel('Average dB')
        axes[0, 1].set_title('Average Sound Level by Condition')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. 폰 사용 시간 vs 소음 비율 (산점도)
        phone_times = []
        noise_ratios_scatter = []
        for c in conditions:
            if '폰_사용_시간_분' in self.condition_stats[c]:
                phone_times.append(self.condition_stats[c]['폰_사용_시간_분'])
                noise_ratios_scatter.append(self.condition_stats[c]['소음_구간_비율_%'])
        
        if phone_times:
            axes[1, 0].scatter(phone_times, noise_ratios_scatter, s=100, alpha=0.7)
            for i, c in enumerate(conditions):
                if '폰_사용_시간_분' in self.condition_stats[c]:
                    axes[1, 0].annotate(c, (phone_times[i], noise_ratios_scatter[i]),
                                       xytext=(5, 5), textcoords='offset points')
            
            # 추세선
            if len(phone_times) >= 2:
                z = np.polyfit(phone_times, noise_ratios_scatter, 1)
                p = np.poly1d(z)
                x_line = np.linspace(min(phone_times), max(phone_times), 100)
                axes[1, 0].plot(x_line, p(x_line), "r--", alpha=0.5, label='Trend')
            
            axes[1, 0].set_xlabel('Phone Usage Time (min)')
            axes[1, 0].set_ylabel('Noise Ratio (%)')
            axes[1, 0].set_title('Phone Usage vs Noise Ratio')
            axes[1, 0].grid(True, alpha=0.3)
            axes[1, 0].legend()
        
        # 4. 수면 초반 1시간 소음 비율
        first_hour_ratios = [self.condition_stats[c]['수면초반1시간_소음비율_%'] for c in conditions]
        axes[1, 1].bar(conditions, first_hour_ratios, color=['green', 'orange', 'blue'])
        axes[1, 1].set_ylabel('Noise Ratio (%)')
        axes[1, 1].set_title('First Hour Noise Ratio by Condition')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ 비교 그래프 저장: {save_path}")
        
        plt.show()
    
    def generate_final_report(self, save_path='results/hypothesis_test_report.txt'):
        """
        최종 가설 검증 보고서 생성
        
        Parameters:
        -----------
        save_path : str
            보고서 저장 경로
        """
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("수면 패턴 분석 - 가설 검증 최종 보고서\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"분석 일시: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"임계값 설정: {self.threshold_db} dB\n")
            f.write(f"분석 조건 수: {len(self.condition_stats)}개\n\n")
            
            # 조건별 요약
            f.write("--- 조건별 측정 결과 ---\n\n")
            for condition, stats in self.condition_stats.items():
                f.write(f"[조건 {condition}]\n")
                f.write(f"  총 측정 시간: {stats['총_측정_시간_분']:.1f}분\n")
                f.write(f"  소음 구간 비율: {stats['소음_구간_비율_%']:.2f}%\n")
                f.write(f"  평균 dB: {stats['평균_dB']:.2f}\n")
                f.write(f"  최대 dB: {stats['최대_dB']:.2f}\n")
                if '폰_사용_시간_분' in stats:
                    f.write(f"  취침 전 폰 사용: {stats['폰_사용_시간_분']}분\n")
                f.write("\n")
            
            # 가설 검증 결과
            f.write("\n--- 가설 검증 결과 ---\n\n")
            
            # 가설 1
            h1_result = self.test_hypothesis1()
            f.write(f"[가설 1] {h1_result['가설']}\n")
            f.write(f"  평균 소음 구간 비율: {h1_result['평균_소음비율_%']:.2f}%\n")
            f.write(f"  → 소음 구간이 관찰되며, 각성/뒤척임과 관련 가능성 추정\n\n")
            
            # 가설 2
            h2_result = self.test_hypothesis2()
            f.write(f"[가설 2] {h2_result['가설']}\n")
            if '피어슨_상관계수' in h2_result:
                f.write(f"  피어슨 상관계수: {h2_result['피어슨_상관계수']:.3f}\n")
                f.write(f"  p-value: {h2_result['p_value']:.3f}\n")
            if '가설_판정' in h2_result:
                f.write(f"  판정: {h2_result['가설_판정']}\n")
                f.write(f"  조건 A-B 차이: {h2_result['차이_%p']:+.2f}%p\n")
            
            f.write("\n" + "="*80 + "\n")
        
        print(f"✓ 최종 보고서 저장: {save_path}")


def main():
    """메인 실행 함수"""
    print("\n" + "="*80)
    print("수면 패턴 분석 - 가설 검증 프로그램")
    print("="*80 + "\n")
    
    # 가설 검증 객체 생성
    tester = HypothesisTest(threshold_db=40)
    
    # 실험 기록 로드
    experiment_log_file = 'data/experiment_log.csv'
    if os.path.exists(experiment_log_file):
        exp_log = pd.read_csv(experiment_log_file, encoding='utf-8')
        print("✓ 실험 기록 로드 완료\n")
    else:
        exp_log = None
        print("! 실험 기록 파일이 없습니다. 기본 분석만 수행합니다.\n")
    
    # 조건별 데이터 분석
    conditions = ['A', 'B', 'C']
    
    for condition in conditions:
        data_file = f'data/sample_sleep_data_{condition}.csv'
        
        if os.path.exists(data_file):
            # 실험 정보 추출
            exp_info = None
            if exp_log is not None:
                exp_row = exp_log[exp_log['조건'] == condition]
                if not exp_row.empty:
                    exp_info = exp_row.iloc[0].to_dict()
            
            tester.analyze_condition(data_file, condition, exp_info)
        else:
            print(f"✗ 파일을 찾을 수 없습니다: {data_file}")
    
    # 조건별 비교
    if len(tester.condition_stats) >= 2:
        comparison_df = tester.compare_conditions()
        
        # 가설 검증
        h1_result = tester.test_hypothesis1()
        h2_result = tester.test_hypothesis2()
        
        # 비교 그래프
        tester.plot_comparison(save_path='results/condition_comparison.png')
        
        # 최종 보고서
        tester.generate_final_report()
        
        print("\n✓ 모든 분석 완료!")
    else:
        print("\n✗ 분석할 데이터가 충분하지 않습니다.")


if __name__ == "__main__":
    main()
