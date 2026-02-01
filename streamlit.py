import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random

# 👇 여기에 본인 엑셀 주소 넣으세요 (따옴표 필수!)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1u09CnLBLV8Ny5v0TDaXC7KBDRRx4tmMrh5o6cHR7vQI/edit?gid=0#gid=0" 

@st.cache_resource
def init_connection():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # Secrets 처리 (줄바꿈 문자 에러 방지)
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
    sheet.delete_row(row_index + 2)

def main():
    st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)
    st.set_page_config(page_title="나만의 일본어 노트", page_icon="🇯🇵")
    st.title("🇯🇵 나만의 일본어 문장 노트 (Excel Ver.)")

    # 엑셀 헤더 생성 확인
    try:
        client = init_connection()
        sheet = client.open_by_url(SHEET_URL).sheet1
        if not sheet.row_values(1):
            sheet.append_row(["일본어", "한국어"])
    except:
        st.error("엑셀 연결 실패! URL과 공유(편집자 권한)를 확인하세요.")
        return

    sentences = load_data()
    menu = st.sidebar.selectbox("메뉴", ["문장 추가", "목록 관리", "랜덤 퀴즈"])

    if menu == "문장 추가":
        st.header("새로운 문장 기록 ✍️")
        with st.form("input_form", clear_on_submit=True):
            jp_input = st.text_input("일본어 문장")
            kr_input = st.text_input("한국어 뜻")
            submitted = st.form_submit_button("저장하기")
            
            if submitted and jp_input and kr_input:
                add_data(jp_input, kr_input)
                st.success("✅ 구글 엑셀에 저장되었습니다!") # 👉 이 메시지가 떠야 성공!
                st.rerun()

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
                    st.success("삭제됨")
                    st.rerun()

    elif menu == "랜덤 퀴즈":
        st.header("퀴즈!")
        if st.button("문제 뽑기"):
            q = random.choice(sentences)
            st.info(f"Q. {q.get('일본어') or q.get('jp')}")
            with st.expander("정답"):
                st.write(q.get('한국어') or q.get('kr'))

if __name__ == "__main__":
    main()
