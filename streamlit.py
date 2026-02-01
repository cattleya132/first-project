import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random
import time

# ==========================================
# 👇 [중요] 본인의 구글 엑셀 주소를 꼭 다시 넣어주세요!
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

# 데이터 추가 (백그라운드)
def add_data_to_sheet(jp, kr):
    client = init_connection()
    sheet = client.open_by_url(SHEET_URL).sheet1
    sheet.append_row([jp, kr])

# 데이터 삭제 (버전 호환)
def delete_data_from_sheet(row_index):
    client = init_connection()
    sheet = client.open_by_url(SHEET_URL).sheet1
    target_row = row_index + 2
    try:
        sheet.delete_rows(target_row)
    except AttributeError:
        sheet.delete_row(target_row)

def main():
    # 👇 [핵심 수정] 관리자 버튼, 푸터, 헤더, 햄버거 메뉴 싹 다 숨기기 (강력 버전)
    st.markdown("""
        <style>
        /* 1. 상단 햄버거 메뉴 숨기기 */
        #MainMenu {visibility: hidden;}
        
        /* 2. 하단 'Made with Streamlit' 푸터 숨기기 */
        footer {visibility: hidden;}
        
        /* 3. 상단 헤더 장식 줄 숨기기 */
        header {visibility: hidden;}
        
        /* 4. [중요] 우측 하단 관리자 버튼(왕관/프사) 숨기기 */
        div[data-testid="stStatusWidget"] {
            visibility: hidden;
            display: none !important;
        }
        
        /* 5. 혹시 모를 툴바 버튼 숨기기 */
        div[data-testid="stToolbar"] {
            visibility: hidden;
            display: none !important;
        }

        /* 6. 모바일 화면 여백 조정 (메뉴 버튼은 보이게) */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
        }
        </style>
        """, unsafe_allow_html=True)
    
    st.set_page_config(page_title="나만의 일본어 노트", page_icon="🇯🇵")
    st.title("🇯🇵 나만의 일본어 문장 노트")

    if 'sentences' not in st.session_state:
        try:
            st.session_state['sentences'] = load_data()
        except:
            st.session_state['sentences'] = []

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
                    try:
                        add_data_to_sheet(jp_input, kr_input)
                        st.session_state['sentences'].append({'일본어': jp_input, '한국어': kr_input})
                        st.success("✅ 저장되었습니다!")
                    except Exception as e:
                        st.error(f"저장 실패: {e}")
                else:
                    st.warning("내용을 입력해주세요.")

    # --- [목록 관리] ---
    elif menu == "목록 관리":
        st.header(f"총 {len(st.session_state['sentences'])}개의 문장이 있어요 📂")
        data_list = list(enumerate(st.session_state['sentences']))
        
        for idx, item in data_list:
            col1, col2 = st.columns([4, 1])
            with col1:
                jp = item.get('일본어') or item.get('jp')
                kr = item.get('한국어') or item.get('kr')
                with st.expander(f"🇯🇵 {jp}"):
                    st.write(f"🇰🇷 뜻: {kr}")
            with col2:
                if st.button("삭제", key=f"del_{idx}"):
                    try:
                        delete_data_from_sheet(idx)
                        if idx < len(st.session_state['sentences']):
                            del st.session_state['sentences'][idx]
                        st.rerun()
                    except Exception as e:
                        st.error("삭제 중 문제 발생")

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
