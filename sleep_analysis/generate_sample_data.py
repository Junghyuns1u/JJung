"""
샘플 데이터 생성 스크립트
실제와 유사한 수면 중 소리 데이터를 생성합니다.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random


def generate_sleep_data(condition, duration_hours=7, start_time="23:30:00"):
    """
    수면 데이터 생성
    
    Parameters:
    -----------
    condition : str
        조건 (A: 평소, B: 취침 전 폰 사용, C: 폰 사용 최소)
    duration_hours : float
        측정 시간 (시간)
    start_time : str
        시작 시간
    
    Returns:
    --------
    pd.DataFrame : 생성된 데이터
    """
    # 5초 간격으로 데이터 생성
    num_records = int(duration_hours * 3600 / 5)
    
    # 기본 배경 소음 (30-35 dB)
    base_noise = 32
    
    # 시간별 데이터 생성
    times = []
    dbs = []
    
    start = datetime.strptime(start_time, "%H:%M:%S")
    
    for i in range(num_records):
        current_time = start + timedelta(seconds=i * 5)
        times.append(current_time.strftime("%H:%M:%S"))
        
        # 시간대별 패턴
        hour_progress = i / num_records
        
        # 기본 노이즈 (정규분포)
        db = base_noise + np.random.normal(0, 2)
        
        # 조건에 따른 패턴 조정
        if condition == "A":  # 평소 패턴
            # 입면 초기(첫 1시간): 약간 높음
            if hour_progress < 0.15:
                db += np.random.normal(2, 1)
            # 깊은 수면(중간): 낮음
            elif 0.3 < hour_progress < 0.7:
                db -= np.random.normal(1, 0.5)
            # 기상 전(마지막 1시간): 약간 높음
            elif hour_progress > 0.85:
                db += np.random.normal(1.5, 1)
            
            # 무작위 뒤척임 (5-8회)
            if random.random() < 0.008:
                db += np.random.uniform(10, 18)
        
        elif condition == "B":  # 취침 전 폰 사용 (수면 질 저하)
            # 입면 초기: 더 높음 (잠들기 어려움)
            if hour_progress < 0.2:
                db += np.random.normal(3, 1.5)
            # 얕은 수면
            elif 0.3 < hour_progress < 0.7:
                db += np.random.normal(0.5, 0.8)
            # 기상 전: 더 불안정
            elif hour_progress > 0.8:
                db += np.random.normal(2, 1.5)
            
            # 뒤척임 더 빈번 (10-15회)
            if random.random() < 0.015:
                db += np.random.uniform(12, 22)
        
        elif condition == "C":  # 폰 사용 최소 (양질의 수면)
            # 입면 초기: 빠른 안정
            if hour_progress < 0.1:
                db += np.random.normal(1, 0.8)
            # 깊은 수면: 매우 낮음
            elif 0.2 < hour_progress < 0.75:
                db -= np.random.normal(2, 0.5)
            # 기상 전: 자연스러운 각성
            elif hour_progress > 0.9:
                db += np.random.normal(1, 0.8)
            
            # 뒤척임 적음 (3-5회)
            if random.random() < 0.005:
                db += np.random.uniform(8, 15)
        
        # 간헐적 코골이/숨소리 (매우 약함)
        if random.random() < 0.02:
            db += np.random.uniform(2, 5)
        
        # 외부 소음 (매우 드묾)
        if random.random() < 0.002:
            db += np.random.uniform(5, 12)
        
        # dB는 음수가 될 수 없음
        db = max(db, 25)
        
        dbs.append(round(db, 1))
    
    # DataFrame 생성
    df = pd.DataFrame({
        '시간': times,
        'dB': dbs
    })
    
    return df


def main():
    """샘플 데이터 생성 메인 함수"""
    print("샘플 수면 데이터 생성 중...\n")
    
    conditions = {
        'A': {'duration': 7.5, 'start': "23:30:00", 'desc': "평소 패턴"},
        'B': {'duration': 7.5, 'start': "23:45:00", 'desc': "취침 전 2시간 폰 사용"},
        'C': {'duration': 7.75, 'start': "23:00:00", 'desc': "취침 전 폰 사용 최소"}
    }
    
    for cond, params in conditions.items():
        print(f"조건 {cond} 생성 중: {params['desc']}")
        
        df = generate_sleep_data(
            condition=cond,
            duration_hours=params['duration'],
            start_time=params['start']
        )
        
        # 저장
        filename = f'data/sample_sleep_data_{cond}.csv'
        df.to_csv(filename, index=False, encoding='utf-8')
        
        print(f"  ✓ 저장 완료: {filename}")
        print(f"    레코드 수: {len(df)}, 측정 시간: {params['duration']}시간")
        print(f"    평균 dB: {df['dB'].mean():.1f}, 최대 dB: {df['dB'].max():.1f}\n")
    
    print("✓ 모든 샘플 데이터 생성 완료!")


if __name__ == "__main__":
    main()
