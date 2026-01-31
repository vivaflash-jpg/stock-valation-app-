import streamlit as st
import yfinance as yf
import FinanceDataReader as fdr

st.set_page_config(page_title="글로벌 주식 계산기 v3.1", layout="wide")
st.title("⚖️ 지표별 맞춤형 적정주가 계산기")

with st.sidebar:
    st.header("🔍 분석 설정")
    # 종목 코드를 입력받습니다 (예: NVDA, 005930)
    ticker_input = st.text_input("종목코드 입력 (한국은 숫자 6자리)", value="NVDA").upper()
    
    metric_choice = st.radio(
        "사용할 평가지표 선택",
        ('PER (수익성)', 'PSR (매출성)', 'PBR (자산성)')
    )
    target_multiple = st.number_input(f"적용할 {metric_choice[:3]} 배수", min_value=0.0, value=15.0, step=0.5)
    safety_margin = st.slider("안전 마진 (%)", 0, 50, 20)

def get_advanced_data(symbol):
    # 1. 한국 주식인지 확인 및 심볼 변환
    if symbol.isdigit():
        # 코스피/코스닥 구분 시도 (기본적으로 .KS를 시도하고 데이터 없으면 .KQ 시도)
        search_symbol = f"{symbol}.KS"
        stock = yf.Ticker(search_symbol)
        if not stock.info.get('currentPrice'):
            search_symbol = f"{symbol}.KQ"
            stock = yf.Ticker(search_symbol)
    else:
        search_symbol = symbol
        stock = yf.Ticker(search_symbol)

    info = stock.info
    
    # 2. 재무 데이터 추출 (다양한 키값 대응)
    # PBR을 위해 'Total Assets' 대신 'Book Value' 관련 데이터 사용
    data = {
        "name": info.get('longName') or info.get('shortName') or symbol,
        "current_price": info.get('currentPrice') or info.get('regularMarketPreviousClose'),
        "shares": info.get('sharesOutstanding'),
        "net_income": info.get('netIncomeToCommon') or info.get('netIncome'),
        "revenue": info.get('totalRevenue'),
        "book_value": info.get('totalStockholderEquity') or info.get('bookValue', 0) * info.get('sharesOutstanding', 0),
        "currency": "₩" if symbol.isdigit() else "$"
    }
    return data

if ticker_input:
    try:
        with st.spinner('데이터를 불러오는 중...'):
            d = get_advanced_data(ticker_input)
        
        # 지표별 값 할당 (데이터가 없을 경우 0 처리)
        metrics_map = {
            'PER (수익성)': (d['net_income'], "당기순이익"),
            'PSR (매출성)': (d['revenue'], "연간 매출액"),
            'PBR (자산성)': (d['book_value'], "순자산(자본)")
        }
        
        base_value, label = metrics_map[metric_choice]

        if base_value and d['shares'] and d['current_price']:
            fair_price = (base_value * target_multiple) / d['shares']
            buy_price = fair_price * (1 - safety_margin / 100)
            upside = ((fair_price - d['current_price']) / d['current_price']) * 100

            st.header(f"📊 {d['name']} 분석 결과")
            c1, c2, c3 = st.columns(3)
            c1.metric("현재가", f"{d['currency']} {d['current_price']:,.0f if d['currency']=='₩' else 2}")
            c2.metric("목표 적정주가", f"{d['currency']} {fair_price:,.0f if d['currency']=='₩' else 2}")
            c3.metric(f"매수 권장가", f"{d['currency']} {buy_price:,.0f if d['currency']=='₩' else 2}")
            
            st.info(f"📌 기반 데이터: 최근 {label} {d['currency']} {base_value:,.0f}")
        else:
            st.error(f"⚠️ {d['name']}의 {label} 또는 주식수 데이터를 찾을 수 없습니다. 다른 지표를 선택해 보세요.")

    except Exception as e:
        st.error(f"알 수 없는 오류가 발생했습니다: {e}")import streamlit as st
import yfinance as yf
import FinanceDataReader as fdr

st.set_page_config(page_title="글로벌 주식 계산기 v3.1", layout="wide")
st.title("⚖️ 지표별 맞춤형 적정주가 계산기")

with st.sidebar:
    st.header("🔍 분석 설정")
    # 종목 코드를 입력받습니다 (예: NVDA, 005930)
    ticker_input = st.text_input("종목코드 입력 (한국은 숫자 6자리)", value="NVDA").upper()
    
    metric_choice = st.radio(
        "사용할 평가지표 선택",
        ('PER (수익성)', 'PSR (매출성)', 'PBR (자산성)')
    )
    target_multiple = st.number_input(f"적용할 {metric_choice[:3]} 배수", min_value=0.0, value=15.0, step=0.5)
    safety_margin = st.slider("안전 마진 (%)", 0, 50, 20)

def get_advanced_data(symbol):
    # 1. 한국 주식인지 확인 및 심볼 변환
    if symbol.isdigit():
        # 코스피/코스닥 구분 시도 (기본적으로 .KS를 시도하고 데이터 없으면 .KQ 시도)
        search_symbol = f"{symbol}.KS"
        stock = yf.Ticker(search_symbol)
        if not stock.info.get('currentPrice'):
            search_symbol = f"{symbol}.KQ"
            stock = yf.Ticker(search_symbol)
    else:
        search_symbol = symbol
        stock = yf.Ticker(search_symbol)

    info = stock.info
    
    # 2. 재무 데이터 추출 (다양한 키값 대응)
    # PBR을 위해 'Total Assets' 대신 'Book Value' 관련 데이터 사용
    data = {
        "name": info.get('longName') or info.get('shortName') or symbol,
        "current_price": info.get('currentPrice') or info.get('regularMarketPreviousClose'),
        "shares": info.get('sharesOutstanding'),
        "net_income": info.get('netIncomeToCommon') or info.get('netIncome'),
        "revenue": info.get('totalRevenue'),
        "book_value": info.get('totalStockholderEquity') or info.get('bookValue', 0) * info.get('sharesOutstanding', 0),
        "currency": "₩" if symbol.isdigit() else "$"
    }
    return data

if ticker_input:
    try:
        with st.spinner('데이터를 불러오는 중...'):
            d = get_advanced_data(ticker_input)
        
        # 지표별 값 할당 (데이터가 없을 경우 0 처리)
        metrics_map = {
            'PER (수익성)': (d['net_income'], "당기순이익"),
            'PSR (매출성)': (d['revenue'], "연간 매출액"),
            'PBR (자산성)': (d['book_value'], "순자산(자본)")
        }
        
        base_value, label = metrics_map[metric_choice]

        if base_value and d['shares'] and d['current_price']:
            fair_price = (base_value * target_multiple) / d['shares']
            buy_price = fair_price * (1 - safety_margin / 100)
            upside = ((fair_price - d['current_price']) / d['current_price']) * 100

            st.header(f"📊 {d['name']} 분석 결과")
            c1, c2, c3 = st.columns(3)
            c1.metric("현재가", f"{d['currency']} {d['current_price']:,.0f if d['currency']=='₩' else 2}")
            c2.metric("목표 적정주가", f"{d['currency']} {fair_price:,.0f if d['currency']=='₩' else 2}")
            c3.metric(f"매수 권장가", f"{d['currency']} {buy_price:,.0f if d['currency']=='₩' else 2}")
            
            st.info(f"📌 기반 데이터: 최근 {label} {d['currency']} {base_value:,.0f}")
        else:
            st.error(f"⚠️ {d['name']}의 {label} 또는 주식수 데이터를 찾을 수 없습니다. 다른 지표를 선택해 보세요.")

    except Exception as e:
        st.error(f"알 수 없는 오류가 발생했습니다: {e}")
