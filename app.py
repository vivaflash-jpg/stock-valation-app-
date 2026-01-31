import streamlit as st
import FinanceDataReader as fdr
import OpenDartReader
import pandas as pd

# 스트림릿 페이지 설정
st.set_page_config(page_title="자동 데이터 연동 주식 계산기", layout="wide")

# API 키 입력 (실제 앱에서는 환경변수 처리가 좋습니다)
DART_API_KEY = st.sidebar.text_input("DART API 키를 입력하세요", type="password")

st.title("🤖 AI 자동 데이터 연동 적정주가 계산기")

# 입력 섹션
with st.sidebar:
    stock_code = st.text_input("종목코드 (예: 005930)", value="005930")
    target_per = st.number_input("적용할 PER (배)", min_value=0.0, value=10.0)
    safety_margin = st.slider("안전 마진 (%)", 0, 50, 20)

if DART_API_KEY:
    try:
        # 1. 현재가 및 종목 정보 가져오기
        stock_info = fdr.StockListing('KRX')
        stock_name = stock_info[stock_info['Code'] == stock_code]['Name'].values[0]
        
        df_price = fdr.DataReader(stock_code)
        current_price = df_price['Close'].iloc[-1]

        # 2. DART에서 재무제표(순이익) 가져오기
        dart = OpenDartReader(DART_API_KEY)
        # 가장 최근 연도 사업보고서 기준 당기순이익 추출
        fin_stat = dart.fin_state(stock_code, 2023) # 예시로 2023년 데이터
        net_income_row = fin_stat[(fin_stat['account_nm'] == '당기순이익') & (fin_stat['fs_div'] == 'CFS')]
        
        # 단위 변환 (DART는 보통 원 단위)
        net_income = int(net_income_row['thstrm_amount'].values[0].replace(',', ''))
        
        # 3. 주식수 가져오기
        report = dart.report(stock_code, '주식총수', 2023, '11011')
        total_shares = int(report.iloc[0]['total_stock_sts'].replace(',', ''))

        # 계산 로직
        fair_market_cap = net_income * target_per
        fair_price = fair_market_cap / total_shares
        buy_price = fair_price * (1 - safety_margin / 100)

        # 결과 대시보드
        st.header(f"📊 {stock_name} ({stock_code}) 분석 리포트")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("현재 주가", f"{int(current_price):,} 원")
        c2.metric("목표 적정주가", f"{int(fair_price):,} 원")
        c3.metric("매수 권장가", f"{int(buy_price):,} 원")

        # 괴리율 분석
        diff_ratio = ((fair_price - current_price) / current_price) * 100
        st.write(f"💡 현재가 대비 적정주가까지 **{diff_ratio:.1f}%**의 상승 여력이 있습니다.")

    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
else:
    st.warning("왼쪽 사이드바에 DART API 키를 입력해 주세요.")
    except Exception as e:
        st.error(f"오류 발생: {e}. 올바른 종목코드인지 확인해주세요.")
