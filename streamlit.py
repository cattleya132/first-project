import streamlit as st
import json
import os
import random

# 데이터 파일 이름
FILE_NAME = "my_japanese_data.json"

# 1. 데이터 불러오기/저장하기 함수
def load_data():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 2. 화면 디자인 & 기능
def main():
    st.set_page_config(page_title="나만의 일본어 노트", page_icon="🇯🇵")
    st.title("🇯🇵 나만의 일본어 문장 노트")

    # 데이터 로드
    sentences = load_data()

    # 사이드바 메뉴
    menu = st.sidebar.selectbox("메뉴를 선택하세요", ["문장 추가", "목록 관리", "랜덤 퀴즈"])

    # --- 메뉴 1: 문장 추가 ---
    if menu == "문장 추가":
        st.header("새로운 문장 기록 ✍️")
        
        with st.form("input_form", clear_on_submit=True):
            jp_input = st.text_input("일본어 문장", placeholder="예: 私は学生です")
            kr_input = st.text_input("한국어 뜻", placeholder="예: 저는 학생입니다")
            submitted = st.form_submit_button("저장하기")
            
            if submitted:
                if jp_input and kr_input:
                    sentences.append({"jp": jp_input, "kr": kr_input})
                    save_data(sentences)
                    st.success("✅ 저장되었습니다!")
                else:
                    st.warning("⚠️ 문장과 뜻을 모두 입력해주세요.")

    # --- 메뉴 2: 목록 관리 (수정된 부분!) ---
    elif menu == "목록 관리":
        st.header(f"총 {len(sentences)}개의 문장이 있어요 📂")
        
        if not sentences:
            st.info("저장된 문장이 없습니다. '문장 추가' 탭에서 추가해주세요!")
        else:
            # 리스트를 하나씩 꺼내서 보여줌 (인덱스 필요해서 enumerate 사용)
            for idx, item in enumerate(sentences):
                # 화면을 4:1 비율로 쪼개기 (왼쪽:내용, 오른쪽:삭제버튼)
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    # 문장 보여주기
                    with st.expander(f"🇯🇵 {item['jp']}"):
                        st.write(f"🇰🇷 뜻: {item['kr']}")
                
                with col2:
                    # 삭제 버튼 (key값이 겹치지 않게 idx를 붙여줌)
                    if st.button("삭제", key=f"del_{idx}"):
                        del sentences[idx]   # 1. 데이터 삭제
                        save_data(sentences) # 2. 파일 저장
                        st.rerun()           # 3. 화면 새로고침 (중요!)

    # --- 메뉴 3: 랜덤 퀴즈 ---
    elif menu == "랜덤 퀴즈":
        st.header("복습 퀴즈 시간! 🧠")
        
        if not sentences:
            st.error("문장이 너무 적어요. 먼저 문장을 추가해주세요!")
        else:
            # '다음 문제' 버튼
            if st.button("새로운 문제 뽑기", type="primary"):
                quiz = random.choice(sentences)
                st.session_state['quiz_q'] = quiz['jp']
                st.session_state['quiz_a'] = quiz['kr']

            if 'quiz_q' in st.session_state:
                st.subheader(f"Q. {st.session_state['quiz_q']}")
                
                with st.expander("정답 확인하기"):
                    st.success(f"정답: {st.session_state['quiz_a']}")

if __name__ == "__main__":
    main()