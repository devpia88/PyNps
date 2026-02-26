import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
import platform
import seaborn as sns
import re
import streamlit as st





# 주어진 'company_name' 으로 기업 검색
def find_company(self, company_name):
    # 가입자수가 많은 순으로 정렬하여 리턴
    return self.df.loc[self.df['사업장명'].str.contains(company_name), ['사업장명', '월급여추정', '연간급여추정', '업종코드', '가입자수']]\
                .sort_values('가입자수', ascending=False)

# 주어진 'company_name' 으로
# 동종업계 정보 (월급여 추정액, 연간급여추정액 ) 비교
def compare_company(self, company_name):
    company = self.find_company(company_name)
    code = company['업종코드'].iloc[0]
    df1 = self.df.loc[self.df['업종코드'] == code, ['월급여추정', '연간급여추정']].agg(['mean', 'count', 'min', 'max'])
    df1.columns = ['업종_월급여추정', '업종_연간급여추정']
    df1 = df1.T
    df1.columns = ['평균', '개수', '최소', '최대']
    df1.loc['업종_월급여추정', company_name] = company['월급여추정'].values[0]
    df1.loc['업종_연간급여추정', company_name] = company['연간급여추정'].values[0]
    return df1

# 검색 기업 정보 출력
def company_info(self, company_name):
    company = self.find_company(company_name)
    return self.df.loc[company.iloc[0].name]
            
def get_data(self):
    return self.df

# 국민연금공단_국민연금 가입 사업장 내역_20251124.csv
file_path = r'https://www.dropbox.com/scl/fi/q05nabk8r0822dy8q1kew/_-_20251124.csv?rlkey=x3z852i71fwm60kc69rijiwno&st=cxcnw7rz&dl=1'

@st.cache_resource   #동일함수 호출되면 , 매번 실행하지 않고 직전 실행된 결과 리턴케 함.
def read_pensiondata():
    data = PensionData(file_path)
    return data

data = read_pensiondata()

company_name = st.text_input('회사명을 입력해 주세요.', placeholder='검색할 회사명 입력')

if data and company_name:
    output = data.find_company(company_name = company_name)
    output

    if len(output) > 0:
        st.subheader(output.iloc[0]['사업장명'])

    info = data.company_info(company_name = company_name)
    st.markdown(
            f"""
            - `{info['주소']}`
            - 업종코드명 `{info['업종코드명']}`
            - 총 근무자 `{int(info['가입자수']):,}` 명
            - 신규 입사자 `{info['신규']:,}` 명
            - 퇴사자 `{info['상실']:,}` 명
            """
        )  

    col1, col2, col3 = st.columns(3)
    col1.text('월급여 추정')
    col1.markdown(f"`{int(output.iloc[0]['월급여추정']):,}` 원")

    col2.text('연봉 추정')
    col2.markdown(f"`{int(output.iloc[0]['연간급여추정']):,}` 원")

    col3.text('가입자수 추정')
    col3.markdown(f"`{int(output.iloc[0]['가입자수']):,}` 명")

    comp_output = data.compare_company(company_name = company_name)
    st.dataframe(comp_output.round(0), use_container_width=True)

    st.markdown(f'### 업종 평균 VS {company_name} 비교')
    # 검색은 회사의 '월급여추정'액과 업종평균을 비교
    percent_value = info['월급여추정'] / comp_output.iloc[0, 0] * 100 - 100
    diff_month = abs(comp_output.iloc[0, 0] - info['월급여추정'])  # 월급여추정 액의 차이
    diff_year = abs(comp_output.iloc[1, 0] - info['연간급여추정'])  # 연간급여추정 액의 차이
    upordown = '높은' if percent_value > 0 else '낮은'  # %값이 높은지 낮은지에 따른 문구 선택
    # 위 결과로 아래에 markdown 으로 출력
    st.markdown(f"""
    - 업종 **평균 월급여**는 `{int(comp_output.iloc[0, 0]):,}` 원, **평균 연봉**은 `{int(comp_output.iloc[1, 0]):,}` 원 입니다.
    - `{company_name}`는 평균 보다 `{int(diff_month):,}` 원, :red[약 {percent_value:.2f} %] `{upordown}` `{int(info['월급여추정']):,}` 원을 **월 평균 급여**를 받는 것으로 추정합니다.
    - `{company_name}`는 평균 보다 `{int(diff_year):,}` 원 `{upordown}` `{int(info['연간급여추정']):,}` 원을 **연봉**을 받는 것으로 추정합니다.
    """)
   
    fig, ax = plt.subplots(1, 2)

    p1 = ax[0].bar(x=["Average", "Your Company"], height=(comp_output.iloc[0, 0], info['월급여추정']), width=0.7)
    ax[0].bar_label(p1, fmt='%d')
    p1[0].set_color('black')
    p1[1].set_color('red')
    ax[0].set_title('Monthly Salary')

    p2 = ax[1].bar(x=["Average", "Your Company"], height=(comp_output.iloc[1, 0], info['연간급여추정']), width=0.7)
    p2[0].set_color('black')
    p2[1].set_color('red')
    ax[1].bar_label(p2, fmt='%d')
    ax[1].set_title('Yearly Salary')

    ax[0].tick_params(axis='both', which='major', labelsize=8, rotation=0)
    ax[0].tick_params(axis='both', which='minor', labelsize=6)
    ax[1].tick_params(axis='both', which='major', labelsize=8)
    ax[1].tick_params(axis='both', which='minor', labelsize=6)

    st.pyplot(fig)

    st.markdown('### 동종업계')
    df = data.get_data()
    st.dataframe(df.loc[df['업종코드'] == info['업종코드'], ['사업장명', '월급여추정', '연간급여추정', '가입자수']]\
        .sort_values('연간급여추정', ascending=False).head(10).round(0),
        use_container_width=True
    )
else:
    st.subheader('검색결과가 없습니다')       
    


