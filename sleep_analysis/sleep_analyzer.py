"""
수면 패턴 분석 프로그램
소리 센서(dB) 데이터를 분석하여 수면 패턴을 평가합니다.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os

# 폰트 설정 (영문)
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False


class SleepAnalyzer:
    """수면 데이터 분석 클래스"""
    
    def __init__(self, threshold_db=40):
        """
        초기화
        
        Parameters:
        -----------
        threshold_db : float
            소음으로 간주할 dB 임계값 (기본값: 40dB)
        """
        self.threshold_db = threshold_db
        self.data = None
        self.stats = {}
        self.measurement_interval = 1  # 측정 간격 (초), 자동 계산됨
        
    def load_data(self, csv_file):
        """
        CSV 파일에서 수면 데이터 로드
        
        Parameters:
        -----------
        csv_file : str
            CSV 파일 경로 (형식: 시간,dB)
        
        Returns:
        --------
        pd.DataFrame : 로드된 데이터
        """
        try:
            df = pd.read_csv(csv_file, encoding='utf-8')
            
            # 컬럼명 정리
            df.columns = df.columns.str.strip()
            
            # 시간 컬럼을 datetime으로 변환
            if '시간' in df.columns:
                df['시간'] = pd.to_datetime(df['시간'], format='%H:%M:%S', errors='coerce')
            elif 'Time' in df.columns:
                df['시간'] = pd.to_datetime(df['Time'], format='%H:%M:%S', errors='coerce')
                
            # dB 컬럼 확인
            if 'dB' not in df.columns and 'Decibel' in df.columns:
                df.rename(columns={'Decibel': 'dB'}, inplace=True)
            
            # 측정 간격 자동 계산 (datetime 컬럼이 있는 경우)
            if '시간' in df.columns and len(df) > 1:
                try:
                    # 첫 두 레코드 간의 시간 차이 계산
                    time_diff = (df['시간'].iloc[1] - df['시간'].iloc[0]).total_seconds()
                    if time_diff > 0:
                        self.measurement_interval = time_diff
                    else:
                        self.measurement_interval = 1  # 기본값
                except:
                    self.measurement_interval = 1
            else:
                self.measurement_interval = 1
            
            self.data = df
            total_seconds = len(df) * self.measurement_interval
            print(f"✓ 데이터 로드 완료: {len(df)}개 레코드")
            print(f"  측정 간격: {self.measurement_interval}초")
            print(f"  측정 시간: {total_seconds/60:.1f}분 ({total_seconds/3600:.1f}시간)")
            
            return df
            
        except Exception as e:
            print(f"✗ 데이터 로드 실패: {e}")
            return None
    
    def preprocess_data(self, window_size=5):
        """
        데이터 전처리 및 노이즈 완화 (이동평균)
        
        Parameters:
        -----------
        window_size : int
            이동평균 윈도우 크기 (기본값: 5)
        """
        if self.data is None:
            print("✗ 먼저 데이터를 로드하세요.")
            return
        
        # 이동평균으로 노이즈 완화
        self.data['dB_smoothed'] = self.data['dB'].rolling(
            window=window_size, 
            center=True, 
            min_periods=1
        ).mean()
        
        # 소음 구간 표시 (임계값 기준)
        self.data['is_noise'] = self.data['dB'] >= self.threshold_db
        
        # REM 수면 추정 (낮은 dB + 약간의 변동성)
        # REM 수면: 평균보다 낮지만 완전히 조용하지는 않은 구간
        window_std = self.data['dB'].rolling(window=60, center=True, min_periods=1).std()
        avg_db = self.data['dB'].mean()
        self.data['is_rem'] = (self.data['dB'] < avg_db) & (window_std > 1.5) & (window_std < 4)
        
        print(f"✓ 전처리 완료 (이동평균 윈도우: {window_size})")
        
    def calculate_statistics(self):
        """
        수면 데이터 통계 계산
        
        Returns:
        --------
        dict : 통계 정보
        """
        if self.data is None:
            print("✗ 먼저 데이터를 로드하세요.")
            return None
        
        total_records = len(self.data)
        noise_records = self.data['is_noise'].sum()
        
        # 소음 구간 비율
        noise_ratio = (noise_records / total_records) * 100
        
        # 연속 소음 구간 분석
        consecutive_noise = []
        current_streak = 0
        
        for is_noise in self.data['is_noise']:
            if is_noise:
                current_streak += 1
            else:
                if current_streak > 0:
                    consecutive_noise.append(current_streak)
                current_streak = 0
        
        if current_streak > 0:
            consecutive_noise.append(current_streak)
        
        # 통계 저장
        total_seconds = total_records * self.measurement_interval
        self.stats = {
            '총_측정_횟수': total_records,
            '총_측정_시간_분': total_seconds / 60,
            '소음_구간_횟수': noise_records,
            '소음_구간_비율_%': noise_ratio,
            '평균_dB': self.data['dB'].mean(),
            '최대_dB': self.data['dB'].max(),
            '최소_dB': self.data['dB'].min(),
            '표준편차_dB': self.data['dB'].std(),
            '연속_소음_구간_평균_길이_초': np.mean(consecutive_noise) * self.measurement_interval if consecutive_noise else 0,
            '최장_연속_소음_구간_초': max(consecutive_noise) * self.measurement_interval if consecutive_noise else 0,
        }
        
        # REM 수면 비율 추가
        if 'is_rem' in self.data.columns:
            rem_records = self.data['is_rem'].sum()
            self.stats['REM_수면_비율_%'] = (rem_records / total_records) * 100
        
        # 수면 초반 1시간 분석
        first_hour_records = int(3600 / self.measurement_interval)  # 1시간 = 3600초
        first_hour_count = min(first_hour_records, total_records)
        first_hour_noise = self.data['is_noise'].iloc[:first_hour_count].sum()
        self.stats['수면초반1시간_소음비율_%'] = (first_hour_noise / first_hour_count) * 100
        
        # 시간대별 수면 품질 분석 (외부 연구 기반)
        # 연구 출처: Sleep Foundation, NIH Sleep Research
        # Deep sleep: < 30 dB (매우 조용한 수면)
        # Light sleep: 30-35 dB (조용한 수면, 뒤척임 없음)
        # Restless: 35-40 dB (뒤척임, 약한 움직임)
        # Disturbed: > 40 dB (자주 깨거나 큰 소음)
        
        deep_sleep = (self.data['dB'] < 30).sum()
        light_sleep = ((self.data['dB'] >= 30) & (self.data['dB'] < 35)).sum()
        restless = ((self.data['dB'] >= 35) & (self.data['dB'] < 40)).sum()
        disturbed = (self.data['dB'] >= 40).sum()
        
        self.stats['깊은수면_비율_%'] = (deep_sleep / total_records) * 100
        self.stats['얕은수면_비율_%'] = (light_sleep / total_records) * 100
        self.stats['뒤척임_비율_%'] = (restless / total_records) * 100
        self.stats['수면방해_비율_%'] = (disturbed / total_records) * 100
        
        # 시간대별 분석 (30분 단위)
        time_hours = np.arange(len(self.data)) * self.measurement_interval / 3600
        hourly_quality = []
        for hour in range(int(np.ceil(time_hours[-1]))):
            hour_mask = (time_hours >= hour) & (time_hours < hour + 1)
            if hour_mask.sum() > 0:
                hour_data = self.data.loc[hour_mask, 'dB']
                hourly_quality.append({
                    'hour': hour,
                    'avg_db': hour_data.mean(),
                    'deep_sleep_%': (hour_data < 30).sum() / len(hour_data) * 100,
                    'restless_%': ((hour_data >= 35) & (hour_data < 40)).sum() / len(hour_data) * 100
                })
        self.stats['시간대별_품질'] = hourly_quality
        
        return self.stats
    
    def print_statistics(self):
        """통계 정보 출력"""
        if not self.stats:
            self.calculate_statistics()
        
        print("\n" + "="*60)
        print("수면 데이터 분석 결과")
        print("="*60)
        
        for key, value in self.stats.items():
            key_korean = key.replace('_', ' ')
            if isinstance(value, float):
                print(f"{key_korean:30s}: {value:8.2f}")
            elif isinstance(value, list):
                # 리스트는 출력하지 않음 (시간대별 데이터 등)
                continue
            else:
                print(f"{key_korean:30s}: {value:8d}")
        
        print("="*60 + "\n")
    
    def plot_data(self, save_path=None):
        """
        데이터 시각화 (시간-dB 그래프)
        
        Parameters:
        -----------
        save_path : str, optional
            그래프 저장 경로
        """
        if self.data is None:
            print("✗ 먼저 데이터를 로드하세요.")
            return
        
        fig, ax = plt.subplots(figsize=(16, 7))
        
        # 시간 인덱스 생성 (시간 단위)
        time_hours = np.arange(len(self.data)) * self.measurement_interval / 3600
        
        # REM 수면 구간을 더 명확하게 표시
        if 'is_rem' in self.data.columns:
            rem_mask = self.data['is_rem'].values
            # 연속된 REM 구간 찾기
            in_rem = False
            rem_start = 0
            rem_count = 0
            for i in range(len(rem_mask)):
                if rem_mask[i] and not in_rem:
                    rem_start = time_hours[i]
                    in_rem = True
                elif not rem_mask[i] and in_rem:
                    # REM 구간 표시 (첫 번째만 라벨)
                    label = 'REM Sleep Period (estimated)' if rem_count == 0 else ''
                    ax.axvspan(rem_start, time_hours[i-1], alpha=0.12, color='mediumpurple', 
                              label=label, zorder=1)
                    rem_count += 1
                    in_rem = False
            # 마지막 구간 처리
            if in_rem:
                label = 'REM Sleep Period (estimated)' if rem_count == 0 else ''
                ax.axvspan(rem_start, time_hours[-1], alpha=0.12, color='mediumpurple', 
                          label=label, zorder=1)
        
        # 원본 데이터 플롯 (매우 투명)
        ax.plot(time_hours, self.data['dB'], 
                alpha=0.15, color='lightgray', label='Raw Data', linewidth=0.5, zorder=2)
        
        # 평활화된 데이터 플롯 (진한 파란색)
        if 'dB_smoothed' in self.data.columns:
            ax.plot(time_hours, self.data['dB_smoothed'], 
                    color='#2E86DE', label='Smoothed Data', linewidth=2.5, zorder=3)
        
        # 임계값 선
        ax.axhline(y=self.threshold_db, color='#EE5A6F', 
                   linestyle='--', label=f'Noise Threshold ({self.threshold_db}dB)', 
                   linewidth=2, alpha=0.8, zorder=4)
        
        # 소음 구간 강조
        noise_indices = self.data[self.data['is_noise']].index
        if len(noise_indices) > 0:
            ax.scatter(time_hours[noise_indices], 
                      self.data.loc[noise_indices, 'dB'],
                      color='#EE5A6F', s=20, alpha=0.7, label='Noise Events', 
                      zorder=5, edgecolors='darkred', linewidths=0.5)
        
        ax.set_xlabel('Time (hours)', fontsize=14, fontweight='bold')
        ax.set_ylabel('Sound Level (dB)', fontsize=14, fontweight='bold')
        ax.set_title('Sleep Sound Pattern Analysis', fontsize=17, fontweight='bold', pad=20)
        
        # 범례를 더 보기 좋게
        legend = ax.legend(loc='upper right', fontsize=11, framealpha=0.95, 
                          shadow=True, fancybox=True)
        legend.get_frame().set_facecolor('#F8F9FA')
        
        ax.grid(True, alpha=0.25, linestyle='--', linewidth=0.5)
        ax.set_facecolor('#FAFAFA')
        
        # x축 눈금을 1시간 단위로
        max_hours = int(np.ceil(time_hours[-1]))
        ax.set_xticks(np.arange(0, max_hours + 1, 1))
        
        # y축 범위 설정
        ax.set_ylim([self.data['dB'].min() - 5, self.data['dB'].max() + 5])
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ 그래프 저장: {save_path}")
        
        plt.show()
    
    def plot_additional_analysis(self, save_path=None):
        """
        Additional analysis graphs (histogram, boxplot, etc.)
        Based on sleep research: <30dB=deep sleep, 30-35dB=light sleep, 35-40dB=restless, >40dB=disturbed
        
        Parameters:
        -----------
        save_path : str, optional
            Path to save the graph
        """
        if self.data is None:
            print("✗ Load data first.")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.patch.set_facecolor('#FAFAFA')
        
        # 1. Histogram with sleep quality zones
        axes[0, 0].hist(self.data['dB'], bins=50, color='#2E86DE', edgecolor='black', alpha=0.7)
        axes[0, 0].axvline(30, color='green', linestyle='--', linewidth=2, label='Deep Sleep (<30dB)', alpha=0.8)
        axes[0, 0].axvline(35, color='orange', linestyle='--', linewidth=2, label='Restless (35dB)', alpha=0.8)
        axes[0, 0].axvline(40, color='red', linestyle='--', linewidth=2, label='Disturbed (40dB)', alpha=0.8)
        axes[0, 0].set_xlabel('Sound Level (dB)', fontsize=12, fontweight='bold')
        axes[0, 0].set_ylabel('Frequency', fontsize=12, fontweight='bold')
        axes[0, 0].set_title('Sound Level Distribution', fontsize=14, fontweight='bold')
        axes[0, 0].legend(fontsize=9)
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].set_facecolor('#FAFAFA')
        
        # 2. Boxplot
        bp = axes[0, 1].boxplot([self.data['dB']], labels=['Overall'], patch_artist=True)
        bp['boxes'][0].set_facecolor('#2E86DE')
        bp['boxes'][0].set_alpha(0.6)
        axes[0, 1].set_ylabel('Sound Level (dB)', fontsize=12, fontweight='bold')
        axes[0, 1].set_title('Sound Level Variance', fontsize=14, fontweight='bold')
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].set_facecolor('#FAFAFA')
        
        # 3. Hourly average with quality zones
        time_hours = np.arange(len(self.data)) * self.measurement_interval / 3600
        window = max(100, int(600 / self.measurement_interval))  # 10분 윈도우
        rolling_mean = self.data['dB'].rolling(window=window).mean()
        
        axes[1, 0].plot(time_hours, rolling_mean, color='#2E86DE', linewidth=2.5, label='Rolling Average')
        axes[1, 0].axhline(30, color='green', linestyle='--', linewidth=1.5, label='Deep Sleep (30dB)', alpha=0.6)
        axes[1, 0].axhline(35, color='orange', linestyle='--', linewidth=1.5, label='Restless (35dB)', alpha=0.6)
        axes[1, 0].axhline(40, color='red', linestyle='--', linewidth=1.5, label='Disturbed (40dB)', alpha=0.6)
        axes[1, 0].set_xlabel('Time (hours)', fontsize=12, fontweight='bold')
        axes[1, 0].set_ylabel('Average Sound Level (dB)', fontsize=12, fontweight='bold')
        axes[1, 0].set_title('Sleep Quality Over Time', fontsize=14, fontweight='bold')
        axes[1, 0].legend(fontsize=9)
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].set_facecolor('#FAFAFA')
        
        # 4. Cumulative noise events
        cumulative_noise = self.data['is_noise'].cumsum()
        axes[1, 1].plot(time_hours, cumulative_noise, color='#EE5A6F', linewidth=2.5)
        axes[1, 1].fill_between(time_hours, 0, cumulative_noise, color='#EE5A6F', alpha=0.2)
        axes[1, 1].set_xlabel('Time (hours)', fontsize=12, fontweight='bold')
        axes[1, 1].set_ylabel('Cumulative Noise Events', fontsize=12, fontweight='bold')
        axes[1, 1].set_title('Noise Event Accumulation', fontsize=14, fontweight='bold')
        axes[1, 1].grid(True, alpha=0.3)
        axes[1, 1].set_facecolor('#FAFAFA')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Additional graphs saved: {save_path}")
        
        plt.show()
    
    def generate_report(self, condition_name, save_dir='results'):
        """
        분석 보고서 생성
        
        Parameters:
        -----------
        condition_name : str
            실험 조건 이름 (A, B, C 등)
        save_dir : str
            저장 디렉토리
        """
        if not self.stats:
            self.calculate_statistics()
        
        # 디렉토리 생성
        os.makedirs(save_dir, exist_ok=True)
        
        # 보고서 파일명
        report_file = os.path.join(save_dir, f'report_{condition_name}.txt')
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write(f"수면 패턴 분석 보고서 - 조건 {condition_name}\n")
            f.write("="*60 + "\n\n")
            
            f.write(f"분석 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"임계값 설정: {self.threshold_db} dB\n\n")
            
            f.write("--- 측정 정보 ---\n")
            for key, value in self.stats.items():
                key_korean = key.replace('_', ' ')
                f.write(f"{key_korean}: {value}\n")
            
            f.write("\n" + "="*60 + "\n")
        
        print(f"✓ 보고서 저장: {report_file}")
        
        return report_file


def main():
    """메인 실행 함수"""
    print("\n" + "="*60)
    print("수면 패턴 분석 프로그램")
    print("="*60 + "\n")
    
    # 분석기 초기화 (임계값: 40dB)
    analyzer = SleepAnalyzer(threshold_db=40)
    
    # 데이터 파일 경로 (예시)
    data_file = 'data/sample_sleep_data_A.csv'
    
    # 파일이 존재하는지 확인
    if not os.path.exists(data_file):
        print(f"✗ 파일을 찾을 수 없습니다: {data_file}")
        print("\n사용법:")
        print("1. data/ 폴더에 CSV 파일을 넣으세요")
        print("2. CSV 형식: 시간,dB")
        print("   예: 23:30:00,35.2")
        return
    
    # 1. 데이터 로드
    analyzer.load_data(data_file)
    
    # 2. 전처리
    analyzer.preprocess_data(window_size=5)
    
    # 3. 통계 계산 및 출력
    analyzer.calculate_statistics()
    analyzer.print_statistics()
    
    # 4. 그래프 생성
    analyzer.plot_data(save_path='results/sleep_analysis_A.png')
    
    # 5. 보고서 생성
    analyzer.generate_report('A')
    
    print("\n✓ 분석 완료!")


if __name__ == "__main__":
    main()
