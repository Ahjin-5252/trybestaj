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
        # 데이터 로드 (LFS 문제가 해결되었다면 정상적으로 읽힙니다)
        df = pd.read_csv(FILE_NAME, encoding='utf-8-sig')
        # 혹시 모를 제목 오타 방지를 위해 컬럼명 강제 지정
        df.columns = ['Topic', 'Level', 'Passage', 'Vocabulary', 'Grammar', 'Question', 'Option', 'Answer']
        return df
    except Exception as e:
        st.error(f"데이터 파일 읽기 실패: {e}")
        return None

# (중략: 이전과 동일한 UI 및 문제 풀이 코드)
