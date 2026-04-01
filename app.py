import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# 1. 사이트 기본 설정
st.set_page_config(page_title="안드로 주식게임", layout="wide")

constellations = [
    '양자리', '황소자리', '쌍둥이자리', '게자리', 
    '사자자리', '처녀자리', '천칭자리', '전갈자리', 
    '사수자리', '염소자리', '물병자리', '물고기자리'
]
special_coin = '안드로 코인'
all_assets = constellations + [special_coin]

# ⭐ 시대별 12궁도 고정 주가 데이터베이스
yearly_prices = {
    1997: {'양자리': 800, '황소자리': 500, '쌍둥이자리': 300, '게자리': 400, '사자자리': 1200, '처녀자리': 600, '천칭자리': 100, '전갈자리': 150, '사수자리': 200, '염소자리': 100, '물병자리': 500, '물고기자리': 200},
    1998: {'양자리': 500, '황소자리': 300, '쌍둥이자리': 200, '게자리': 250, '사자자리': 800, '처녀자리': 400, '천칭자리': 150, '전갈자리': 200, '사수자리': 250, '염소자리': 150, '물병자리': 800, '물고기자리': 300},
    1999: {'양자리': 2500, '황소자리': 1800, '쌍둥이자리': 500, '게자리': 600, '사자자리': 1500, '처녀자리': 800, '천칭자리': 300, '전갈자리': 500, '사수자리': 400, '염소자리': 200, '물병자리': 5000, '물고기자리': 800},
    2003: {'양자리': 4000, '황소자리': 2500, '쌍둥이자리': 800, '게자리': 900, '사자자리': 2200, '처녀자리': 1200, '천칭자리': 800, '전갈자리': 1200, '사수자리': 1000, '염소자리': 500, '물병자리': 2000, '물고기자리': 1500},
    2004: {'양자리': 5500, '황소자리': 3500, '쌍둥이자리': 1200, '게자리': 1500, '사자자리': 3000, '처녀자리': 1800, '천칭자리': 1500, '전갈자리': 2500, '사수자리': 1800, '염소자리': 800, '물병자리': 3500, '물고기자리': 2200},
    2005: {'양자리': 7000, '황소자리': 4500, '쌍둥이자리': 1800, '게자리': 2000, '사자자리': 4500, '처녀자리': 2500, '천칭자리': 2500, '전갈자리': 4000, '사수자리': 3000, '염소자리': 1500, '물병자리': 6000, '물고기자리': 4000},
    2024: {'양자리': 75000, '황소자리': 150000, '쌍둥이자리': 180000, '게자리': 55000, '사자자리': 200000, '처녀자리': 110000, '천칭자리': 85000, '전갈자리': 180000, '사수자리': 400000, '염소자리': 150000, '물병자리': 180000, '물고기자리': 200000},
    2025: {'양자리': 85000, '황소자리': 180000, '쌍둥이자리': 250000, '게자리': 60000, '사자자리': 220000, '처녀자리': 130000, '천칭자리': 90000, '전갈자리': 200000, '사수자리': 350000, '염소자리': 120000, '물병자리': 190000, '물고기자리': 250000},
    2026: {'양자리': 95000, '황소자리': 220000, '쌍둥이자리': 300000, '게자리': 70000, '사자자리': 250000, '처녀자리': 150000, '천칭자리': 100000, '전갈자리': 230000, '사수자리': 450000, '염소자리': 200000, '물병자리': 220000, '물고기자리': 300000}
}

# 2. 서버 공용 메모리 설정
@st.cache_resource
def get_global_state():
    fixed_sequence = [2024, 2025, 2003, 2004, 2005, 1997, 1998, 1999, 2026]
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
    st.info("9번의 시간 여행! 시드머니 1,000만 원으로 시작합니다.")
    
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
        if st.button("🔄 화면이 멈췄다면 누르세요 (수동 동기화)", use_container_width=True):
            st.rerun()

        my_id = st.session_state.user_id
        my_data = global_state["users"][my_id]
        total_stock_value = sum(my_data["portfolio"][s] * current_prices[s] for s in all_assets)
        total_assets = my_data["cash"] + total_stock_value

        if is_game_over:
            st.title("🏁 게임 종료!")
            st.header(f"🎊 최종 자산: {total_assets:,}원")
            st.balloons()
        else:
            st.title(f"📈 {current_year}년 주식시장")
            m1, m2, m3 = st.columns(3)
            m1.metric("총 자산", f"{total_assets:,}원")
            m2.metric("현금 잔고", f"{my_data['cash']:,}원")
            m3.metric("수익률", f"{(total_assets-10000000)/100000:+.2f}%")
            
            st.divider()

            # ⭐ 코인 거래
            with st.container(border=True):
                coin_diff = current_prices[special_coin] - prev_prices[special_coin]
                st.metric(label="🪙 안드로 코인", value=f"{current_prices[special_coin]:,}원", delta=f"{coin_diff:,}원")
                owned_coin = my_data["portfolio"][special_coin]
                st.caption(f"내 보유량: **{owned_coin}개**")
                
                c1, c2 = st.columns(2)
                with c1:
                    b_amt = st.number_input("매수 수량", min_value=0, step=1, key="b_coin")
                    st.caption(f"예상: -{b_amt * current_prices[special_coin]:,}원")
                    
                    # 일반 매수 / MAX 매수 버튼 분리
                    b_col1, b_col2 = st.columns(2)
                    if b_col1.button("매수", key="btn_b_coin", use_container_width=True):
                        if b_amt > 0 and b_amt * current_prices[special_coin] <= my_data["cash"]:
                            global_state["users"][my_id]["cash"] -= b_amt * current_prices[special_coin]
                            global_state["users"][my_id]["portfolio"][special_coin] += b_amt
                            st.rerun()
                        else:
                            st.error("현금 부족!")
                    
                    if b_col2.button("MAX", key="btn_max_b_coin", type="primary", use_container_width=True):
                        max_qty = my_data["cash"] // current_prices[special_coin] # 살 수 있는 최대 수량 계산
                        if max_qty > 0:
                            global_state["users"][my_id]["cash"] -= max_qty * current_prices[special_coin]
                            global_state["users"][my_id]["portfolio"][special_coin] += max_qty
                            st.rerun()
                        else:
                            st.error("현금 부족!")

                with c2:
                    s_amt = st.number_input("매도 수량", min_value=0, step=1, key="s_coin")
                    st.caption(f"예상: +{s_amt * current_prices[special_coin]:,}원")
                    
                    # 일반 매도 / MAX 매도 버튼 분리
                    s_col1, s_col2 = st.columns(2)
                    if s_col1.button("매도", key="btn_s_coin", use_container_width=True):
                        if s_amt > 0 and s_amt <= owned_coin:
                            global_state["users"][my_id]["cash"] += s_amt * current_prices[special_coin]
                            global_state["users"][my_id]["portfolio"][special_coin] -= s_amt
                            st.rerun()
                        else:
                            st.error("수량 부족!")
                            
                    if s_col2.button("MAX", key="btn_max_s_coin", type="primary", use_container_width=True):
                        if owned_coin > 0:
                            global_state["users"][my_id]["cash"] += owned_coin * current_prices[special_coin]
                            global_state["users"][my_id]["portfolio"][special_coin] = 0 # 전량 매도
                            st.rerun()
                        else:
                            st.error("보유량 없음!")

            # ⭐ 12궁도 주식 거래
            st.markdown("### 🛒 12궁도 거래소")
            display_cols = st.columns(2)
            for i, stock in enumerate(constellations):
                with display_cols[i % 2]:
                    with st.container(border=True):
                        stock_diff = current_prices[stock] - prev_prices[stock]
                        st.metric(label=f"🌌 {stock}", value=f"{current_prices[stock]:,}원", delta=f"{stock_diff:,}원")
                        owned = my_data["portfolio"][stock]
                        st.caption(f"내 보유량: **{owned}주**")
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            b_amt = st.number_input("매수", min_value=0, step=1, key=f"b_n_{stock}")
                            st.caption(f"예상: -{b_amt * current_prices[stock]:,}원")
                            
                            b_col1, b_col2 = st.columns(2)
                            if b_col1.button("매수", key=f"b_b_{stock}", use_container_width=True):
                                if b_amt > 0 and b_amt * current_prices[stock] <= my_data["cash"]:
                                    global_state["users"][my_id]["cash"] -= b_amt * current_prices[stock]
                                    global_state["users"][my_id]["portfolio"][stock] += b_amt
                                    st.rerun()
                                else:
                                    st.error("현금 부족!")
                            
                            if b_col2.button("MAX", key=f"max_b_{stock}", type="primary", use_container_width=True):
                                max_qty = my_data["cash"] // current_prices[stock]
                                if max_qty > 0:
                                    global_state["users"][my_id]["cash"] -= max_qty * current_prices[stock]
                                    global_state["users"][my_id]["portfolio"][stock] += max_qty
                                    st.rerun()
                                else:
                                    st.error("현금 부족!")

                        with c2:
                            s_amt = st.number_input("매도", min_value=0, step=1, key=f"s_n_{stock}")
                            st.caption(f"예상: +{s_amt * current_prices[stock]:,}원")
                            
                            s_col1, s_col2 = st.columns(2)
                            if s_col1.button("매도", key=f"s_b_{stock}", use_container_width=True):
                                if s_amt > 0 and s_amt <= owned:
                                    global_state["users"][my_id]["cash"] += s_amt * current_prices[stock]
                                    global_state["users"][my_id]["portfolio"][stock] -= s_amt
                                    st.rerun()
                                else:
                                    st.error("수량 부족!")
                                    
                            if s_col2.button("MAX", key=f"max_s_{stock}", type="primary", use_container_width=True):
                                if owned > 0:
                                    global_state["users"][my_id]["cash"] += owned * current_prices[stock]
                                    global_state["users"][my_id]["portfolio"][stock] = 0
                                    st.rerun()
                                else:
                                    st.error("보유량 없음!")

    if st.sidebar.button("로그아웃"):
        st.session_state.clear()
        st.rerun()
