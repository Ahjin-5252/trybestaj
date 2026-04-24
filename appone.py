import streamlit as st
import pandas as pd
from gtts import gTTS
import base64
from io import BytesIO

# 1. 파일명 설정
FILE_NAME = 'data.csv'

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(FILE_NAME, encoding='utf-8-sig')
        df.columns = ['Topic', 'Level', 'Passage', 'Vocabulary', 'Grammar', 'Question', 'Option', 'Answer']
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"데이터 파일을 읽는 중 오류가 발생했습니다. 파일명과 형식을 확인해주세요: {e}")
        return None

def speak(text):
    try:
        tts = gTTS(text=text, lang='en')
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        audio_bytes = fp.read()
        b64 = base64.b64encode(audio_bytes).decode()
        st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
    except:
        st.warning("음성 재생 실패")

# --- 앱 상태 초기화 함수 ---
def reset_app():
    st.session_state.show_quiz = False
    st.rerun()

# --- UI 설정 ---
st.set_page_config(page_title="고1 영어 수준별 학습", layout="wide")
st.title("📚 고등학교 1학년 영어 수준별 학습 앱")

# 세션 상태 관리
if 'show_quiz' not in st.session_state:
    st.session_state.show_quiz = False

df = load_data()

if df is not None:
    # 1. 사이드바: 학생 정보 및 학습 선택
    with st.sidebar:
        st.header("👤 학습자 정보 입력")
        # 학년, 반, 번호, 이름 입력란 추가
        col1, col2, col3 = st.columns(3)
        with col1:
            grade = st.text_input("학년", "1")
        with col2:
            s_class = st.text_input("반")
        with col3:
            s_num = st.text_input("번호")
        name = st.text_input("이름")
        
        st.divider()
        
        st.header("⚙️ 학습 설정")
        u_topic = st.selectbox("주제 선택", df['Topic'].unique())
        u_level = st.selectbox("레벨 선택", df['Level'].unique())
        
        st.divider()
        # 처음으로 버튼 (설정 초기화)
        if st.button("🏠 처음으로"):
            reset_app()

    # 2. 본문: 지문 학습 섹션
    try:
        sel = df[(df['Topic'] == u_topic) & (df['Level'] == u_level)].iloc[0]

        st.subheader(f"📖 {u_topic} 지문 학습 ({u_level})")
        
        col_p, col_s = st.columns([0.9, 0.1])
        with col_p:
            st.info(sel['Passage'])
        with col_s:
            if st.button("🔊"):
                speak(sel['Passage'])

        with st.expander("💡 어휘 및 구문 도움말 보기"):
            st.write("**[핵심 어휘]**")
            st.write(sel['Vocabulary'])
            st.write("**[구문 해설]**")
            st.write(sel['Grammar'])

        st.divider()

        # 3. 문제 풀기 섹션
        if not st.session_state.show_quiz:
            if st.button("📝 학습하기 (문제 풀기)"):
                st.session_state.show_quiz = True
                st.rerun()

        if st.session_state.show_quiz:
            st.subheader("✍️ 확인 문제")
            qs = str(sel['Question']).split('|')
            ans = str(sel['Answer']).split('|')
            
            user_choices = []
            for i in range(len(qs)):
                st.write(f"**Q{i+1}. {qs[i].strip()}**")
                choice = st.radio(f"정답 선택 {i+1}", ["(A)", "(B)", "(C)", "(D)"], key=f"q{i}", horizontal=True)
                user_choices.append(choice)

            c_btn1, c_btn2 = st.columns([0.2, 0.8])
            with c_btn1:
                if st.button("✅ 채점 완료"):
                    score = sum([1 for u, a in zip(user_choices, ans) if u.strip() == a.strip()])
                    st.session_state.final_score = score
            
            if 'final_score' in st.session_state:
                score = st.session_state.final_score
                st.subheader(f"📊 {grade}학년 {s_class}반 {s_num}번 {name} 학생의 결과")
                st.write(f"총 {len(qs)}문제 중 {score}문제를 맞혔습니다!")
                
                if score == len(qs):
                    st.balloons()
                    st.success("🌟 완벽해요! 선생님이 가득 칭찬합니다!")
                elif score >= len(qs) // 2:
                    st.warning("👏 노력하는 모습이 멋져요! 조금만 더 하면 다 맞을 수 있어요!")
                else:
                    st.error("💪 조금 어렵나요? 다시 한번 지문을 읽어보며 도전해봐요!")
                
                # 다시하기 버튼 (문제 풀기 상태만 초기화)
                if st.button("🔄 다시하기"):
                    st.session_state.show_quiz = False
                    if 'final_score' in st.session_state:
                        del st.session_state.final_score
                    st.rerun()
                    
    except IndexError:
        st.warning("해당 주제와 레벨에 맞는 지문이 없습니다. 다른 옵션을 선택해주세요.")
