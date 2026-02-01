import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random

# ==========================================

SHEET_URL = "https://docs.google.com/spreadsheets/d/1u09CnLBLV8Ny5v0TDaXC7KBDRRx4tmMrh5o6cHR7vQI/edit?gid=0#gid=0"
# ==========================================

# [보안] 구글 시트 연결하기 (에러 방지 코드 포함)
@st.cache_resource
def init_connection():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Secrets에서 정보 가져오기
    creds_dict = dict(st.secrets["gcp_service_account"])
    
    # 줄바꿈 문자(\n) 에러 자동 수정 (매우 중요)
    if "private_key" in creds_dict:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

# 데이터 불러오기
def load_data():
    try:
        client = init_connection()
        sheet = client.open_by_url(SHEET_URL).sheet1
        return sheet.get_all_records()
    except Exception as e:
        return []

# 데이터 추가하기
def add_data(jp, kr):
    client = init_connection()
    sheet = client.open_by_url(SHEET_URL).sheet1
    sheet.append_row([jp, kr])

# 데이터 삭제하기
def delete_data(row_index):
    client = init_connection()
    sheet = client.open_by_url(SHEET_URL).sheet1
    sheet.delete_row(row_index + 2)

# 메인 화면 구성
def main():
    # 메뉴 숨기기 (깔끔하게)
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """, unsafe_allow_html=True)
    
    st.set_page_config(page_title="나만의 일본어 노트", page_icon="🇯🇵")
    st.title("🇯🇵 나만의 일본어 문장 노트")

    # 1. 엑셀 연결 및 헤더 확인
    try:
        client = init_connection()
        sheet = client.open_by_url(SHEET_URL).sheet1
        # 첫 줄이 비어있으면 제목줄 생성
        if not sheet.row_values(1):
            sheet.append_row(["일본어", "한국어"])
    except:
        st.error("엑셀 연결 실패! URL 주소가 맞는지 확인해주세요.")
        return

    # 2. 데이터 로드
    sentences = load_data()

    # 사이드바 메뉴
    menu = st.sidebar.selectbox("메뉴", ["문장 추가", "목록 관리", "랜덤 퀴즈"])

    # --- [문장 추가] ---
    if menu == "문장 추가":
        st.header("새로운 문장 기록 ✍️")
        
        # clear_on_submit=True 덕분에 저장 후 입력창이 자동으로 깨끗해집니다.
        with st.form("input_form", clear_on_submit=True):
            jp_input = st.text_input("일본어 문장")
            kr_input = st.text_input("한국어 뜻")
            submitted = st.form_submit_button("저장하기")
            
            if submitted:
                if jp_input and kr_input:
                    add_data(jp_input, kr_input)
                    # 성공 메시지 띄우기 (rerun을 지워서 메시지가 유지됨)
                    st.success("✅ 구글 엑셀에 저장되었습니다!")
                else:
                    st.warning("내
