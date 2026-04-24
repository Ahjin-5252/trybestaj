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
        # 데이터 로드 (한글 깨짐 방지를 위해 utf-8-sig 사용)
        df = pd.read_csv(FILE_NAME, encoding='utf-8-sig')
        
        # [핵심] 제목 행의 이름과 상관없이 순서대로 이름을 강제 지정합니다.
        # 데이터 파일의 열 순서가 주제, 레벨, 지문... 순서여야 합니다.
        df.columns = ['Topic', 'Level', 'Passage', 'Vocabulary', 'Grammar', 'Question', 'Option', 'Answer']
        
        # 데이터 앞뒤 공백 제거하여 매칭 오류 방지
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"데이터 파일을 읽는 중 오류가 발생했습니다: {e}")
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

# --- UI 설정 ---
st.set_page_config(page_title="고1 영어 수준별 학습", layout="wide")
st.title("📚 고등학교 1학년 영어 수준별 학습 앱")

df = load_data()

if df is not None:
    # 1. 사이드바 인터페이스
    with st.sidebar:
        st.header("👤 학생 정보")
        name = st.text_input("이름")
        st.divider()
        
        st.header("⚙️ 학습 설정")
        # csv 파일에 있는 모든 주제와 레벨을 자동으로 가져옵니다.
        u_topic = st.selectbox("주제 선택", df['Topic'].unique())
        u_level = st.selectbox("레벨 선택", df['Level'].unique())

    # 2. 지문 출력 영역
    try:
        # 선택한 주제와 레벨에 맞는 데이터 추출
        sel = df[(df['Topic'] == u_topic) & (df['Level'] == u_level)].iloc[0]

        st.subheader(f"📖 {u_topic} 지문 학습 ({u_level})")
        c1, c2 = st.columns([0.9, 0.1])
        with c1:
            st.info(sel['Passage'])
        with c2:
            if st.button("🔊"):
                speak(sel['Passage'])

        with st.expander("💡 학습 포인트 (어휘/구문)"):
            st.write("**[어휘]**", sel['Vocabulary'])
            st.write("**[구문]**", sel['Grammar'])

        st.divider()

        # 3. 문제 풀기 및 피드백
        if st.button("📝 학습하기 (문제 풀기)"):
            st.session_state.quiz = True

        if st.session_state.get('quiz'):
            st.subheader("✍️ 확인 문제")
            qs = sel['Question'].split('|')
            ans = sel['Answer'].split('|')
            
            user_ans = []
            for i, q in enumerate(qs):
                st.write(f"**Q{i+1}. {q.strip()}**")
                u_choice = st.radio(f"답안 {i+1}", ["(A)", "(B)", "(C)", "(D)"], key=f"q{i}", horizontal=True)
                user_ans.append(u_choice)

            if st.button("채점 완료"):
                score = sum([1 for u, a in zip(user_ans, ans) if u.strip() == a.strip()])
                st.subheader(f"📊 {name} 학생: 5문제 중 {score}문제를 맞혔습니다!")
                
                if score >= 4:
                    st.balloons()
                    st.success("🌟 열심히 공부한 것에 대해 선생님이 가득 칭찬합니다! 정말 대단해요!")
                elif score >= 2:
                    st.warning("👏 노력하는 모습이 아주 멋져요! 조금만 더 열심히 하면 좋은 결과가 있을 거예요!")
                else:
                    st.error("💪 어렵더라도 포기하지 말고 꾸준히 노력해보자!")
    except:
        st.warning("해당 주제와 레벨에 맞는 데이터를 찾을 수 없습니다.")
