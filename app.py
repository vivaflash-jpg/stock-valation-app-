import streamlit as st
import yfinance as yf
import FinanceDataReader as fdr

st.set_page_config(page_title="멀티 지표 주식 계산기", layout="wide")

st.title("⚖️ 지표별 맞춤형 적정주가 계산기")

# 1. 사이드바: 설정 및 지표 선택
with st.sidebar:
    st.header("🔍 분석 설정")
    ticker = st.text_input("종목코드 (예: NVDA, 000660)", value="NVDA").upper()
    
    # 지표 선택 라디오 버튼
    metric_choice = st.radio(
        "사용할 평가지표 선택",
        ('PER (수익성)', 'PSR (매출성)', 'PBR (자산성)')
    )
    
    target_multiple = st.number_input(f"적용할 {metric_choice[:3]} 배수", min_value=0.0, value=15.0, step=0.5)
    safety_margin = st.slider("안전 마진 (%)", 0, 50, 20)

# 2. 데이터 처리 함수
def get_advanced_data(ticker):
    # 미국/한국 구분 로직
    is_korea = not ticker.isalpha()
    search_ticker = f"{ticker}.KS" if is_korea else ticker
    
    stock = yf.Ticker(search_ticker)
    info = stock.info
    
    data = {
        "name": info.get('longName', ticker),
        "current_price": info.get('currentPrice') or info.get('regularMarketPrice'),
        "shares": info.get('sharesOutstanding'),
        "net_income": info.get('netIncomeToCommon'),
        "revenue": info.get('totalRevenue'),
        "book_value": info.get('totalAssets'), # 단순 자산총계 기준
        "currency": "₩" if is_korea else "$"
    }
    return data

# 3. 메인 로직 실행
if ticker:
    try:
        d = get_advanced_data(ticker)
        
        # 선택된 지표에 따른 가치 평가액(Valuation) 설정
        if 'PER' in metric_choice:
            base_value = d['net_income']
            label = "당기순이익"
        elif 'PSR' in metric_choice:
            base_value = d['revenue']
            label = "연간 매출액"
        else:
            base_value = d['book_value']
            label = "총 자산"

        if base_value and d['shares'] and d['current_price']:
            # 적정가 계산
            fair_price = (base_value * target_multiple) / d['shares']
            buy_price = fair_price * (1 - safety_margin / 100)
            upside = ((fair_price - d['current_price']) / d['current_price']) * 100

            # 결과 리포트
            st.header(f"📊 {d['name']} 분석 ({metric_choice[:3]} 기준)")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("현재가", f"{d['currency']} {d['current_price']:,.2f}")
            c2.metric("목표 적정주가", f"{d['currency']} {fair_price:,.2f}")
            c3.metric(f"매수가 (마진 {safety_margin}%)", f"{d['currency']} {buy_price:,.2f}")

            st.info(f"📌 기반 데이터: 최근 {label} {d['currency']} {base_value:,.0f}")

            # 가이드 메시지
            if upside > 0:
                st.success(f"✅ 현재가 대비 **{upside:.1f}%** 저평가 상태입니다.")
            else:
                st.warning(f"❌ 현재가 대비 **{abs(upside):.1f}%** 고평가 상태입니다.")
        else:
            st.error("선택한 지표를 위한 재무 데이터가 부족합니다.")

    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
