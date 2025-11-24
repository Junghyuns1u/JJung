"""
수면 패턴 분석 웹 앱 (Streamlit)
브라우저에서 실행되는 GUI 앱
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
from sleep_analyzer import SleepAnalyzer
from convert_dbmeter import convert_dbmeter_data

# 페이지 설정
st.set_page_config(
    page_title="수면 패턴 분석",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False


def load_css():
    """커스텀 CSS"""
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 1rem;
        border-radius: 0.3rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 1rem;
        border-radius: 0.3rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)


def main():
    """메인 앱"""
    load_css()
    
    # 헤더
    st.markdown('<div class="main-header">🌙 수면 패턴 분석 시스템</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # 사이드바
    with st.sidebar:
        st.header("📋 메뉴")
        
        menu = st.radio(
            "기능 선택",
            ["🏠 홈", "📂 데이터 업로드", "📊 데이터 분석", "📈 그래프 보기", 
             "🔬 조건별 비교", "📄 보고서", "⚙️ 설정"]
        )
        
        st.markdown("---")
        st.info("💡 **사용 팁**\n\n1. 데이터 업로드\n2. 분석 실행\n3. 그래프 확인\n4. 보고서 다운로드")
    
    # 세션 상태 초기화
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = None
    if 'threshold' not in st.session_state:
        st.session_state.threshold = 40.0
    
    # 메뉴별 페이지
    if menu == "🏠 홈":
        show_home()
    elif menu == "📂 데이터 업로드":
        show_upload()
    elif menu == "📊 데이터 분석":
        show_analysis()
    elif menu == "📈 그래프 보기":
        show_graphs()
    elif menu == "🔬 조건별 비교":
        show_comparison()
    elif menu == "📄 보고서":
        show_report()
    elif menu == "⚙️ 설정":
        show_settings()


def show_home():
    """홈 페이지"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📊 데이터 분석")
        st.write("CSV 파일을 업로드하고 수면 패턴을 분석합니다")
        st.write("- 소음 구간 분류")
        st.write("- 통계 지표 계산")
        st.write("- 시간대별 패턴 분석")
    
    with col2:
        st.markdown("### 📈 시각화")
        st.write("다양한 그래프로 수면을 시각화합니다")
        st.write("- 시간-dB 그래프")
        st.write("- 소음 구간 표시")
        st.write("- 조건별 비교 차트")
    
    with col3:
        st.markdown("### 🔬 가설 검증")
        st.write("과학적 가설을 검증합니다")
        st.write("- dB와 각성의 관계")
        st.write("- 폰 사용과 수면 질")
        st.write("- 상관관계 분석")
    
    st.markdown("---")
    
    # 프로젝트 정보
    st.markdown("### 📖 프로젝트 소개")
    
    with st.expander("🎯 연구 목적"):
        st.write("""
        이 프로젝트는 스마트폰의 소리 센서를 활용하여 수면 중 발생하는 소리 변화를 
        측정하고, 이를 통해 개인의 수면 패턴을 분석합니다. 
        
        - **가설 1**: 수면 중 dB 값이 높은 구간은 뒤척임·각성 가능성이 높다
        - **가설 2**: 취침 전 스마트폰/게임 시간이 길수록 소음 구간 비율이 증가한다
        """)
    
    with st.expander("🔬 실험 조건"):
        st.write("""
        - **조건 A**: 평소 생활 패턴
        - **조건 B**: 취침 전 2시간 폰 사용
        - **조건 C**: 취침 전 폰 사용 최소화
        
        각 조건별로 6-8시간 측정, 5초 간격으로 dB 값 기록
        """)
    
    with st.expander("📱 필요한 준비물"):
        st.write("""
        - 스마트폰 (Android/iOS)
        - 소리 측정 앱 (dBMeter, Sound Meter 등)
        - 충전기
        - 조용한 수면 환경
        """)
    
    # 현재 상태
    st.markdown("---")
    st.markdown("### 📌 현재 상태")
    
    if st.session_state.data is not None:
        st.success(f"✅ 데이터 로드 완료 ({len(st.session_state.data):,}개 레코드)")
    else:
        st.warning("⚠️ 데이터를 업로드해주세요")


def show_upload():
    """데이터 업로드 페이지"""
    st.header("📂 데이터 업로드")
    
    tab1, tab2 = st.tabs(["📄 표준 CSV", "📱 dBMeter 파일"])
    
    with tab1:
        st.markdown("### 표준 CSV 업로드")
        st.info("형식: `시간,dB` (예: `23:30:00,35.2`)")
        
        uploaded_file = st.file_uploader(
            "CSV 파일을 선택하세요",
            type=['csv'],
            key='standard_csv'
        )
        
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8')
                
                # 컬럼명 확인
                if '시간' in df.columns and 'dB' in df.columns:
                    st.session_state.data = df
                    
                    st.success(f"✅ 데이터 로드 성공! ({len(df):,}개 레코드)")
                    
                    # 데이터 미리보기
                    with st.expander("📊 데이터 미리보기"):
                        st.dataframe(df.head(10))
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("레코드 수", f"{len(df):,}")
                        with col2:
                            st.metric("평균 dB", f"{df['dB'].mean():.1f}")
                        with col3:
                            st.metric("최대 dB", f"{df['dB'].max():.1f}")
                    
                    # 분석기 초기화
                    if st.button("🔍 분석 시작", type="primary"):
                        analyzer = SleepAnalyzer(threshold_db=st.session_state.threshold)
                        analyzer.data = df
                        analyzer.preprocess_data()
                        st.session_state.analyzer = analyzer
                        st.success("✅ 분석 준비 완료!")
                        st.balloons()
                else:
                    st.error("❌ CSV 형식이 올바르지 않습니다. `시간,dB` 컬럼이 필요합니다.")
                    
            except Exception as e:
                st.error(f"❌ 파일 로드 실패: {e}")
    
    with tab2:
        st.markdown("### dBMeter 앱 데이터 변환")
        st.info("dBMeter 앱에서 내보낸 한글 형식 CSV를 자동 변환합니다")
        
        uploaded_file = st.file_uploader(
            "dBMeter 파일을 선택하세요",
            type=['csv', 'txt'],
            key='dbmeter_csv'
        )
        
        if uploaded_file:
            with st.spinner("변환 중..."):
                try:
                    # 임시 파일로 저장
                    temp_path = f"temp_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
                    with open(temp_path, 'wb') as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # 변환
                    df = convert_dbmeter_data(temp_path, output_file=None)
                    
                    # 임시 파일 삭제
                    os.remove(temp_path)
                    
                    if df is not None:
                        st.session_state.data = df
                        st.success(f"✅ 변환 및 로드 성공! ({len(df):,}개 레코드)")
                        
                        # 데이터 정보
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("레코드 수", f"{len(df):,}")
                        with col2:
                            st.metric("측정 시간", f"{len(df)/720:.1f}시간")
                        with col3:
                            st.metric("평균 dB", f"{df['dB'].mean():.1f}")
                        with col4:
                            st.metric("최대 dB", f"{df['dB'].max():.1f}")
                        
                        # 분석기 초기화
                        if st.button("🔍 분석 시작", type="primary", key='start_dbmeter'):
                            analyzer = SleepAnalyzer(threshold_db=st.session_state.threshold)
                            analyzer.data = df
                            analyzer.preprocess_data()
                            st.session_state.analyzer = analyzer
                            st.success("✅ 분석 준비 완료!")
                            st.balloons()
                    else:
                        st.error("❌ 변환 실패")
                        
                except Exception as e:
                    st.error(f"❌ 처리 실패: {e}")
                    if os.path.exists(temp_path):
                        os.remove(temp_path)


def show_analysis():
    """데이터 분석 페이지"""
    st.header("📊 데이터 분석")
    
    if st.session_state.analyzer is None:
        st.warning("⚠️ 먼저 데이터를 업로드하고 분석을 시작하세요 (📂 데이터 업로드)")
        return
    
    analyzer = st.session_state.analyzer
    
    # 분석 실행
    with st.spinner("분석 중..."):
        analyzer.calculate_statistics()
        stats = analyzer.stats
    
    st.success("✅ 분석 완료!")
    
    # 주요 지표 (KPI)
    st.markdown("### 📈 주요 지표")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "소음 구간 비율",
            f"{stats['소음_구간_비율_%']:.2f}%",
            help="임계값 이상의 소음이 발생한 비율"
        )
    
    with col2:
        st.metric(
            "평균 dB",
            f"{stats['평균_dB']:.1f}",
            help="전체 측정 시간 동안의 평균 음량"
        )
    
    with col3:
        st.metric(
            "최대 dB",
            f"{stats['최대_dB']:.1f}",
            help="측정 중 최고 음량"
        )
    
    with col4:
        st.metric(
            "측정 시간",
            f"{stats['총_측정_시간_분']/60:.1f}시간",
            help="총 수면 측정 시간"
        )
    
    # 상세 통계
    st.markdown("---")
    st.markdown("### 📋 상세 통계")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 기본 통계")
        st.write(f"**총 측정 횟수**: {stats['총_측정_횟수']:,}회")
        st.write(f"**소음 구간 횟수**: {stats['소음_구간_횟수']}회")
        st.write(f"**최소 dB**: {stats['최소_dB']:.1f}")
        st.write(f"**표준편차**: {stats['표준편차_dB']:.2f}")
    
    with col2:
        st.markdown("#### 패턴 분석")
        st.write(f"**연속 소음 구간 평균**: {stats['연속_소음_구간_평균_길이_초']:.1f}초")
        st.write(f"**최장 소음 구간**: {stats['최장_연속_소음_구간_초']:.1f}초")
        st.write(f"**수면 초반 1시간 소음**: {stats['수면초반1시간_소음비율_%']:.2f}%")
        if 'REM_수면_비율_%' in stats:
            st.write(f"**REM 수면 비율**: {stats['REM_수면_비율_%']:.1f}%")
    
    # 수면 품질 분석 (외부 연구 기반)
    st.markdown("---")
    st.markdown("### 🛏️ 수면 품질 분석")
    st.caption("기준: Sleep Foundation & NIH Sleep Research")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "깊은 수면",
            f"{stats['깊은수면_비율_%']:.1f}%",
            help="<30dB: 매우 조용한 깊은 수면"
        )
    
    with col2:
        st.metric(
            "얕은 수면",
            f"{stats['얕은수면_비율_%']:.1f}%",
            help="30-35dB: 조용한 수면, 뒤척임 없음"
        )
    
    with col3:
        st.metric(
            "뒤척임",
            f"{stats['뒤척임_비율_%']:.1f}%",
            help="35-40dB: 뒤척임, 약한 움직임"
        )
    
    with col4:
        st.metric(
            "수면 방해",
            f"{stats['수면방해_비율_%']:.1f}%",
            help=">40dB: 자주 깨거나 큰 소음"
        )
    
    # 해석
    st.markdown("---")
    st.markdown("### 💡 해석")
    
    noise_ratio = stats['소음_구간_비율_%']
    avg_db = stats['평균_dB']
    
    if noise_ratio < 1:
        interpretation = "🟢 **매우 좋음**: 소음이 거의 없는 안정적인 수면입니다."
    elif noise_ratio < 3:
        interpretation = "🟡 **양호**: 약간의 소음이 있지만 정상 범위입니다."
    elif noise_ratio < 5:
        interpretation = "🟠 **주의**: 소음 구간이 다소 많습니다. 수면 환경을 점검하세요."
    else:
        interpretation = "🔴 **개선 필요**: 소음이 많이 발생했습니다. 수면 질 개선이 필요합니다."
    
    st.info(interpretation)
    
    # 권장사항
    with st.expander("💡 수면 개선 권장사항"):
        st.write("""
        **소음 구간이 높다면:**
        - 취침 전 스마트폰 사용 줄이기
        - 카페인 섭취 시간 조정
        - 규칙적인 수면 시간 유지
        - 수면 환경 개선 (온도, 조명)
        
        **평균 dB가 높다면:**
        - 주변 소음원 제거
        - 방음 처리
        - 귀마개 착용 고려
        """)


def show_graphs():
    """그래프 페이지"""
    st.header("📈 그래프 보기")
    
    if st.session_state.analyzer is None:
        st.warning("⚠️ 먼저 데이터를 분석하세요 (📊 데이터 분석)")
        return
    
    analyzer = st.session_state.analyzer
    data = analyzer.data
    
    # 그래프 옵션
    col1, col2 = st.columns(2)
    with col1:
        show_original = st.checkbox("원본 데이터 표시", value=True)
    with col2:
        show_smoothed = st.checkbox("평활화 데이터 표시", value=True)
    
    # 메인 그래프
    st.markdown("### 🌙 Sleep Sound Pattern")
    
    fig, ax = plt.subplots(figsize=(16, 7))
    
    # 시간 인덱스 (시간 단위)
    time_hours = np.arange(len(data)) * analyzer.measurement_interval / 3600
    
    # REM 수면 구간
    if 'is_rem' in data.columns:
        rem_mask = data['is_rem'].values
        in_rem = False
        rem_start = 0
        rem_count = 0
        for i in range(len(rem_mask)):
            if rem_mask[i] and not in_rem:
                rem_start = time_hours[i]
                in_rem = True
            elif not rem_mask[i] and in_rem:
                label = 'REM Sleep (estimated)' if rem_count == 0 else ''
                ax.axvspan(rem_start, time_hours[i-1], alpha=0.12, color='mediumpurple', 
                          label=label, zorder=1)
                rem_count += 1
                in_rem = False
        if in_rem:
            label = 'REM Sleep (estimated)' if rem_count == 0 else ''
            ax.axvspan(rem_start, time_hours[-1], alpha=0.12, color='mediumpurple', 
                      label=label, zorder=1)
    
    # 원본 데이터
    if show_original:
        ax.plot(time_hours, data['dB'], 
                alpha=0.15, color='lightgray', label='Raw Data', linewidth=0.5, zorder=2)
    
    # 평활화 데이터
    if show_smoothed and 'dB_smoothed' in data.columns:
        ax.plot(time_hours, data['dB_smoothed'],
                color='#2E86DE', label='Smoothed Data', linewidth=2.5, zorder=3)
    
    # 임계값 선
    ax.axhline(y=analyzer.threshold_db, color='#EE5A6F', 
               linestyle='--', label=f'Noise Threshold ({analyzer.threshold_db}dB)', 
               linewidth=2, alpha=0.8, zorder=4)
    
    # 소음 구간 강조
    if 'is_noise' in data.columns:
        noise_indices = data[data['is_noise']].index
        if len(noise_indices) > 0:
            ax.scatter(time_hours[noise_indices],
                      data.loc[noise_indices, 'dB'],
                      color='#EE5A6F', s=20, alpha=0.7, label='Noise Events', 
                      zorder=5, edgecolors='darkred', linewidths=0.5)
    
    ax.set_xlabel('Time (hours)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Sound Level (dB)', fontsize=14, fontweight='bold')
    ax.set_title('Sleep Sound Pattern Analysis', fontsize=17, fontweight='bold', pad=20)
    
    legend = ax.legend(loc='upper right', fontsize=11, framealpha=0.95, 
                      shadow=True, fancybox=True)
    legend.get_frame().set_facecolor('#F8F9FA')
    
    ax.grid(True, alpha=0.25, linestyle='--', linewidth=0.5)
    ax.set_facecolor('#FAFAFA')
    
    # x축 눈금을 1시간 단위로
    max_hours = int(np.ceil(time_hours[-1]))
    ax.set_xticks(np.arange(0, max_hours + 1, 1))
    
    # y축 범위 설정
    ax.set_ylim([data['dB'].min() - 5, data['dB'].max() + 5])
    
    st.pyplot(fig)
    
    # 그래프 설명
    st.markdown("---")
    st.markdown("### 📖 그래프 해석")
    
    # 통계 가져오기
    stats = analyzer.stats
    
    # 시간대별 분석
    if '시간대별_품질' in stats:
        hourly_data = stats['시간대별_품질']
        
        # 가장 푹 잔 시간
        best_hour = max(hourly_data, key=lambda x: x['deep_sleep_%'])
        worst_hour = max(hourly_data, key=lambda x: x['restless_%'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success(f"""**😴 가장 푹 잔 시간**
            
**{best_hour['hour']}~{best_hour['hour']+1}시간째**
- 평균 음량: {best_hour['avg_db']:.1f}dB
- 깊은 수면: {best_hour['deep_sleep_%']:.1f}%

이 시간대는 가장 조용하고 안정적인 수면을 취했습니다.""")
        
        with col2:
            st.warning(f"""**😵 수면이 불안정했던 시간**
            
**{worst_hour['hour']}~{worst_hour['hour']+1}시간째**
- 평균 음량: {worst_hour['avg_db']:.1f}dB  
- 뒤척임: {worst_hour['restless_%']:.1f}%

이 시간대는 뒤척임이나 움직임이 많았습니다.""")
    
    # 수면 품질 종합 평가
    st.markdown("---")
    deep_ratio = stats['깊은수면_비율_%']
    restless_ratio = stats['뒤척임_비율_%']
    
    st.markdown("#### 💡 종합 평가")
    
    if deep_ratio > 50:
        quality = "🟢 **매우 좋음**"
        advice = "깊은 수면이 50% 이상으로 매우 건강한 수면입니다."
    elif deep_ratio > 30:
        quality = "🟢 **좋음**"
        advice = "깊은 수면 비율이 양호합니다."
    elif restless_ratio > 30:
        quality = "🟠 **개선 필요**"
        advice = "뒤척임이 많습니다. 수면 환경을 점검하세요."
    else:
        quality = "🟡 **보통**"
        advice = "수면 환경을 개선하면 더 좋은 수면을 취할 수 있습니다."
    
    st.info(f"{quality}\n\n{advice}")
    
    # 다운로드 버튼
    if st.button("💾 그래프 저장", type="primary"):
        save_path = f"results/sleep_graph_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        os.makedirs('results', exist_ok=True)
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        st.success(f"✅ 저장 완료: {save_path}")
    
    # 추가 그래프
    st.markdown("---")
    st.markdown("### 📊 Additional Analysis")
    st.caption("Based on sleep research: <30dB=deep sleep, 30-35dB=light sleep, 35-40dB=restless, >40dB=disturbed")
    
    if st.button("🔍 Show Additional Graphs"):
        analyzer.plot_additional_analysis()
        st.success("✅ Additional analysis graphs displayed!")


def show_comparison():
    """조건별 비교 페이지"""
    st.header("🔬 조건별 비교")
    
    st.info("이 기능은 여러 조건(A/B/C)의 데이터를 비교합니다. 각 조건의 dBMeter 파일을 업로드하세요.")
    
    # 파일 업로드
    col1, col2, col3 = st.columns(3)
    
    files = {}
    with col1:
        st.markdown("#### 조건 A (평소)")
        file_a = st.file_uploader("dBMeter CSV 파일", key='file_a', type=['csv', 'txt'])
        if file_a:
            try:
                # 임시 파일로 저장
                temp_path_a = f"temp_upload_a_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
                with open(temp_path_a, 'wb') as f:
                    f.write(file_a.getbuffer())
                
                # dBMeter 형식 변환
                df_a = convert_dbmeter_data(temp_path_a, output_file=None)
                os.remove(temp_path_a)
                
                if df_a is not None:
                    files['A'] = df_a
                    st.success(f"✅ 로드 완료 ({len(df_a):,}개)")
                else:
                    st.error("❌ 변환 실패")
            except Exception as e:
                st.error(f"❌ 오류: {e}")
                if os.path.exists(temp_path_a):
                    os.remove(temp_path_a)
    
    with col2:
        st.markdown("#### 조건 B (폰 2시간)")
        file_b = st.file_uploader("dBMeter CSV 파일", key='file_b', type=['csv', 'txt'])
        if file_b:
            try:
                temp_path_b = f"temp_upload_b_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
                with open(temp_path_b, 'wb') as f:
                    f.write(file_b.getbuffer())
                
                df_b = convert_dbmeter_data(temp_path_b, output_file=None)
                os.remove(temp_path_b)
                
                if df_b is not None:
                    files['B'] = df_b
                    st.success(f"✅ 로드 완료 ({len(df_b):,}개)")
                else:
                    st.error("❌ 변환 실패")
            except Exception as e:
                st.error(f"❌ 오류: {e}")
                if os.path.exists(temp_path_b):
                    os.remove(temp_path_b)
    
    with col3:
        st.markdown("#### 조건 C (폰 최소)")
        file_c = st.file_uploader("dBMeter CSV 파일", key='file_c', type=['csv', 'txt'])
        if file_c:
            try:
                temp_path_c = f"temp_upload_c_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
                with open(temp_path_c, 'wb') as f:
                    f.write(file_c.getbuffer())
                
                df_c = convert_dbmeter_data(temp_path_c, output_file=None)
                os.remove(temp_path_c)
                
                if df_c is not None:
                    files['C'] = df_c
                    st.success(f"✅ 로드 완료 ({len(df_c):,}개)")
                else:
                    st.error("❌ 변환 실패")
            except Exception as e:
                st.error(f"❌ 오류: {e}")
                if os.path.exists(temp_path_c):
                    os.remove(temp_path_c)
    
    if len(files) >= 2:
        if st.button("🔍 비교 분석 시작", type="primary"):
            with st.spinner("분석 중..."):
                from hypothesis_test import HypothesisTest
                
                tester = HypothesisTest(threshold_db=st.session_state.threshold)
                
                # 각 조건 분석
                for cond, df in files.items():
                    # 임시 파일로 저장
                    temp_file = f"temp_{cond}.csv"
                    df.to_csv(temp_file, index=False)
                    tester.analyze_condition(temp_file, cond)
                    os.remove(temp_file)
                
                # 비교 결과
                st.success("✅ 분석 완료!")
                
                comparison_df = tester.compare_conditions()
                
                st.markdown("### 📊 비교 결과")
                st.dataframe(comparison_df)
                
                # 가설 검증
                st.markdown("---")
                st.markdown("### 🔬 가설 검증")
                
                h1 = tester.test_hypothesis1()
                h2 = tester.test_hypothesis2()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 가설 1")
                    st.write(h1['가설'])
                    st.metric("평균 소음 비율", f"{h1['평균_소음비율_%']:.2f}%")
                
                with col2:
                    st.markdown("#### 가설 2")
                    st.write(h2['가설'])
                    if '가설_판정' in h2:
                        if h2['가설_판정'] == '지지':
                            st.success(f"✅ 가설 지지 (차이: {h2['차이_%p']:+.2f}%p)")
                        else:
                            st.warning(f"⚠️ 가설 기각 (차이: {h2['차이_%p']:+.2f}%p)")
    else:
        st.warning("⚠️ 최소 2개 조건의 데이터가 필요합니다")


def show_report():
    """보고서 페이지"""
    st.header("📄 보고서 생성")
    
    if st.session_state.analyzer is None:
        st.warning("⚠️ 먼저 데이터를 분석하세요")
        return
    
    analyzer = st.session_state.analyzer
    
    st.markdown("### 📝 보고서 미리보기")
    
    # 보고서 내용
    stats = analyzer.stats
    
    report_md = f"""
## 수면 패턴 분석 보고서

**분석 일시**: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}

---

### 📊 측정 정보

- **총 측정 횟수**: {stats['총_측정_횟수']:,}회
- **총 측정 시간**: {stats['총_측정_시간_분']:.1f}분 ({stats['총_측정_시간_분']/60:.1f}시간)
- **임계값 설정**: {analyzer.threshold_db} dB

### 📈 주요 지표

| 지표 | 값 |
|------|-----|
| 소음 구간 비율 | {stats['소음_구간_비율_%']:.2f}% |
| 평균 dB | {stats['평균_dB']:.2f} |
| 최대 dB | {stats['최대_dB']:.2f} |
| 최소 dB | {stats['최소_dB']:.2f} |
| 표준편차 | {stats['표준편차_dB']:.2f} |

### 🔍 패턴 분석

- **소음 구간 횟수**: {stats['소음_구간_횟수']}회
- **연속 소음 구간 평균 길이**: {stats['연속_소음_구간_평균_길이_초']:.1f}초
- **최장 연속 소음 구간**: {stats['최장_연속_소음_구간_초']:.1f}초
- **수면 초반 1시간 소음 비율**: {stats['수면초반1시간_소음비율_%']:.2f}%

### 💡 해석

"""
    
    if stats['소음_구간_비율_%'] < 1:
        report_md += "소음 구간 비율이 1% 미만으로 매우 안정적인 수면 패턴을 보입니다.\n"
    elif stats['소음_구간_비율_%'] < 3:
        report_md += "소음 구간 비율이 정상 범위 내에 있습니다.\n"
    else:
        report_md += "소음 구간 비율이 다소 높습니다. 수면 환경 개선을 권장합니다.\n"
    
    st.markdown(report_md)
    
    # 다운로드
    col1, col2 = st.columns(2)
    
    with col1:
        # 텍스트 보고서
        if st.button("💾 텍스트 보고서 저장"):
            report_file = f"results/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            os.makedirs('results', exist_ok=True)
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_md.replace('**', '').replace('###', '').replace('|', ''))
            
            st.success(f"✅ 저장 완료: {report_file}")
    
    with col2:
        # CSV 데이터
        if st.button("📊 CSV 데이터 다운로드"):
            csv_file = f"results/data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            os.makedirs('results', exist_ok=True)
            analyzer.data.to_csv(csv_file, index=False, encoding='utf-8')
            st.success(f"✅ 저장 완료: {csv_file}")


def show_settings():
    """설정 페이지"""
    st.header("⚙️ 설정")
    
    st.markdown("### 🎛️ 분석 설정")
    
    # 임계값 설정
    new_threshold = st.slider(
        "소음 임계값 (dB)",
        min_value=30.0,
        max_value=60.0,
        value=st.session_state.threshold,
        step=1.0,
        help="이 값 이상을 소음 구간으로 분류합니다"
    )
    
    if new_threshold != st.session_state.threshold:
        st.session_state.threshold = new_threshold
        st.success(f"✅ 임계값이 {new_threshold} dB로 변경되었습니다")
        
        # 기존 분석기가 있으면 재분석
        if st.session_state.analyzer is not None:
            st.info("💡 데이터를 다시 분석하려면 '📊 데이터 분석' 메뉴를 방문하세요")
    
    st.markdown("---")
    
    # 앱 정보
    st.markdown("### ℹ️ 앱 정보")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **수면 패턴 분석 시스템**
        
        버전: 1.0
        개발: 2025
        목적: 학교 탐구 프로젝트
        """)
    
    with col2:
        st.success("""
        **사용 기술**
        
        - Python
        - Streamlit
        - Pandas, Matplotlib
        - Scipy
        """)
    
    st.markdown("---")
    
    # 도움말
    with st.expander("❓ 도움말"):
        st.write("""
        ### 사용 방법
        
        1. **데이터 업로드**: dBMeter 앱에서 내보낸 CSV 파일 업로드
        2. **분석 실행**: 자동으로 통계 계산 및 그래프 생성
        3. **결과 확인**: 다양한 지표와 시각화로 수면 패턴 파악
        4. **보고서 생성**: 분석 결과를 파일로 저장
        
        ### 추천 임계값
        
        - **35-40 dB**: 매우 조용한 환경
        - **40-45 dB**: 일반적인 실내 환경
        - **45-50 dB**: 약간 시끄러운 환경
        
        ### 문제 해결
        
        - CSV 형식 오류: 파일이 `시간,dB` 형식인지 확인
        - 그래프가 안 보임: 데이터를 먼저 분석했는지 확인
        - 느린 성능: 데이터 크기가 너무 크면 일부만 사용
        """)


if __name__ == "__main__":
    main()
