import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random
import time  # 👈 [1] 시간 관련 기능을 쓰기 위해 추가했습니다!

# ==========================================
# 👇 [중요] 본인의 구글 엑셀 주소를 다시 넣어주세요!
SHEET_URL = "https://docs.google.com/spreadsheets/d/1u09CnLBLV8Ny5v0TDaXC7KBDRRx4tmMrh5o6cHR7vQI/edit?gid=0#gid=0"
# ==========================================

# [보안] 구글 시트 연결하기
@st.cache_resource
def init_connection():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = dict(st.secrets["gcp_service_account"])
    if "private_key" in creds_dict:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

def load_data():
    try:
        client = init_connection()
        sheet = client.open_by_url(SHEET_URL).sheet1
        return sheet.get_all_records()
    except Exception as e:
        return []

def add_data(jp, kr):
    client = init_connection()
    sheet = client.open_by_url(SHEET_URL).sheet1
    sheet.append_row([jp, kr])

def delete_data(row_index):
    client = init_connection()
    sheet = client.open_by_url(SHEET_URL).sheet1
    sheet.delete_rows(row_index + 2)

def main():
    # 모바일 메뉴 보이게 설정 (헤더 숨김 코드 제거됨)
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """, unsafe_allow_html=True)
    
    st.set_page_config(page_title="나만의 일본어 노트", page_icon="🇯🇵")
    st.title("🇯🇵 나만의 일본어 문장 노트")

    try:
        client = init_connection()
        sheet = client.open_by_url(SHEET_URL).sheet1
        if not sheet.row_values(1):
            sheet.append_row(["일본어", "한국어"])
    except:
        st.error("엑셀 연결 실패! URL 주소가 맞는지 확인해주세요.")
        return

    sentences = load_data()
    menu = st.sidebar.selectbox("메뉴", ["문장 추가", "목록 관리", "랜덤 퀴즈"])

    if menu == "문장 추가":
        st.header("새로운 문장 기록 ✍️")
        with st.form("input_form", clear_on_submit=True):
            jp_input = st.text_input("일본어 문장")
            kr_input = st.text_input("한국어 뜻")
            submitted = st.form_submit_button("저장하기")
            
            if submitted:
                if jp_input and kr_input:
                    add_data(jp_input, kr_input)
                    st.success("✅ 구글 엑셀에 저장되었습니다!")
                else:
                    st.warning("내용을 입력해주세요.")

    elif menu == "목록 관리":
        st.header(f"총 {len(sentences)}개의 문장이 있어요 📂")
        
        for idx, item in enumerate(sentences):
            col1, col2 = st.columns([4, 1])
            with col1:
                jp = item.get('일본어') or item.get('jp')
                kr = item.get('한국어') or item.get('kr')
                with st.expander(f"🇯🇵 {jp}"):
                    st.write(f"🇰🇷 뜻: {kr}")
            with col2:
                if st.button("삭제", key=f"del_{idx}"):
                    delete_data(idx)
                    st.success("삭제 처리 중...") # 사용자 안심 메시지
                    
                    # 👇 [2] 여기서 1초 쉬고 새로고침합니다!
                    time.sleep(1.0) 
                    st.rerun()

    elif menu == "랜덤 퀴즈":
        st.header("복습 퀴즈 시간! 🧠")
        if not sentences:
            st.info("데이터가 없습니다. 문장을 먼저 추가해주세요.")
        else:
            if st.button("새 문제 뽑기", type="primary"):
                quiz = random.choice(sentences)
                st.session_state['q'] = quiz.get('일본어') or quiz.get('jp')
                st.session_state['a'] = quiz.get('한국어') or quiz.get('kr')
            
            if 'q' in st.session_state:
                st.subheader(f"Q. {st.session_state['q']}")
                with st.expander("정답 확인"):
                    st.write(f"정답: {st.session_state['a']}")

if __name__ == "__main__":
    main()
