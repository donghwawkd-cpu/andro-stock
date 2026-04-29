# 모의주식 게임 만들기
import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# 1. 사이트 기본 설정 (페이지 설정이 가장 먼저 와야 함)
st.set_page_config(page_title="안드로 주식게임", layout="wide", initial_sidebar_state="expanded")

# ⭐ 우주 배경 및 주식 앱 감성 커스텀 CSS 적용
st.markdown("""
<style>
/* 우주 배경 (다크 톤) */
.stApp {
    background-color: #0b0f19;
    background-image: 
        radial-gradient(white, rgba(255,255,255,.2) 2px, transparent 40px),
        radial-gradient(white, rgba(255,255,255,.15) 1px, transparent 30px),
        radial-gradient(white, rgba(255,255,255,.1) 2px, transparent 40px);
    background-size: 550px 550px, 350px 350px, 250px 250px;
    background-position: 0 0, 40px 60px, 130px 270px;
    color: #e2e8f0;
}

/* 카드 뷰(컨테이너) 디자인 - 실제 트레이딩 앱 느낌 */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(17, 24, 39, 0.85) !important;
    border: 1px solid #374151 !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5) !important;
}

/* 제목 및 텍스트 색상 조정 */
h1, h2, h3 {
    color: #f8fafc !important;
    font-weight: 700 !important;
}

/* 메트릭(자산, 수익률 등) 박스 디자인 */
[data-testid="stMetricValue"] {
    font-weight: 800 !important;
}

/* 버튼 모서리 둥글게 및 호버 효과 */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease-in-out;
}
.stButton > button:hover {
    transform: translateY(-2px);
}
</style>
""", unsafe_allow_html=True)

constellations = [
    '양자리', '황소자리', '쌍둥이자리', '게자리', 
    '사자자리', '처녀자리', '천칭자리', '전갈자리', 
    '사수자리', '염소자리', '물병자리', '물고기자리'
]
special_coin = '안드로 코인'
all_assets = constellations + [special_coin]

# ⭐ 시대별 12궁도 고정 주가 데이터베이스 (필요한 연도 데이터 유지)
yearly_prices = {
    1997: {'양자리': 800, '황소자리': 500, '쌍둥이자리': 300, '게자리': 400, '사자자리': 1200, '처녀자리': 600, '천칭자리': 100, '전갈자리': 150, '사수자리': 200, '염소자리': 100, '물병자리': 500, '물고기자리': 200},
    1999: {'양자리': 2500, '황소자리': 1800, '쌍둥이자리': 500, '게자리': 600, '사자자리': 1500, '처녀자리': 800, '천칭자리': 300, '전갈자리': 500, '사수자리': 400, '염소자리': 200, '물병자리': 5000, '물고기자리': 800},
    2024: {'양자리': 75000, '황소자리': 150000, '쌍둥이자리': 180000, '게자리': 55000, '사자자리': 200000, '처녀자리': 110000, '천칭자리': 85000, '전갈자리': 180000, '사수자리': 400000, '염소자리': 150000, '물병자리': 180000, '물고기자리': 200000},
    2025: {'양자리': 85000, '황소자리': 180000, '쌍둥이자리': 250000, '게자리': 60000, '사자자리': 220000, '처녀자리': 130000, '천칭자리': 90000, '전갈자리': 200000, '사수자리': 350000, '염소자리': 120000, '물병자리': 190000, '물고기자리': 250000},
    2026: {'양자리': 95000, '황소자리': 220000, '쌍둥이자리': 300000, '게자리': 70000, '사자자리': 250000, '처녀자리': 150000, '천칭자리': 100000, '전갈자리': 230000, '사수자리': 450000, '염소자리': 200000, '물병자리': 220000, '물고기자리': 300000}
}

# 2. 서버 공용 메모리 설정
@st.cache_resource
def get_global_state():
    # ⭐ 총 4번의 시간여행 (5개 연도) 하드코딩
    fixed_sequence = [2024, 1997, 1999, 2025, 2026]
    first_year = fixed_sequence[0]
    init_prices = yearly_prices[first_year].copy()
    init_prices[special_coin] = 1000 

    return {
        "year_sequence": fixed_sequence, 
        "current_turn_idx": 0,              
        "prices": init_prices,
        "prev_prices": init_prices.copy(),
        "users": {},
        "is_game_over": False               
    }

global_state = get_global_state()

# 3. 로그인 시스템
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌌 안드로 주식게임")
    st.info("4번의 시공간 이동! 시드머니 1,000만 원으로 시작합니다.")
    
    col1, col2 = st.columns(2)
    with col1:
        user_input = st.text_input("참가자 이름", key="user_login")
        if st.button("참가자 접속", use_container_width=True) and user_input:
            if user_input not in global_state["users"]:
                global_state["users"][user_input] = {
                    "cash": 10000000, 
                    "portfolio": {s: 0 for s in all_assets}
                }
            st.session_state.user_role = "user"
            st.session_state.user_id = user_input
            st.session_state.logged_in = True
            st.rerun()
                
    with col2:
        admin_pw = st.text_input("관리자 암호", type="password", key="admin_login")
        if st.button("관리자 접속", use_container_width=True) and admin_pw == "andro":
            st.session_state.user_role = "admin"
            st.session_state.user_id = "관리자"
            st.session_state.logged_in = True
            st.rerun()

# 4. 메인 게임 로직
else:
    turn_idx = global_state["current_turn_idx"]
    year_list = global_state["year_sequence"]
    current_year = year_list[turn_idx]
    current_prices = global_state["prices"]
    prev_prices = global_state["prev_prices"]
    is_game_over = global_state["is_game_over"]
    
    st.sidebar.title(f"👤 {st.session_state.user_id}님")
    st.sidebar.subheader(f"📅 {turn_idx + 1} / {len(year_list)} 라운드")
    st.sidebar.markdown(f"### 현재 시대: **{current_year}년**")

    # ----------------------------------------
    # [관리자 모드]
    # ----------------------------------------
    if st.session_state.user_role == "admin":
        st.title("⚙️ 중앙 통제실")
        
        st.markdown("### 🏆 참가자 자산 현황")
        user_data_list = []
        for name, data in global_state["users"].items():
            total_stock_value = sum(data["portfolio"][s] * current_prices[s] for s in all_assets)
            total_assets = data["cash"] + total_stock_value
            user_data_list.append({"이름": name, "총 자산": total_assets, "현금": data["cash"]})
        
        if user_data_list:
            df_users = pd.DataFrame(user_data_list).sort_values(by="총 자산", ascending=False)
            st.dataframe(df_users, use_container_width=True, hide_index=True)
            if st.button("🔄 랭킹판 강제 새로고침"):
                st.rerun()

        st.divider()

        st.markdown("### 🚀 시공간 이동 (다음 라운드)")
        if not is_game_over:
            with st.container(border=True):
                next_year_label = year_list[turn_idx+1] if turn_idx < len(year_list)-1 else '종료'
                st.write(f"**목적지:** {next_year_label}년")
                
                reserved_coin_price = st.number_input(
                    "💡 다음 라운드 도착 시 '안드로 코인' 설정 가격", 
                    value=current_prices[special_coin], step=500, key="reserve_coin"
                )
                
                if st.button(f"🚀 {next_year_label}년으로 점프 실행!", type="primary", use_container_width=True):
                    if turn_idx < len(year_list) - 1:
                        global_state["prev_prices"] = global_state["prices"].copy()
                        global_state["current_turn_idx"] += 1
                        new_year = year_list[global_state["current_turn_idx"]]
                        
                        for stock in constellations:
                            global_state["prices"][stock] = yearly_prices[new_year][stock]
                        global_state["prices"][special_coin] = reserved_coin_price
                        st.rerun()
                    else:
                        global_state["is_game_over"] = True
                        st.rerun()

        st.divider()

        st.markdown("### 💹 현재 시장 강제 조작 (즉시 반영)")
        st.caption("라운드를 넘기지 않고 현재 시대에서 가격만 폭락/폭등 시킬 때 사용하세요.")
        
        if st.session_state.get("last_sync_year") != current_year:
            for s in all_assets:
                st.session_state[f"edit_{s}"] = current_prices[s]
            st.session_state["last_sync_year"] = current_year

        with st.form("admin_price_form"):
            st.number_input("🪙 안드로 코인", step=500, key=f"edit_{special_coin}")
            
            cols = st.columns(4)
            for i, stock in enumerate(constellations):
                with cols[i % 4]:
                    st.number_input(f"{stock}", step=100, key=f"edit_{stock}")
            
            submit = st.form_submit_button("✅ 설정한 가격으로 전원 즉시 반영", use_container_width=True)
            if submit:
                global_state["prev_prices"] = global_state["prices"].copy()
                for s in all_assets:
                    global_state["prices"][s] = st.session_state[f"edit_{s}"]
                st.success("시장 가격이 성공적으로 업데이트되었습니다!")
                st.rerun()

    # ----------------------------------------
    # [참가자 모드]
    # ----------------------------------------
    elif st.session_state.user_role == "user":
        st_autorefresh(interval=3000, limit=None, key="user_refresh")
        
        # 상단 네비게이션
        head_c1, head_c2 = st.columns([4, 1])
        with head_c2:
            if st.button("🔄 수동 동기화", use_container_width=True):
                st.rerun()

        my_id = st.session_state.user_id
        my_data = global_state["users"][my_id]
        
        # 총 자산 및 수익률 계산
        total_stock_value = sum(my_data["portfolio"][s] * current_prices[s] for s in all_assets)
        total_assets = my_data["cash"] + total_stock_value
        initial_cash = 10000000 
        total_profit = total_assets - initial_cash
        roi_pct = (total_profit / initial_cash) * 100

        if is_game_over:
            st.title("🏁 게임 종료!")
            st.header(f"🎊 최종 자산: {total_assets:,}원")
            st.balloons()
        else:
            st.title(f"📈 {current_year}년 주식시장")
            
            # 내 자산 요약
            with st.container(border=True):
                m1, m2, m3 = st.columns(3)
                m1.metric("내 총 자산", f"{total_assets:,}원", delta=f"{total_profit:,}원", delta_color="inverse")
                m2.metric("보유 현금", f"{my_data['cash']:,}원")
                m3.metric("누적 수익률", f"{roi_pct:+.2f}%", delta=f"{roi_pct:+.2f}%p", delta_color="inverse")
            
            st.divider()

            # ⭐ 거래 입력창용 공통 함수 (콜백 로직 적용 완료)
            def render_trading_ui(asset_name, current_price, owned_qty):
                b_key = f"buy_amt_{asset_name}"
                s_key = f"sell_amt_{asset_name}"
                
                max_buyable = my_data["cash"] // current_price
                max_sellable = owned_qty

                # --- 🛠️ 콜백(Callback) 함수 정의 ---
                # 1. 50% / MAX 수량 자동 입력 콜백
                def set_amt(key, val):
                    st.session_state[key] = val

                # 2. 매수/매도 실행 콜백 (화면 렌더링 전 즉시 처리)
                def execute_trade(action, key, price):
                    amt = st.session_state.get(key, 0)
                    current_owned = global_state["users"][my_id]["portfolio"][asset_name]
                    
                    if action == "buy":
                        if amt > 0 and amt * price <= global_state["users"][my_id]["cash"]:
                            global_state["users"][my_id]["cash"] -= amt * price
                            global_state["users"][my_id]["portfolio"][asset_name] += amt
                            st.session_state[key] = 0 # 거래 성공 시 입력창 0으로 초기화
                        else:
                            st.toast("⚠️ 현금이 부족하거나 수량을 확인하세요!", icon="🚨")
                    elif action == "sell":
                        if amt > 0 and amt <= current_owned:
                            global_state["users"][my_id]["cash"] += amt * price
                            global_state["users"][my_id]["portfolio"][asset_name] -= amt
                            st.session_state[key] = 0 # 거래 성공 시 입력창 0으로 초기화
                        else:
                            st.toast("⚠️ 보유량이 부족하거나 수량을 확인하세요!", icon="🚨")

                # --- 메트릭 표시 (상단) ---
                asset_diff = current_price - prev_prices[asset_name]
                asset_pct = (asset_diff / prev_prices[asset_name] * 100) if prev_prices[asset_name] != 0 else 0
                
                c1, c2 = st.columns([1, 1])
                with c1:
                    st.metric(
                        label=f"🌌 {asset_name}" if asset_name != special_coin else f"🪙 {asset_name}", 
                        value=f"{current_price:,}원", 
                        delta=f"{asset_diff:,}원 ({asset_pct:+.2f}%)", 
                        delta_color="inverse"
                    )
                with c2:
                    st.markdown(f"<div style='text-align: right; padding-top: 20px; color: #9ca3af;'>보유량: <b style='color: white;'>{owned_qty}주</b></div>", unsafe_allow_html=True)
                
                st.markdown("<hr style='margin: 5px 0px 15px 0px; border-color: #374151;'>", unsafe_allow_html=True)

                trade_c1, trade_c2 = st.columns(2)
                
                # --- 🔴 매수(Buy) 구역 ---
                with trade_c1:
                    st.markdown(f"<span style='color: #ef4444; font-weight: bold;'>매수</span> (최대 {max_buyable:,}주)", unsafe_allow_html=True)
                    
                    buy_amt = st.number_input("수량", min_value=0, step=1, key=b_key, label_visibility="collapsed")
                    
                    btn_c1, btn_c2, btn_c3 = st.columns([1, 1, 2])
                    btn_c1.button("50%", key=f"b_50_{asset_name}", on_click=set_amt, args=(b_key, max_buyable // 2))
                    btn_c2.button("MAX", key=f"b_max_{asset_name}", on_click=set_amt, args=(b_key, max_buyable))
                    
                    # 실행 버튼 클릭 시 콜백 함수 즉시 호출
                    btn_c3.button("🔴 매수 실행", key=f"b_exec_{asset_name}", type="primary", use_container_width=True, on_click=execute_trade, args=("buy", b_key, current_price))
                    
                    st.caption(f"예상 비용: -{buy_amt * current_price:,}원")

                # --- 🔵 매도(Sell) 구역 ---
                with trade_c2:
                    st.markdown(f"<span style='color: #3b82f6; font-weight: bold;'>매도</span> (보유 {max_sellable:,}주)", unsafe_allow_html=True)
                    
                    sell_amt = st.number_input("수량", min_value=0, step=1, key=s_key, label_visibility="collapsed")
                    
                    btn_c1, btn_c2, btn_c3 = st.columns([1, 1, 2])
                    btn_c1.button("50%", key=f"s_50_{asset_name}", on_click=set_amt, args=(s_key, max_sellable // 2))
                    btn_c2.button("MAX", key=f"s_max_{asset_name}", on_click=set_amt, args=(s_key, max_sellable))
                    
                    # 실행 버튼 클릭 시 콜백 함수 즉시 호출
                    btn_c3.button("🔵 매도 실행", key=f"s_exec_{asset_name}", use_container_width=True, on_click=execute_trade, args=("sell", s_key, current_price))
                            
                    st.caption(f"예상 수익: +{sell_amt * current_price:,}원")

            # 🪙 스페셜 코인
            st.markdown("### 💎 스페셜 마켓")
            with st.container(border=True):
                render_trading_ui(special_coin, current_prices[special_coin], my_data["portfolio"][special_coin])

            # 🌌 12궁도 주식
            st.markdown("### 🛒 12궁도 거래소")
            display_cols = st.columns(2)
            for i, stock in enumerate(constellations):
                with display_cols[i % 2]:
                    with st.container(border=True):
                        render_trading_ui(stock, current_prices[stock], my_data["portfolio"][stock])

    if st.sidebar.button("🚪 로그아웃", use_container_width=True):
        st.session_state.clear()
        st.rerun()
