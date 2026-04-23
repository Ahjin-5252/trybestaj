import streamlit as st
import pandas as pd
from gtts import gTTS
import base64
from io import BytesIO
import os

# [해결책] 특정 이름을 지정하지 않고, 폴더 내의 첫 번째 CSV 파일을 자동으로 찾습니다.
def get_csv_file():
    files = [f for f in os.listdir('.') if f.endswith('.csv')]
    if files:
        return files[0] # 가장 먼저 발견된 CSV 파일을 반환
    return None

FILE_NAME = get_csv_file()

@st.cache_data
def load_data():
    if not FILE_NAME:
        return None
    # 어떤 제목이 있든 무시하고 순서대로 제목을 강제 지정합니다.
    df = pd.read_csv(FILE_NAME, encoding='utf-8-sig')
    df.columns = ['Topic', 'Level', 'Passage', 'Vocabulary', 'Grammar', 'Question', 'Option', 'Answer']
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()
    return df

def speak(text):
    tts = gTTS(text=text, lang='en')
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    audio_bytes = fp.read()
    b64 = base64.b64encode(audio_bytes).decode()
    st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)

# --- UI 시작 ---
st.set_page_config(page_title="고1 영어 학습", layout="wide")
st.title("📚 고등학교 1학년 수준별 영어 학습 앱")

if not FILE_NAME:
    st.error("데이터 파일(.csv)을 찾을 수 없습니다. GitHub에 CSV 파일이 있는지 확인해주세요.")
else:
    try:
        df = load_data()
        
        with st.sidebar:
            st.header("👤 학생 정보")
            name = st.text_input("이름", "학생")
            topic = st.selectbox("주제", df['Topic'].unique())
            level = st.selectbox("난이도", df['Level'].unique())

        sel = df[(df['Topic'] == topic) & (df['Level'] == level)].iloc[0]

        st.subheader(f"📖 {topic} - {level}")
        col1, col2 = st.columns([0.9, 0.1])
        with col1:
            st.info(sel['Passage'])
        with col2:
            if st.button("🔊"):
                speak(sel['Passage'])

        with st.expander("학습 도움말 보기"):
            st.write("**단어:**", sel['Vocabulary'])
            st.write("**문법:**", sel['Grammar'])

        st.divider()

        st.subheader("📝 확인 문제")
        qs = sel['Question'].split('|')
        opts = sel['Option'].split('|')
        ans = sel['Answer'].split('|')

        user_ans = []
        for i in range(len(qs)):
            st.write(f"**{i+1}. {qs[i]}**")
            choice = st.radio(f"정답 선택 {i+1}", ["(A)", "(B)", "(C)", "(D)"], key=f"q{i}", horizontal=True)
            user_ans.append(choice)

        if st.button("채점하기"):
            score = sum([1 for u, a in zip(user_ans, ans) if u.strip() == a.strip()])
            st.success(f"{name} 학생, 5문제 중 {score}문제를 맞혔습니다!")
            
            if score >= 4:
                st.balloons()
                st.write(f"🌟 **{name} 학생, 정말 대단해요!** 선생님이 가득 칭찬합니다!")
            elif score >= 2:
                st.write(f"👏 **{name} 학생, 노력하는 모습이 멋져요!** 조금만 더 하면 만점이에요.")
            else:
                st.write(f"💪 **{name} 학생, 포기하지 마세요!** 꾸준히 하면 실력이 늘 거예요.")

    except Exception as e:
        st.error(f"앱 실행 중 오류가 발생했습니다. (데이터 형식을 확인해주세요)")
