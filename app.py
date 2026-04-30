# 안드로 모의주식 게임 - 동시 접속 최적화 + 관리자 실시간 동기화 버전
import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import threading 

# 1. 사이트 기본 설정
st.set_page_config(page_title="안드로 주식게임", layout="wide", initial_sidebar_state="expanded")

# ⭐ 우주 배경 및 주식 앱 감성 커스텀 CSS
st.markdown("""
<style>
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
[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(17, 24, 39, 0.85) !important;
    border: 1px solid #374151 !important;
    border-radius: 12px !important;
}
h1, h2, h3 { color: #f8fafc !important; font-weight: 700 !important; }
.stButton > button { border-radius: 8px !important; font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)

constellations = ['양자리', '황소자리', '쌍둥이자리', '게자리', '사자자리', '처녀자리', '천칭자리', '전갈자리', '사수자리', '염소자리', '물병자리', '물고기자리']
special_coin = '안드로 코인'
all_assets = constellations + [special_coin]

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
        "is_game_over": False,
        "lock": threading.Lock() 
    }

global_state = get_global_state()

# 3. 로그인 시스템
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌌 안드로 주식게임")
    st.info("총 4번의 시간 여행! 시드머니 1,000만 원으로 시작하세요.")
    col1, col2 = st.columns(2)
    with col1:
        user_input = st.text_input("참가자 이름", key="user_login")
        if st.button("참가자 접속", use_container_width=True) and user_input:
            with global_state["lock"]: 
                if user_input not in global_state["users"]:
                    global_state["users"][user_input] = {"cash": 10000000, "portfolio": {s: 0 for s in all_assets}}
            st.session_state.user_role, st.session_state.user_id, st.session_state.logged_in = "user", user_input, True
            st.rerun()
    with col2:
        admin_pw = st.text_input("관리자 암호", type="password", key="admin_login")
        if st.button("관리자 접속", use_container_width=True) and admin_pw == "andro":
            st.session_state.user_role, st.session_state.user_id, st.session_state.logged_in = "admin", "관리자", True
            st.rerun()

# 4. 메인 게임 로직
else:
    turn_idx, year_list = global_state["current_turn_idx"], global_state["year_sequence"]
    current_year, current_prices, prev_prices = year_list[turn_idx], global_state["prices"], global_state["prev_prices"]
    is_game_over = global_state["is_game_over"]
    
    st.sidebar.title(f"👤 {st.session_state.user_id}님")
    st.sidebar.subheader(f"📅 {turn_idx + 1} / {len(year_list)} 라운드")
    st.sidebar.markdown(f"### 현재 시대: **{current_year}년**")

    # ----------------------------------------
    # [관리자 모드]
    # ----------------------------------------
    if st.session_state.user_role == "admin":
        # ⭐ [수정됨] 관리자 화면에도 5초마다 자동 새로고침 추가 (실시간 랭킹 반영)
        st_autorefresh(interval=5000, limit=None, key="admin_refresh")
        
        st.title("⚙️ 중앙 통제실")
        
        # 1. 참가자 자산 현황 랭킹
        st.markdown("### 🏆 참가자 자산 현황 (실시간 업데이트 중)")
        user_data_list = []
        for name, data in global_state["users"].items():
            total_assets = data["cash"] + sum(data["portfolio"][s] * current_prices[s] for s in all_assets)
            user_data_list.append({"이름": name, "총 자산": total_assets, "현금": data["cash"]})
        
        if user_data_list:
            # ⭐ [수정됨] 랭킹 보드의 가시성을 위해 데이터프레임을 더 깔끔하게 출력
            st.dataframe(pd.DataFrame(user_data_list).sort_values(by="총 자산", ascending=False), use_container_width=True, hide_index=True)
        else:
            st.info("현재 접속 중인 참가자가 없습니다.")

        st.divider()
        
        # 2. 시공간 이동 (라운드 넘기기)
        st.markdown("### 🚀 시공간 이동 (다음 라운드)")
        if not is_game_over:
            with st.container(border=True):
                next_year = year_list[turn_idx+1] if turn_idx < len(year_list)-1 else '종료'
                st.write(f"**다음 목적지:** {next_year}년")
                reserved_coin = st.number_input("💡 다음 라운드 도착 시 '안드로 코인' 설정 가격", value=current_prices[special_coin], step=500)
                if st.button(f"🚀 {next_year}년으로 점프 실행!", type="primary", use_container_width=True):
                    with global_state["lock"]:
                        if turn_idx < len(year_list) - 1:
                            global_state["prev_prices"] = global_state["prices"].copy()
                            global_state["current_turn_idx"] += 1
                            new_y = year_list[global_state["current_turn_idx"]]
                            for s in constellations: global_state["prices"][s] = yearly_prices[new_y][s]
                            global_state["prices"][special_coin] = reserved_coin
                        else: global_state["is_game_over"] = True
                    st.rerun()

        st.divider()

        # 3. 현재 시장 강제 조작
        st.markdown("### 💹 현재 시장 강제 조작 (즉시 반영)")
        if st.session_state.get("last_sync_year") != current_year:
            for s in all_assets: st.session_state[f"edit_{s}"] = current_prices[s]
            st.session_state["last_sync_year"] = current_year

        with st.form("admin_price_form"):
            st.number_input("🪙 안드로 코인", step=500, key=f"edit_{special_coin}")
            cols = st.columns(4)
            for i, stock in enumerate(constellations):
                with cols[i % 4]: st.number_input(f"{stock}", step=100, key=f"edit_{stock}")
            
            if st.form_submit_button("✅ 설정한 가격으로 전원 즉시 반영", use_container_width=True):
                with global_state["lock"]:
                    global_state["prev_prices"] = global_state["prices"].copy()
                    for s in all_assets: global_state["prices"][s] = st.session_state[f"edit_{s}"]
                st.success("시장 가격이 성공적으로 업데이트되었습니다!")
                st.rerun()

    # ----------------------------------------
    # [참가자 모드]
    # ----------------------------------------
    elif st.session_state.user_role == "user":
        st_autorefresh(interval=5000, limit=None, key="user_refresh") 
        my_id = st.session_state.user_id
        my_data = global_state["users"][my_id]
        total_assets = my_data["cash"] + sum(my_data["portfolio"][s] * current_prices[s] for s in all_assets)
        roi = ((total_assets - 10000000) / 10000000) * 100

        if is_game_over:
            st.title("🏁 게임 종료!"); st.header(f"🎊 최종 자산: {total_assets:,}원"); st.balloons()
        else:
            st.title(f"📈 {current_year}년 주식시장")
            with st.container(border=True):
                m1, m2, m3 = st.columns(3)
                m1.metric("내 총 자산", f"{total_assets:,}원", delta=f"{total_assets-10000000:,}원", delta_color="inverse")
                m2.metric("보유 현금", f"{my_data['cash']:,}원")
                m3.metric("누적 수익률", f"{roi:+.2f}%", delta=f"{roi:+.2f}%p", delta_color="inverse")
            st.divider()

            def render_trading_ui(asset, price, owned):
                b_key, s_key = f"b_{asset}", f"s_{asset}"
                max_b, max_s = my_data["cash"] // price, owned
                
                def set_val(k, v): st.session_state[k] = v
                def do_trade(mode, k, p):
                    amt = st.session_state.get(k, 0)
                    with global_state["lock"]: 
                        u_data = global_state["users"][my_id]
                        if mode == "buy" and amt > 0 and amt * p <= u_data["cash"]:
                            u_data["cash"] -= amt * p
                            u_data["portfolio"][asset] += amt
                            st.session_state[k] = 0
                        elif mode == "sell" and amt > 0 and amt <= u_data["portfolio"][asset]:
                            u_data["cash"] += amt * p
                            u_data["portfolio"][asset] -= amt
                            st.session_state[k] = 0
                        else: st.toast("⚠️ 수량이나 잔액을 확인하세요!", icon="🚨")

                diff = price - prev_prices[asset]
                pct = (diff / prev_prices[asset] * 100) if prev_prices[asset] != 0 else 0
                c1, c2 = st.columns([1, 1])
                with c1: st.metric(label=f"🌌 {asset}" if asset!=special_coin else f"🪙 {asset}", value=f"{price:,}원", delta=f"{diff:,}원 ({pct:+.2f}%)", delta_color="inverse")
                with c2: st.markdown(f"<div style='text-align: right; padding-top: 20px;'>보유: <b>{owned}주</b></div>", unsafe_allow_html=True)
                
                t1, t2 = st.columns(2)
                with t1:
                    st.markdown("<span style='color:#ef4444'>매수</span>", unsafe_allow_html=True)
                    st.number_input("수량", min_value=0, step=1, key=b_key, label_visibility="collapsed")
                    bc1, bc2, bc3 = st.columns([1, 1, 2])
                    bc1.button("50%", key=f"b5_{asset}", on_click=set_val, args=(b_key, max_b//2))
                    bc2.button("MAX", key=f"bm_{asset}", on_click=set_val, args=(b_key, max_b))
                    bc3.button("🔴 매수", key=f"be_{asset}", type="primary", use_container_width=True, on_click=do_trade, args=("buy", b_key, price))
                with t2:
                    st.markdown("<span style='color:#3b82f6'>매도</span>", unsafe_allow_html=True)
                    st.number_input("수량", min_value=0, step=1, key=s_key, label_visibility="collapsed")
                    sc1, sc2, sc3 = st.columns([1, 1, 2])
                    sc1.button("50%", key=f"s5_{asset}", on_click=set_val, args=(s_key, max_s//2))
                    sc2.button("MAX", key=f"sm_{asset}", on_click=set_val, args=(s_key, max_s))
                    sc3.button("🔵 매도", key=f"se_{asset}", use_container_width=True, on_click=do_trade, args=("sell", s_key, price))

            st.markdown("### 💎 스페셜 마켓")
            with st.container(border=True): render_trading_ui(special_coin, current_prices[special_coin], my_data["portfolio"][special_coin])
            st.markdown("### 🛒 12궁도 거래소")
            d_cols = st.columns(2)
            for i, s in enumerate(constellations):
                with d_cols[i % 2]:
                    with st.container(border=True): render_trading_ui(s, current_prices[s], my_data["portfolio"][s])

    if st.sidebar.button("🚪 로그아웃", use_container_width=True):
        st.session_state.clear(); st.rerun()
