import streamlit as st
import yfinance as yf

st.set_page_config(page_title="주식 계산기 v4.1 (Fix)", layout="wide")
st.title("📊 지표별 적정주가 계산기 (오류 수정판)")

# 1. 사이드바 설정
with st.sidebar:
    st.header("🔍 분석 설정")
    # 종목코드: 한국은 숫자만, 미국은 티커 입력
    ticker_input = st.text_input("종목코드 입력 (예: AAPL, 005930)", value="005930").upper()
    
    metric_choice = st.radio("평가지표", ('PER (수익성)', 'PSR (매출성)', 'PBR (자산성)'))
    
    # 지표별 기본 멀티플값 자동 조정 (PBR은 보통 1.0 내외이므로)
    default_multiple = 1.0 if 'PBR' in metric_choice else 15.0
    target_multiple = st.number_input(f"적용할 배수 (Multiple)", value=default_multiple, step=0.1)
    
    safety_margin = st.slider("안전 마진 (%)", 0, 50, 20)

# 2. 데이터 추출 함수 (안전장치 강화)
def get_stock_data(symbol):
    # 한국 주식 처리 로직
    if symbol.isdigit():
        # 1차 시도: 코스피 (.KS)
        stock = yf.Ticker(f"{symbol}.KS")
        info = stock.info
        # 데이터가 없으면 2차 시도: 코스닥 (.KQ)
        if not info or 'regularMarketPrice' not in info:
            stock = yf.Ticker(f"{symbol}.KQ")
            info = stock.info
        currency = "₩"
    else:
        # 미국 주식
        stock = yf.Ticker(symbol)
        info = stock.info
        currency = "$"

    # 필수 데이터 추출 (None 방지)
    current_price = info.get('currentPrice') or info.get('regularMarketPreviousClose') or info.get('regularMarketPrice')
    shares = info.get('sharesOutstanding')

    # PBR 핵심 수정: 자본총계가 없으면 (BPS * 주식수)로 계산
    book_value = info.get('totalStockholderEquity')
    if book_value is None:
        bps = info.get('bookValue')
        if bps and shares:
            book_value = bps * shares

    data = {
        "name": info.get('longName') or info.get('shortName') or symbol,
        "current_price": current_price,
        "shares": shares,
        "net_income": info.get('netIncomeToCommon') or info.get('netIncome'), # PER용
        "revenue": info.get('totalRevenue'), # PSR용
        "equity": book_value, # PBR용
        "currency": currency
    }
    return data

# 3. 메인 실행부
if ticker_input:
    try:
        with st.spinner('데이터를 분석 중입니다...'):
            d = get_stock_data(ticker_input)
        
        # 선택한 지표에 따른 기준값(Base Value) 설정
        if 'PER' in metric_choice:
            base_val = d['net_income']
            label = "당기순이익"
        elif 'PSR' in metric_choice:
            base_val = d['revenue']
            label = "연간 매출액"
        else: # PBR
            base_val = d['equity']
            label = "순자산(자본총계)"

        # 4. 계산 및 출력
        if base_val and d['shares'] and d['current_price']:
            # 적정 시가총액 & 주가 계산
            fair_market_cap = base_val * target_multiple
            fair_price = fair_market_cap / d['shares']
            buy_price = fair_price * (1 - safety_margin / 100)
            
            # 상승여력
            upside = ((fair_price - d['current_price']) / d['current_price']) * 100

            # 화면 표시
            st.subheader(f"📈 {d['name']} ({ticker_input}) 분석")
            
            # 숫자 포맷팅 (한국 돈은 소수점 없이, 달러는 소수점 2자리)
            fmt = ",.0f" if d['currency'] == "₩" else ",.2f"

            c1, c2, c3 = st.columns(3)
            c1.metric("현재가", f"{d['currency']} {format(d['current_price'], fmt)}")
            c2.metric("목표 적정주가", f"{d['currency']} {format(fair_price, fmt)}")
            c3.metric("매수 권장가", f"{d['currency']} {format(buy_price, fmt)}")

            st.divider()
            
            # 결과 해석
            if upside > 0:
                st.success(f"🚀 현재가 대비 **{upside:.1f}%** 상승 여력이 있습니다.")
            else:
                st.warning(f"⚠️ 현재가가 적정가보다 **{abs(upside):.1f}%** 높습니다.")
                
            st.info(f"📌 [데이터 확인] {label}: {d['currency']} {base_val:,.0f} / 발행주식수: {d['shares']:,}")
            
        else:
            st.error(f"❌ '{d['name']}'의 재무 데이터({label})를 불러올 수 없습니다. (적자 기업이거나 데이터 누락)")

    except Exception as e:
        st.error(f"오류 발생: {e}. 올바른 종목코드인지 확인해주세요.")
