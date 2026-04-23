import streamlit as st
import pandas as pd
from gtts import gTTS
import base64
from io import BytesIO
import os

# 1. 파일 설정: 선생님이 말씀하신 'data'라는 이름을 최우선으로 찾습니다.
def get_csv_file():
    # 1순위: data.csv 라는 이름이 있는지 확인
    if os.path.exists('data.csv'):
        return 'data.csv'
    # 2순위: 그 외에 .csv로 끝나는 첫 번째 파일을 찾음
    files = [f for f in os.listdir('.') if f.endswith('.csv')]
    if files:
        return files[0]
    return None

FILE_NAME = get_csv_file()

@st.cache_data
def load_data():
    if not FILE_NAME:
        return None
    try:
        # 데이터 로드 (utf-8-sig로 한글 깨짐 방지)
        df = pd.read_csv(FILE_NAME, encoding='utf-8-sig')
        
        # [핵심] 제목 칸의 이름에 상관없이 순서대로 강제 지정합니다.
        # 주제, 레벨, 지문, 어휘, 구문, 문제, 보기, 정답 순서
        new_cols = ['Topic', 'Level', 'Passage', 'Vocabulary', 'Grammar', 'Question', 'Option', 'Answer']
        df.columns = new_cols[:len(df.columns)]
        
        # 데이터의 앞뒤 공백 제거
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
        return df
    except:
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
        st.warning("음성 재생에 실패했습니다.")

# --- UI 설정 ---
st.set_page_config(page_title="고1 영어 수준별 학습", layout="wide")
st.title("📚 고등학교 1학년 영어 수준별 학습 앱")

if not FILE_NAME:
    st.error("데이터 파일(data.csv)을 찾을 수 없습니다. GitHub에 파일을 올렸는지 확인해주세요.")
else:
    df = load_data()
    
    if df is not None:
        # 1. 사이드바 정보 입력
        with st.sidebar:
            st.header("👤 학생 정보")
            grade = st.text_input("학년", "1")
            s_class = st.text_input("반")
            number = st.text_input("번호")
            name = st.text_input("이름")
            st.divider()
            
            st.header("⚙️ 학습 설정")
            u_topic = st.selectbox("주제 선택", df['Topic'].unique())
            u_level = st.selectbox("레벨 선택", df['Level'].unique())

        # 2. 지문 필터링 및 출력
        try:
            sel = df[(df['Topic'] == u_topic) & (df['Level'] == u_level)].iloc[0]

            st.subheader(f"📖 {u_topic} - {u_level}")
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                st.info(sel['Passage'])
            with col2:
                if st.button("🔊"):
                    speak(sel['Passage'])

            with st.expander("💡 어휘 및 구문 도움말"):
                st.write("**[어휘]**", sel['Vocabulary'])
                st.write("**[구문]**", sel['Grammar'])

            st.divider()

            # 3. 퀴즈 섹션
            if st.button("📝 학습하기 (문제 풀기)"):
                st.session_state.quiz = True

            if st.session_state.get('quiz'):
                st.subheader("✍️ 확인 문제")
                qs = sel['Question'].split('|')
                opts = sel['Option'].split('|')
                ans = sel['Answer'].split('|')

                user_ans = []
                for i in range(len(qs)):
                    st.write(f"**Q{i+1}. {qs[i].strip()}**")
                    choice = st.radio(f"정답 선택 {i+1}", ["(A)", "(B)", "(C)", "(D)"], key=f"q{i}", horizontal=True)
                    user_ans.append(choice)

                if st.button("채점 및 피드백"):
                    score = sum([1 for u, a in zip(user_ans, ans) if u.strip() == a.strip()])
                    st.subheader(f"📊 {name} 학생: 5문제 중 {score}문제를 맞혔습니다!")
                    
                    if score >= 4:
                        st.balloons()
                        st.success("🌟 열심히 공부한 것에 대해 선생님이 가득 칭찬합니다!")
                    elif score >= 2:
                        st.warning("👏 노력에 대해 칭찬하며, 조금만 더 열심히 하면 좋은 결과가 있을 거예요!")
                    else:
                        st.error("💪 어렵더라도 포기하지 말고 꾸준히 노력해보자!")
        except:
            st.warning("데이터 매칭 오류가 발생했습니다.")
