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
    "종목 코드를 입력하면 최근 1년간의 주가 흐름을 그래프로 보여드려요. "
    "예를 들어 삼성전자는 `005930.KS`, 애플은 `AAPL`을 입력해보세요 :)"
)

st.divider()

# ------------------------------
# 종목 입력창
# ------------------------------
ticker_input = st.text_input(
    "🔍 종목 코드를 입력하세요",
    value="005930.KS",
    placeholder="예: 005930.KS (삼성전자), AAPL (애플)",
)

# 입력값 앞뒤 공백 제거
ticker_symbol = ticker_input.strip()

if ticker_symbol:
    try:
        # ------------------------------
        # yfinance로 데이터 불러오기 (최근 1년)
        # ------------------------------
        end_date = datetime.today()
        start_date = end_date - timedelta(days=365)

        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(start=start_date, end=end_date)

        if df.empty:
            # 데이터가 없을 경우 (잘못된 종목 코드 등)
            st.error(
                "😢 해당 종목의 데이터를 찾을 수 없어요. 종목 코드를 다시 확인해주세요."
            )
        else:
            # ------------------------------
            # 종목 이름 가져오기 (없으면 코드로 대체)
            # ------------------------------
            try:
                company_name = ticker.info.get("longName", ticker_symbol)
            except Exception:
                company_name = ticker_symbol

            # ------------------------------
            # 현재가와 1년 등락률 계산
            # ------------------------------
            current_price = df["Close"].iloc[-1]      # 가장 최근 종가
            start_price = df["Close"].iloc[0]          # 1년 전 종가
            price_change = current_price - start_price
            percent_change = (price_change / start_price) * 100

            st.subheader(f"🏢 {company_name} ({ticker_symbol})")

            # ------------------------------
            # 지표 카드 (현재가, 1년 등락률)
            # ------------------------------
            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    label="현재가",
                    value=f"{current_price:,.2f}",
                )

            with col2:
                st.metric(
                    label="1년 등락률",
                    value=f"{percent_change:,.2f}%",
                    delta=f"{price_change:,.2f}",
                )

            st.divider()

            # ------------------------------
            # Plotly 꺾은선 그래프 그리기
            # ------------------------------
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
                title=f"{company_name} 최근 1년 주가 흐름",
                xaxis_title="날짜",
                yaxis_title="가격",
                hovermode="x unified",
                template="plotly_white",
                height=500,
            )

            st.plotly_chart(fig, use_container_width=True)

            # ------------------------------
            # 원본 데이터 확인 (선택 사항)
            # ------------------------------
            with st.expander("📋 원본 데이터 보기"):
                st.dataframe(df)

    except Exception as e:
        # 예상치 못한 오류가 발생했을 때 사용자에게 친절하게 안내
        st.error(f"⚠️ 데이터를 불러오는 중 문제가 발생했어요: {e}")
else:
    st.info("👆 위에 종목 코드를 입력하면 주가 정보를 보여드릴게요.")

# ------------------------------
# 푸터
# ------------------------------
st.divider()
st.caption("데이터 출처: Yahoo Finance (yfinance) · 투자 판단은 신중하게 해주세요 🙏")
