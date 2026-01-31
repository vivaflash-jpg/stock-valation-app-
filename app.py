import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="히스토리컬 주식 계산기 v4.0", layout="wide")
st.title("📊 과거 5년 평균 배수 기반 적정주가 계산기")

# 1. 사이드바 입력
with st.sidebar:
    st.header("🔍 분석 설정")
    ticker_input = st.text_input("종목코드 입력 (예: AAPL, 005930)", value="AAPL").upper()
    metric_choice = st.radio("평가지표", ('PER', 'PSR', 'PBR'))
    safety_margin = st.slider("안전 마진 (%)", 0, 50, 20)

# 2. 데이터 수집 및 과거 배수 계산 함수
def get_historical_multiple(symbol, mode):
    # 한국 주식 처리
    search_symbol = f"{symbol}.KS" if symbol.isdigit() else symbol
    stock = yf.Ticker(search_symbol)
    
    # 과거 연간 재무제표 (최대 4-5년 제공)
    if mode == 'PER':
        hist_data = stock.financials.loc['Net Income']
    elif mode == 'PSR':
        hist_data = stock.financials.loc['Total Revenue']
    else: # PBR
        hist_data = stock.balance_sheet.loc['Stockholders Equity']
    
    # 과거 주가 (연말 기준 시가총액 계산용)
    shares = stock.info.get('sharesOutstanding')
    multiples = []
    
    for date in hist_data.index:
        year = date.year
        # 해당 연도말 주가 가져오기 (대략적 산출)
        end_of_year = f"{year}-12-30"
        price_hist = stock.history(start=f"{year}-12-01", end=f"{year}-12-31")
        if not price_hist.empty:
            avg_price = price_hist['Close'].mean()
            val = hist_data[date]
            if val and val > 0:
                m = (avg_price * shares) / val
                multiples.append(m)
                
    avg_m = sum(multiples) / len(multiples) if multiples else 15.0 # 기본값 15
    return stock.info, avg_m

# 3. 메인 실행부
if ticker_input:
    try:
        with st.spinner('5년치 데이터를 분석 중입니다...'):
            info, recommended_m = get_historical_multiple(ticker_input, metric_choice)
        
        # 추천 배수를 입력창의 기본값으로 사용하거나 별도 표시
        st.sidebar.success(f"💡 추천 {metric_choice}: {recommended_m:.2f}배 (5년 평균)")
        target_multiple = st.sidebar.number_input(f"적용할 {metric_choice} 배수", value=float(round(recommended_m, 2)))

        # 현재 데이터 가져오기
        curr_price = info.get('currentPrice') or info.get('regularMarketPreviousClose')
        shares = info.get('sharesOutstanding')
        
        if metric_choice == 'PER':
            base_val = info.get('netIncomeToCommon')
        elif metric_choice == 'PSR':
            base_val = info.get('totalRevenue')
        else:
            base_val = info.get('totalStockholderEquity')

        if base_val and shares and curr_price:
            fair_price = (base_val * target_multiple) / shares
            buy_price = fair_price * (1 - safety_margin / 100)
            
            # 결과 표시
            st.subheader(f"📈 {info.get('longName')} 분석 (5년 평균 {metric_choice} 반영)")
            col1, col2, col3 = st.columns(3)
            col1.metric("현재가", f"{int(curr_price):,}")
            col2.metric(f"목표가 (멀티플 {target_multiple:.1f})", f"{int(fair_price):,}")
            col3.metric("매수 권장가", f"{int(buy_price):,}")
            
            upside = ((fair_price - curr_price) / curr_price) * 100
            st.progress(min(max(upside/100, 0.0), 1.0))
            st.write(f"현재가 대비 예상 상승 여력: **{upside:.1f}%**")
            
    except Exception as e:
        st.error(f"데이터 분석 중 오류가 발생했습니다. (재무제표가 비공개된 종목일 수 있습니다.)")
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
