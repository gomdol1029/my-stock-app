import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ------------------------------
# 페이지 기본 설정
# ------------------------------
st.set_page_config(
    page_title="주가 조회 서비스",
    page_icon="📈",
    layout="wide",
)

# ------------------------------
# 제목 및 설명
# ------------------------------
st.title("📈 나만의 주가 조회 서비스")
st.write(
    "종목 코드를 입력하면 주가 흐름을 그래프로 보여드려요. 종목 2개를 함께 입력하면 "
    "나란히 비교도 할 수 있어요. 예를 들어 삼성전자는 `005930.KS`, 애플은 `AAPL`을 입력해보세요 :)"
)

st.divider()

# ------------------------------
# 종목 입력창 (2개까지 비교)
# ------------------------------
col_input1, col_input2 = st.columns(2)

with col_input1:
    ticker_input_1 = st.text_input(
        "🔍 종목 코드 1",
        value="005930.KS",
        placeholder="예: 005930.KS (삼성전자)",
    )

with col_input2:
    ticker_input_2 = st.text_input(
        "🔍 종목 코드 2 (선택)",
        value="",
        placeholder="예: AAPL (애플)",
    )

# ------------------------------
# 조회 기간 선택 버튼
# ------------------------------
period_options = {
    "1개월": 30,
    "6개월": 182,
    "1년": 365,
    "5년": 365 * 5,
}

selected_period_label = st.radio(
    "📅 조회 기간을 선택하세요",
    options=list(period_options.keys()),
    index=2,  # 기본값: 1년
    horizontal=True,
)

selected_days = period_options[selected_period_label]

st.divider()

# 입력값 정리 (공백 제거, 빈 값 제외)
ticker_symbols = []
for raw in [ticker_input_1, ticker_input_2]:
    cleaned = raw.strip()
    if cleaned:
        ticker_symbols.append(cleaned)


# ------------------------------
# 종목 하나를 조회해서 화면에 그려주는 함수
# ------------------------------
def show_ticker(ticker_symbol: str, days: int, period_label: str):
    try:
        # yfinance로 데이터 불러오기
        end_date = datetime.today()
        start_date = end_date - timedelta(days=days)

        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(start=start_date, end=end_date)

        if df.empty:
            # 데이터가 없을 경우 (잘못된 종목 코드 등)
            st.error(
                "😢 해당 종목의 데이터를 찾을 수 없어요. 종목 코드를 다시 확인해주세요."
            )
            return

        # 종목 이름 가져오기 (없으면 코드로 대체)
        try:
            company_name = ticker.info.get("longName", ticker_symbol)
        except Exception:
            company_name = ticker_symbol

        # 현재가와 등락률 계산
        current_price = df["Close"].iloc[-1]   # 가장 최근 종가
        start_price = df["Close"].iloc[0]       # 기간 시작 시점 종가
        price_change = current_price - start_price
        percent_change = (price_change / start_price) * 100

        # 최고가·최저가·평균가 계산
        highest_price = df["Close"].max()
        lowest_price = df["Close"].min()
        average_price = df["Close"].mean()

        st.subheader(f"🏢 {company_name} ({ticker_symbol})")

        # 지표 카드 (현재가, 등락률)
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="현재가", value=f"{current_price:,.2f}")
        with col2:
            st.metric(
                label=f"{period_label} 등락률",
                value=f"{percent_change:,.2f}%",
                delta=f"{price_change:,.2f}",
            )

        # Plotly 꺾은선 그래프 그리기
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["Close"],
                mode="lines",
                name="종가",
                line=dict(color="#1f77b4", width=2),
            )
        )
        fig.update_layout(
            title=f"{company_name} {period_label} 주가 흐름",
            xaxis_title="날짜",
            yaxis_title="가격",
            hovermode="x unified",
            template="plotly_white",
            height=450,
        )
        st.plotly_chart(fig, use_container_width=True)

        # 최고가·최저가·평균가 카드 (그래프 아래)
        col3, col4, col5 = st.columns(3)
        with col3:
            st.metric(label="📈 최고가", value=f"{highest_price:,.2f}")
        with col4:
            st.metric(label="📉 최저가", value=f"{lowest_price:,.2f}")
        with col5:
            st.metric(label="📊 평균가", value=f"{average_price:,.2f}")

        # 원본 데이터 확인 (선택 사항)
        with st.expander("📋 원본 데이터 보기"):
            st.dataframe(df)

    except Exception as e:
        # 예상치 못한 오류가 발생했을 때 사용자에게 친절하게 안내
        st.error(f"⚠️ 데이터를 불러오는 중 문제가 발생했어요: {e}")


# ------------------------------
# 결과 화면 구성
# ------------------------------
if not ticker_symbols:
    st.info("👆 위에 종목 코드를 입력하면 주가 정보를 보여드릴게요.")
elif len(ticker_symbols) == 1:
    # 종목이 1개면 화면 전체 너비로 표시
    show_ticker(ticker_symbols[0], selected_days, selected_period_label)
else:
    # 종목이 2개면 나란히 비교
    compare_col1, compare_col2 = st.columns(2)
    with compare_col1:
        show_ticker(ticker_symbols[0], selected_days, selected_period_label)
    with compare_col2:
        show_ticker(ticker_symbols[1], selected_days, selected_period_label)

# ------------------------------
# 푸터
# ------------------------------
st.divider()
st.caption("데이터 출처: Yahoo Finance (yfinance) · 투자 판단은 신중하게 해주세요 🙏")
