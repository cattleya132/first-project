import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random

# ==========================================
# 👇 [중요] 따옴표("") 안에 본인의 구글 엑셀 주소를 꼭 다시 넣어주세요!
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

# 데이터 불러오기
def load_data():
    try:
        client = init_connection()
        sheet = client.open_by_url(SHEET_URL).sheet1
        return sheet.get_all_records()
    except Exception as e:
        return []

# 데이터 추가하기 (백그라운드)
def add_data_to_sheet(jp, kr):
    client = init_connection()
    sheet = client.open_by_url(SHEET_URL).sheet1
    sheet.append_row([jp, kr])

# 데이터 삭제하기 (백그라운드)
def delete_data_from_sheet(row_index):
    client = init_connection()
    sheet = client.open_by_url(SHEET_URL).sheet1
    # 엑셀은 1부터 시작 + 헤더 1줄 = 실제 데이터는 인덱스 + 2
    sheet.delete_rows(row_index + 2)

def main():
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """, unsafe_allow_html=True)
    
    st.set_page_config(page_title="나만의 일본어 노트", page_icon="🇯🇵")
    st.title("🇯🇵 나만의 일본어 문장 노트")

    # 👇 [핵심 기술] '세션 상태(Session State)'를 사용해서 속도를 높입니다.
    # 앱을 처음 켰을 때만 엑셀에서 데이터를 가져오고, 그 뒤로는 내 컴퓨터 메모리에서 관리합니다.
    if 'sentences' not in st.session_state:
        try:
            st.session_state['sentences'] = load_data()
        except:
            st.session_state['sentences'] = []
            st.error("엑셀 연결 실패! URL을 확인해주세요.")

    menu = st.sidebar.selectbox("메뉴", ["문장 추가", "목록 관리", "랜덤 퀴즈"])

    # --- [문장 추가] ---
    if menu == "문장 추가":
        st.header("새로운 문장 기록 ✍️")
        with st.form("input_form", clear_on_submit=True):
            jp_input = st.text_input("일본어 문장")
            kr_input = st.text_input("한국어 뜻")
            submitted = st.form_submit_button("저장하기")
            
            if submitted:
                if jp_input and kr_input:
                    # 1. 엑셀에 진짜 저장 (뒤에서 몰래 함)
                    add_data_to_sheet(jp_input, kr_input)
                    # 2. 화면에도 즉시 반영 (다시 불러오기 안 함)
                    st.session_state['sentences'].append({'일본어': jp_input, '한국어': kr_input})
                    
                    st.success("✅ 저장되었습니다!")
                else:
                    st.warning("내용을 입력해주세요.")

    # --- [목록 관리] ---
    elif menu == "목록 관리":
        # 현재 내 메모리에 있는 데이터 개수 보여주기
        st.header(f"총 {len(st.session_state['sentences'])}개의 문장이 있어요 📂")
        
        # 목록을 보여줄 때 인덱스(idx)가 필요합니다.
        # 리스트가 중간에 삭제되면 꼬일 수 있으므로 복사본을 보며 처리하지 않고 바로 접근합니다.
        
        # 삭제 후 인덱스 밀림 방지를 위해, 화면 그리기용 리스트를 사용
        data = st.session_state['sentences']
        
        for idx, item in enumerate(data):
            col1, col2 = st.columns([4, 1])
            with col1:
                # 엑셀 헤더 이름 호환성 체크
                jp = item.get('일본어') or item.get('jp')
                kr = item.get('한국어') or item.get('kr')
                with st.expander(f"🇯🇵 {jp}"):
                    st.write(f"🇰🇷 뜻: {kr}")
            with col2:
                # 삭제 버튼마다 고유한 키(key)를 줍니다.
                if st.button("삭제", key=f"del_{idx}"):
                    # 1. 엑셀에서 삭제 요청 (기다리지 않음)
                    delete_data_from_sheet(idx)
                    
                    # 2. 내 화면(메모리)에서 즉시 삭제! (여기가 핵심)
                    del st.session_state['sentences'][idx]
                    
                    # 3. 즉시 새로고침 (기다림 없음)
                    st.rerun()

    # --- [랜덤 퀴즈] ---
    elif menu == "랜덤 퀴즈":
        st.header("복습 퀴즈 시간! 🧠")
        if not st.session_state['sentences']:
            st.info("데이터가 없습니다. 문장을 먼저 추가해주세요.")
        else:
            if st.button("새 문제 뽑기", type="primary"):
                quiz = random.choice(st.session_state['sentences'])
                st.session_state['q'] = quiz.get('일본어') or quiz.get('jp')
                st.session_state['a'] = quiz.get('한국어') or quiz.get('kr')
            
            if 'q' in st.session_state:
                st.subheader(f"Q. {st.session_state['q']}")
                with st.expander("정답 확인"):
                    st.write(f"정답: {st.session_state['a']}")

if __name__ == "__main__":
    main()
