"""
수면 패턴 분석 - 대화형 CLI 메뉴 프로그램
명령어를 입력하면 해당 기능을 실행합니다.
"""

import os
import sys
from datetime import datetime
from sleep_analyzer import SleepAnalyzer
from hypothesis_test import HypothesisTest
from convert_dbmeter import convert_dbmeter_data


class SleepAnalysisApp:
    """대화형 수면 분석 앱"""
    
    def __init__(self):
        self.current_data = None
        self.current_file = None
        self.analyzer = None
        
    def clear_screen(self):
        """화면 지우기"""
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def show_banner(self):
        """앱 배너 출력"""
        print("\n" + "="*70)
        print("🌙 수면 패턴 분석 시스템 v1.0")
        print("="*70)
        print("스마트폰 소리 센서로 당신의 수면을 분석합니다")
        print("="*70 + "\n")
    
    def show_menu(self):
        """메인 메뉴 출력"""
        print("\n📋 메인 메뉴")
        print("-" * 70)
        print("1️⃣  데이터 불러오기 (표준 CSV)")
        print("2️⃣  dBMeter 데이터 변환 및 불러오기")
        print("3️⃣  데이터 분석 및 통계")
        print("4️⃣  그래프 보기")
        print("5️⃣  조건별 비교 분석 (A/B/C)")
        print("6️⃣  가설 검증")
        print("7️⃣  보고서 생성")
        print("8️⃣  현재 데이터 정보")
        print("9️⃣  설정 (임계값 변경)")
        print("0️⃣  종료")
        print("-" * 70)
        
        if self.current_file:
            print(f"📂 현재 파일: {self.current_file}")
        else:
            print("⚠️  데이터가 로드되지 않았습니다")
        print()
    
    def load_data(self):
        """데이터 불러오기"""
        print("\n" + "="*70)
        print("📂 데이터 불러오기")
        print("="*70)
        
        # data 폴더의 CSV 파일 목록
        data_dir = 'data'
        if os.path.exists(data_dir):
            csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
            
            if csv_files:
                print("\n사용 가능한 파일:")
                for i, f in enumerate(csv_files, 1):
                    print(f"  {i}. {f}")
                print(f"  {len(csv_files)+1}. 직접 경로 입력")
                
                choice = input(f"\n파일 번호 선택 (1-{len(csv_files)+1}): ").strip()
                
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(csv_files):
                        file_path = os.path.join(data_dir, csv_files[choice_num-1])
                    elif choice_num == len(csv_files) + 1:
                        file_path = input("파일 경로를 입력하세요: ").strip()
                    else:
                        print("❌ 잘못된 선택입니다")
                        return
                except ValueError:
                    print("❌ 숫자를 입력하세요")
                    return
            else:
                file_path = input("\nCSV 파일 경로를 입력하세요: ").strip()
        else:
            file_path = input("\nCSV 파일 경로를 입력하세요: ").strip()
        
        # 임계값 설정
        threshold = input("\n소음 임계값 (dB, 기본값 40): ").strip()
        threshold = float(threshold) if threshold else 40.0
        
        # 분석기 생성 및 데이터 로드
        self.analyzer = SleepAnalyzer(threshold_db=threshold)
        data = self.analyzer.load_data(file_path)
        
        if data is not None:
            self.current_data = data
            self.current_file = file_path
            self.analyzer.preprocess_data()
            print("\n✅ 데이터 로드 및 전처리 완료!")
        else:
            print("\n❌ 데이터 로드 실패")
        
        input("\nEnter를 눌러 계속...")
    
    def convert_and_load(self):
        """dBMeter 데이터 변환 및 불러오기"""
        print("\n" + "="*70)
        print("🔄 dBMeter 데이터 변환")
        print("="*70)
        
        file_path = input("\ndBMeter 파일 경로를 입력하세요: ").strip()
        
        if not os.path.exists(file_path):
            print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
            input("\nEnter를 눌러 계속...")
            return
        
        # 변환 실행
        df = convert_dbmeter_data(file_path)
        
        if df is not None:
            # 변환된 파일로 자동 로드
            date_str = df['시간'].min().strftime('%Y%m%d')
            converted_file = f'data/sleep_data_{date_str}.csv'
            
            # 분석기 생성
            threshold = input("\n소음 임계값 (dB, 기본값 40): ").strip()
            threshold = float(threshold) if threshold else 40.0
            
            self.analyzer = SleepAnalyzer(threshold_db=threshold)
            self.current_data = self.analyzer.load_data(converted_file)
            self.current_file = converted_file
            self.analyzer.preprocess_data()
            
            print("\n✅ 변환 및 로드 완료!")
        else:
            print("\n❌ 변환 실패")
        
        input("\nEnter를 눌러 계속...")
    
    def analyze_data(self):
        """데이터 분석 및 통계"""
        if self.analyzer is None:
            print("\n❌ 먼저 데이터를 불러오세요 (메뉴 1 또는 2)")
            input("\nEnter를 눌러 계속...")
            return
        
        print("\n" + "="*70)
        print("📊 데이터 분석")
        print("="*70)
        
        self.analyzer.calculate_statistics()
        self.analyzer.print_statistics()
        
        input("\nEnter를 눌러 계속...")
    
    def show_graph(self):
        """그래프 표시"""
        if self.analyzer is None:
            print("\n❌ 먼저 데이터를 불러오세요 (메뉴 1 또는 2)")
            input("\nEnter를 눌러 계속...")
            return
        
        print("\n" + "="*70)
        print("📈 그래프 생성")
        print("="*70)
        
        save_choice = input("\n그래프를 파일로 저장하시겠습니까? (y/n, 기본값 y): ").strip().lower()
        
        if save_choice in ['', 'y', 'yes']:
            date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_path = f'results/sleep_graph_{date_str}.png'
        else:
            save_path = None
        
        print("\n그래프를 생성하는 중...")
        self.analyzer.plot_data(save_path=save_path)
        print("\n✅ 그래프가 표시되었습니다")
        
        input("\nEnter를 눌러 계속...")
    
    def compare_conditions(self):
        """조건별 비교 분석"""
        print("\n" + "="*70)
        print("🔬 조건별 비교 분석")
        print("="*70)
        
        print("\n이 기능은 여러 조건(A/B/C)의 데이터를 비교합니다")
        print("각 조건의 CSV 파일을 준비해주세요\n")
        
        # 임계값 설정
        threshold = input("소음 임계값 (dB, 기본값 40): ").strip()
        threshold = float(threshold) if threshold else 40.0
        
        tester = HypothesisTest(threshold_db=threshold)
        
        # 조건별 파일 입력
        conditions = {}
        for cond in ['A', 'B', 'C']:
            file_path = input(f"\n조건 {cond} 파일 경로 (없으면 Enter): ").strip()
            if file_path and os.path.exists(file_path):
                conditions[cond] = file_path
            elif file_path:
                print(f"⚠️  파일을 찾을 수 없습니다: {file_path}")
        
        if len(conditions) < 2:
            print("\n❌ 최소 2개 조건이 필요합니다")
            input("\nEnter를 눌러 계속...")
            return
        
        # 분석 실행
        print("\n분석 중...")
        for cond, file_path in conditions.items():
            tester.analyze_condition(file_path, cond)
        
        # 비교 결과
        tester.compare_conditions()
        
        # 그래프
        save_choice = input("\n비교 그래프를 저장하시겠습니까? (y/n, 기본값 y): ").strip().lower()
        if save_choice in ['', 'y', 'yes']:
            tester.plot_comparison(save_path='results/comparison_graph.png')
        
        input("\nEnter를 눌러 계속...")
    
    def test_hypothesis(self):
        """가설 검증"""
        if self.analyzer is None:
            print("\n❌ 먼저 데이터를 불러오세요 (메뉴 1 또는 2)")
            print("또는 조건별 비교 분석(메뉴 5)을 사용하세요")
            input("\nEnter를 눌러 계속...")
            return
        
        print("\n" + "="*70)
        print("🔬 가설 검증")
        print("="*70)
        print("\n가설1: 수면 중 dB 값이 높은 구간은 뒤척임·각성 가능성이 높다")
        print("가설2: 취침 전 스마트폰/게임 시간이 길수록 소음 구간 비율이 증가한다")
        
        print("\n✅ 현재 데이터에 대한 분석:")
        self.analyzer.calculate_statistics()
        stats = self.analyzer.stats
        
        print(f"\n소음 구간 비율: {stats['소음_구간_비율_%']:.2f}%")
        print(f"평균 dB: {stats['평균_dB']:.1f}")
        print(f"최대 dB: {stats['최대_dB']:.1f}")
        
        print("\n💡 가설2 검증은 여러 조건 비교가 필요합니다 (메뉴 5 사용)")
        
        input("\nEnter를 눌러 계속...")
    
    def generate_report(self):
        """보고서 생성"""
        if self.analyzer is None:
            print("\n❌ 먼저 데이터를 불러오세요 (메뉴 1 또는 2)")
            input("\nEnter를 눌러 계속...")
            return
        
        print("\n" + "="*70)
        print("📄 보고서 생성")
        print("="*70)
        
        condition = input("\n조건 이름 (A/B/C 또는 임의, 기본값 A): ").strip() or 'A'
        
        print("\n보고서 생성 중...")
        self.analyzer.generate_report(condition)
        
        print("\n✅ 보고서가 results/ 폴더에 저장되었습니다")
        
        input("\nEnter를 눌러 계속...")
    
    def show_data_info(self):
        """현재 데이터 정보"""
        if self.current_data is None:
            print("\n❌ 로드된 데이터가 없습니다")
            input("\nEnter를 눌러 계속...")
            return
        
        print("\n" + "="*70)
        print("ℹ️  현재 데이터 정보")
        print("="*70)
        
        print(f"\n파일: {self.current_file}")
        print(f"레코드 수: {len(self.current_data):,}개")
        print(f"측정 시간: {len(self.current_data) / 720:.1f}시간")
        print(f"\ndB 범위: {self.current_data['dB'].min():.1f} ~ {self.current_data['dB'].max():.1f}")
        print(f"평균 dB: {self.current_data['dB'].mean():.1f}")
        
        if self.analyzer and self.analyzer.stats:
            print(f"\n소음 임계값: {self.analyzer.threshold_db} dB")
            print(f"소음 구간 비율: {self.analyzer.stats['소음_구간_비율_%']:.2f}%")
        
        print("\n데이터 샘플 (처음 5개):")
        print(self.current_data.head())
        
        input("\nEnter를 눌러 계속...")
    
    def change_settings(self):
        """설정 변경"""
        if self.analyzer is None:
            print("\n❌ 먼저 데이터를 불러오세요")
            input("\nEnter를 눌러 계속...")
            return
        
        print("\n" + "="*70)
        print("⚙️  설정")
        print("="*70)
        
        print(f"\n현재 소음 임계값: {self.analyzer.threshold_db} dB")
        
        new_threshold = input("새 임계값 (Enter로 건너뛰기): ").strip()
        
        if new_threshold:
            try:
                new_threshold = float(new_threshold)
                self.analyzer.threshold_db = new_threshold
                self.analyzer.preprocess_data()  # 재처리
                print(f"\n✅ 임계값이 {new_threshold} dB로 변경되었습니다")
            except ValueError:
                print("\n❌ 올바른 숫자를 입력하세요")
        
        input("\nEnter를 눌러 계속...")
    
    def run(self):
        """앱 실행"""
        while True:
            self.clear_screen()
            self.show_banner()
            self.show_menu()
            
            choice = input("메뉴를 선택하세요: ").strip()
            
            if choice == '1':
                self.load_data()
            elif choice == '2':
                self.convert_and_load()
            elif choice == '3':
                self.analyze_data()
            elif choice == '4':
                self.show_graph()
            elif choice == '5':
                self.compare_conditions()
            elif choice == '6':
                self.test_hypothesis()
            elif choice == '7':
                self.generate_report()
            elif choice == '8':
                self.show_data_info()
            elif choice == '9':
                self.change_settings()
            elif choice == '0':
                print("\n👋 프로그램을 종료합니다. 좋은 수면 되세요!")
                break
            else:
                print("\n❌ 잘못된 선택입니다")
                input("\nEnter를 눌러 계속...")


def main():
    """메인 실행"""
    app = SleepAnalysisApp()
    app.run()


if __name__ == "__main__":
    main()
