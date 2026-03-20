import streamlit as st
import json
import os
import time

# === 1. 데이터 관리 설정 ===
DATA_FILE = 'bank_data.json'

def load_data():
    """파일에서 사용자 데이터를 불러옵니다."""
    if not os.path.exists(DATA_FILE):
        return {} # 파일이 없으면 빈 딕셔너리 반환
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    """데이터를 파일에 저장합니다."""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# === 2. 메인 화면 구성 ===
def main():
    st.set_page_config(page_title="우리반 모의 은행", page_icon="🏦")
    
    # 세션 상태 초기화 (로그인 유지용)
    if 'user' not in st.session_state:
        st.session_state['user'] = None

    users = load_data()

    # --- A. 로그인 전 화면 ---
    if st.session_state['user'] is None:
        st.title("🏦 우리반 모의 은행")
        
        tab1, tab2 = st.tabs(["🔒 로그인", "📝 회원가입"])

        # [로그인 탭]
        with tab1:
            with st.form("login_form"):
                id_input = st.text_input("이름 (아이디)")
                pw_input = st.text_input("비밀번호", type="password")
                if st.form_submit_button("로그인"):
                    if id_input in users and users[id_input]["pw"] == pw_input:
                        st.session_state['user'] = id_input
                        st.success(f"{id_input}님, 환영합니다!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("아이디 또는 비밀번호가 틀렸어요.")

        # [회원가입 탭]
        with tab2:
            st.info("처음 왔나요? 이름을 등록하고 10,000원을 받으세요!")
            with st.form("signup_form"):
                new_id = st.text_input("사용할 이름 (중복 불가)")
                new_pw = st.text_input("사용할 비밀번호", type="password")
                if st.form_submit_button("가입하기"):
                    if not new_id or not new_pw:
                        st.warning("이름과 비밀번호를 모두 입력해주세요.")
                    elif new_id in users:
                        st.error("이미 등록된 이름입니다.")
                    else:
                        # 가입 축하금 10,000원 지급
                        users[new_id] = {"pw": new_pw, "balance": 10000}
                        save_data(users)
                        st.success("회원가입 성공! 이제 로그인 탭에서 접속하세요.")

    # --- B. 로그인 후 화면 ---
    else:
        current_user = st.session_state['user']
        st.title(f"👋 반갑습니다, {current_user}님!")
        
        # 잔액 표시 (눈에 띄게)
        balance = users[current_user]['balance']
        st.metric(label="나의 현재 잔액", value=f"{balance:,} 원")
        
        st.divider()

        # [송금 기능]
        st.subheader("💸 친구에게 송금하기")
        # 나를 제외한 사용자 목록
        friends = [u for u in users.keys() if u != current_user]
        
        if not friends:
            st.write("아직 가입한 친구가 없어요. 친구들에게 가입하라고 알려주세요!")
        else:
            with st.form("transfer_form"):
                receiver = st.selectbox("누구에게 보낼까요?", friends)
                amount = st.number_input("보낼 금액 (원)", min_value=0, step=100)
                
                if st.form_submit_button("돈 보내기"):
                    if amount <= 0:
                        st.error("1원 이상 보내야 합니다.")
                    elif balance < amount:
                        st.error("잔액이 부족합니다.")
                    else:
                        # 돈 이동
                        users[current_user]['balance'] -= amount
                        users[receiver]['balance'] += amount
                        save_data(users)
                        
                        st.balloons()
                        st.success(f"{receiver}님에게 {amount:,}원을 보냈습니다!")
                        time.sleep(1.5)
                        st.rerun()

        # [로그아웃]
        st.sidebar.write(f"현재 접속: **{current_user}**")
        if st.sidebar.button("로그아웃"):
            st.session_state['user'] = None
            st.rerun()

if __name__ == "__main__":
    main()