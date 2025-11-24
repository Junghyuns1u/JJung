"""
dBMeter 앱 데이터 변환 스크립트
한글 날짜 형식을 표준 CSV로 변환
"""

import pandas as pd
import os
from datetime import datetime


def convert_dbmeter_data(input_file, output_file=None):
    """
    dBMeter 앱의 한글 CSV를 표준 형식으로 변환
    
    Parameters:
    -----------
    input_file : str
        dBMeter 앱에서 내보낸 CSV 파일 경로
    output_file : str, optional
        변환된 파일 저장 경로 (없으면 자동 생성)
    
    Returns:
    --------
    pd.DataFrame : 변환된 데이터
    """
    print(f"\n📂 파일 읽는 중: {input_file}")
    
    try:
        # 파일 읽기 (한글 인코딩)
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 데이터 파싱
        timestamps = []
        db_values = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            try:
                # "2025. 11. 15. 오전 3:02:46, 53.058983" 형식 파싱
                parts = line.split(',')
                if len(parts) != 2:
                    continue
                
                datetime_str = parts[0].strip()
                db_value = float(parts[1].strip())
                
                # 한글 날짜 파싱
                # "2025. 11. 15. 오전 3:02:46" → datetime
                datetime_str = datetime_str.replace('오전', 'AM').replace('오후', 'PM')
                
                # 날짜와 시간 분리
                date_part = datetime_str.split(' AM ')[0] if ' AM ' in datetime_str else datetime_str.split(' PM ')[0]
                time_part = datetime_str.split(' AM ')[1] if ' AM ' in datetime_str else datetime_str.split(' PM ')[1]
                am_pm = 'AM' if ' AM ' in datetime_str else 'PM'
                
                # 날짜 파싱: "2025. 11. 15."
                year, month, day = date_part.replace('.', '').split()[:3]
                
                # 시간 파싱: "3:02:46"
                hour, minute, second = time_part.split(':')
                hour = int(hour)
                
                # AM/PM 처리
                if am_pm == 'PM' and hour != 12:
                    hour += 12
                elif am_pm == 'AM' and hour == 12:
                    hour = 0
                
                # datetime 객체 생성
                dt = datetime(int(year), int(month), int(day), hour, int(minute), int(second))
                
                timestamps.append(dt)
                db_values.append(db_value)
                
            except Exception as e:
                print(f"⚠️  라인 파싱 실패: {line[:50]}... ({e})")
                continue
        
        # DataFrame 생성
        df = pd.DataFrame({
            '시간': timestamps,
            'dB': db_values
        })
        
        # 시간 기준 정렬
        df = df.sort_values('시간').reset_index(drop=True)
        
        print(f"✓ 데이터 로드 완료!")
        print(f"  총 레코드: {len(df):,}개")
        print(f"  측정 시작: {df['시간'].min()}")
        print(f"  측정 종료: {df['시간'].max()}")
        print(f"  측정 시간: {(df['시간'].max() - df['시간'].min()).total_seconds() / 3600:.1f}시간")
        print(f"  평균 dB: {df['dB'].mean():.1f}")
        print(f"  최대 dB: {df['dB'].max():.1f}")
        
        # 저장
        if output_file is None:
            # 자동 파일명 생성
            date_str = df['시간'].min().strftime('%Y%m%d')
            output_file = f'data/sleep_data_{date_str}.csv'
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"\n✓ 변환 완료: {output_file}")
        
        return df
        
    except Exception as e:
        print(f"\n✗ 파일 변환 실패: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """메인 실행"""
    print("="*70)
    print("dBMeter 데이터 변환기")
    print("="*70)
    
    # 입력 파일 경로
    input_file = input("\n📁 dBMeter 파일 경로를 입력하세요: ").strip()
    
    if not os.path.exists(input_file):
        print(f"✗ 파일을 찾을 수 없습니다: {input_file}")
        return
    
    # 변환 실행
    df = convert_dbmeter_data(input_file)
    
    if df is not None:
        print("\n✓ 변환 성공!")
        print("\n다음 단계:")
        print("1. sleep_analyzer.py 또는 hypothesis_test.py로 분석")
        print("2. 또는 app.py (웹 앱) 실행")


if __name__ == "__main__":
    main()
