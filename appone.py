import streamlit as st
import pandas as pd
from gtts import gTTS
import base64
from io import BytesIO

# 1. 파일명 설정
FILE_NAME = 'data.csv'

@st.cache_data
def load_data():
    # 여러 인코딩 방식을 순차적으로 시도하여 에러를 방지합니다.
    encodings = ['utf-8-sig', 'cp949', 'euc-kr']
    for encoding in encodings:
        try:
            df = pd.read_csv(FILE_NAME, encoding=encoding)
            # 열 이름을 강제로 지정 (데이터 순서: 주제, 레벨, 지문, 어휘, 구문, 문제, 보기, 정답)
            df.columns = ['Topic', 'Level', 'Passage', 'Vocabulary', 'Grammar', 'Question', 'Option', 'Answer']
            # 데이터 공백 제거
            for col in df.columns:
                df[col] = df[col].astype(str).str.strip()
            return df
        except:
            continue
    
    st.error(f"데이터 파일을 읽을 수 없습니다. 파일이 '{FILE_NAME}'인지, 그리고 올바른 CSV 형식인지 확인해주세요.")
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

# --- 앱 상태 관리 함수 ---
def init_session():
    if 'show_quiz' not in st.session_state:
        st.session_state.show_quiz = False
    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False

# --- UI 설정 ---
st.set_page_config(page_title="고1 영어 수준별 학습", layout="wide")
init_session()

st.title("📚 고등학교 1학년 영어 수준별 학습 앱")

df = load_data()

if df is not None:
    # 1. 사이드바: 학습자 정보 및 설정
    with st.sidebar:
        st.header("👤 학습자 정보 입력")
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
        # 처음으로 버튼
        if st.button("🏠 처음으로"):
            st.session_state.show_quiz = False
            st.session_state.quiz_submitted = False
            st.rerun()

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

        # 3. 문제 풀기 및 피드백
        if not st.session_state.show_quiz:
            if st.button("📝 학습하기 (문제 풀기)"):
                st.session_state.show_quiz = True
                st.rerun()

        if st.session_state.show_quiz:
            st.subheader("✍️ 확인 문제")
            qs = str(sel['Question']).split('|')
            opts = str(sel['Option']).split('|')
            ans = str(sel['Answer']).split('|')
            
            user_choices = []
            for i in range(len(qs)):
                st.write(f"**Q{i+1}. {qs[i].strip()}**")
                # 라디오 버튼의 키를 고유하게 설정하여 리런 시에도 유지되도록 함
                u_choice = st.radio(f"정답 선택 {i+1}", ["(A)", "(B)", "(C)", "(D)"], key=f"ans_{u_topic}_{u_level}_{i}", horizontal=True)
                user_choices.append(u_choice)

            if st.button("✅ 채점 완료"):
                st.session_state.quiz_submitted = True
            
            if st.session_state.quiz_submitted:
                score = sum([1 for u, a in zip(user_choices, ans) if u.strip() == a.strip()])
                st.subheader(f"📊 {grade}학년 {s_class}반 {s_num}번 {name} 학생의 결과")
                st.write(f"총 {len(qs)}문제 중 {score}문제를 맞혔습니다!")
                
                # 피드백 제공
                if score >= 4:
                    st.balloons()
                    st.success("🌟 열심히 공부한 것에 대해 선생님이 가득 칭찬합니다! 정말 대단해요!")
                elif score >= 2:
                    st.warning("👏 노력하는 모습이 아주 멋져요! 조금만 더 열심히 하면 좋은 결과가 있을 거예요!")
                else:
                    st.error("💪 어렵더라도 포기하지 말고 꾸준히 노력해보자! 선생님은 너를 응원해.")
                
                # 다시하기 버튼
                if st.button("🔄 다시하기"):
                    st.session_state.quiz_submitted = False
                    st.rerun()
                    
    except Exception:
        st.warning("해당 주제와 레벨에 맞는 데이터를 불러올 수 없습니다.")
                    
    except IndexError:
        st.warning("해당 주제와 레벨에 맞는 지문이 없습니다. 다른 옵션을 선택해주세요.")
