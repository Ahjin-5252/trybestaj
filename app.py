import streamlit as st
import pandas as pd
from gtts import gTTS
import base64
from io import BytesIO

# 1. 파일명 설정
FILE_NAME = 'graded_reading_texts.xlsx - Sheet1.csv'

@st.cache_data
def load_data():
    try:
        # 데이터 로드
        df = pd.read_csv(FILE_NAME, encoding='utf-8-sig')
        
        # [핵심] 제목 칸의 이름이 무엇이든 상관없이 순서대로 강제 지정합니다.
        # 0:주제, 1:레벨, 2:지문, 3:어휘, 4:구문, 5:문제, 6:보기, 7:정답
        new_cols = ['Topic', 'Level', 'Passage', 'Vocabulary', 'Grammar', 'Question', 'Option', 'Answer']
        df.columns = new_cols[:len(df.columns)]
        
        # 데이터 앞뒤 공백 제거
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
        return df
    except Exception as e:
        st.error(f"파일을 읽는 중 에러가 발생했습니다. 파일명을 확인해주세요: {e}")
        return None

# 앱 레이아웃 설정
st.set_page_config(page_title="고1 영어 학습", layout="wide")

if 'quiz_on' not in st.session_state:
    st.session_state.quiz_on = False

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

st.title("📚 고등학교 1학년 수준별 영어 학습")

df = load_data()

if df is not None:
    # 사이드바 입력창
    with st.sidebar:
        st.header("👤 학생 정보")
        u_name = st.text_input("이름", placeholder="이름을 입력하세요")
        st.divider()
        
        # 드롭다운 메뉴
        u_topic = st.selectbox("주제 선택", df['Topic'].unique())
        u_level = st.selectbox("레벨 선택", df['Level'].unique())

    try:
        # 필터링
        sel = df[(df['Topic'] == u_topic) & (df['Level'] == u_level)].iloc[0]

        st.subheader(f"📖 지문: {u_topic} ({u_level})")
        c1, c2 = st.columns([0.85, 0.15])
        with c1:
            st.info(sel['Passage'])
        with c2:
            if st.button("🔊 듣기"):
                speak(sel['Passage'])

        with st.expander("💡 어휘 및 구문 보기"):
            st.write("**[어휘]**", sel['Vocabulary'])
            st.write("**[구문]**", sel['Grammar'])

        st.divider()

        if st.button("📝 문제 풀기"):
            st.session_state.quiz_on = True

        if st.session_state.quiz_on:
            st.subheader("✍️ 학습 확인 문제")
            qs = str(sel['Question']).split('|')
            os = str(sel['Option']).split('|')
            as_ = str(sel['Answer']).split('|')

            answers = []
            for i in range(len(qs)):
                st.write(f"**Q{i+1}. {qs[i].strip()}**")
                ans = st.radio(f"정답 선택 {i+1}", ["(A)", "(B)", "(C)", "(D)"], key=f"q_{i}", horizontal=True)
                answers.append(ans)

            if st.button("제출 및 채점"):
                correct = sum([1 for u, a in zip(answers, as_) if u.strip() == a.strip()])
                st.subheader(f"📊 {u_name} 학생의 점수: {correct} / 5")
                
                if correct >= 4:
                    st.balloons()
                    st.success(f"🌟 정말 대단해요! 완벽하게 이해했군요. 선생님이 가득 칭찬합니다!")
                elif correct >= 2:
                    st.warning(f"👏 노력하는 모습이 멋져요! 조금만 더 하면 만점도 가능할 거예요.")
                else:
                    st.error(f"💪 포기하지 마세요! 꾸준히 하면 반드시 실력이 늘 거예요. 화이팅!")
    except:
        st.warning("데이터를 불러오는 중 문제가 발생했습니다.")
