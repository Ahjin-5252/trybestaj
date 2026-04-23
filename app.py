import streamlit as st
import pandas as pd
from gtts import gTTS
import base64
from io import BytesIO
import os

# 1. 파일 설정 (LFS 문제가 해결된 data.csv를 읽습니다)
FILE_NAME = 'data.csv'

@st.cache_data
def load_data():
    try:
        # 데이터 로드
        df = pd.read_csv(FILE_NAME, encoding='utf-8-sig')
        # 열 이름을 순서대로 강제 지정 (데이터 파일의 헤더에 상관없이 작동)
        df.columns = ['Topic', 'Level', 'Passage', 'Vocabulary', 'Grammar', 'Question', 'Option', 'Answer']
        # 데이터 앞뒤 공백 제거
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"데이터 파일을 읽는 데 실패했습니다. GitHub의 data.csv 내용을 확인해주세요. 오류: {e}")
        return None

# 음성 재생 함수
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
        st.warning("음성 재생에 실패했습니다.")

# --- UI 시작 ---
st.set_page_config(page_title="고1 영어 수준별 학습", layout="wide")
st.title("📚 고등학교 1학년 영어 수준별 학습 앱")

df = load_data()

if df is not None:
    # 1. 학생 정보 입력 (사이드바)
    with st.sidebar:
        st.header("👤 학생 정보 입력")
        grade = st.text_input("학년", "1")
        s_class = st.text_input("반")
        number = st.text_input("번호")
        name = st.text_input("이름")
        
        st.divider()
        
        st.header("⚙️ 학습 설정")
        # 주제와 레벨 선택
        topic_list = df['Topic'].unique()
        level_list = df['Level'].unique()
        u_topic = st.selectbox("주제 선택", topic_list)
        u_level = st.selectbox("레벨 선택", level_list)

    # 2. 지문 출력 섹션
    try:
        # 선택한 주제와 레벨에 맞는 데이터 추출
        sel = df[(df['Topic'] == u_topic) & (df['Level'] == u_level)].iloc[0]

        st.subheader(f"📖 지문 읽기: {u_topic} ({u_level})")
        col_p, col_s = st.columns([0.9, 0.1])
        with col_p:
            st.info(sel['Passage'])
        with col_s:
            if st.button("🔊"):
                speak(sel['Passage'])

        with st.expander("💡 어휘 및 구문 도움말 보기"):
            st.write("**[핵심 어휘]**", sel['Vocabulary'])
            st.write("**[구문 해설]**", sel['Grammar'])

        st.divider()

        # 3. 문제 풀기 (학습하기 버튼)
        if st.button("📝 학습하기 (문제 풀기)"):
            st.session_state.show_quiz = True

        if st.session_state.get('show_quiz'):
            st.subheader("✍️ 확인 문제")
            # 문제와 정답 분리 (| 기호 기준)
            qs = str(sel['Question']).split('|')
            ans = str(sel['Answer']).split('|')
            
            user_choices = []
            for i in range(len(qs)):
                st.write(f"**Q{i+1}. {qs[i].strip()}**")
                # 보기 선택 (기본적으로 A~D 선택지를 제공)
                choice = st.radio(f"정답 선택 {i+1}", ["(A)", "(B)", "(C)", "(D)"], key=f"q{i}", horizontal=True)
                user_choices.append(choice)

            if st.button("채점 및 결과 확인"):
                score = sum([1 for u, a in zip(user_choices, ans) if u.strip() == a.strip()])
                st.subheader(f"📊 {name} 학생의 결과: 5문제 중 {score}문제를 맞혔습니다!")
                
                # 선생님이 요청하신 점수별 피드백
                if score >= 4:
                    st.balloons()
                    st.success("🌟 열심히 공부한 것에 대해 선생님이 가득 칭찬합니다! 정말 대단해요!")
                elif score >= 2:
                    st.warning("👏 노력하는 모습이 아주 멋져요! 조금만 더 열심히 하면 다음엔 좋은 결과가 있을 거예요!")
                else:
                    st.error("💪 어렵더라도 포기하지 말고 꾸준히 노력해보자! 화이팅!")

    except Exception as e:
        st.warning("선택한 주제와 레벨에 맞는 데이터를 찾을 수 없습니다. 옵션을 다시 선택해주세요.")
