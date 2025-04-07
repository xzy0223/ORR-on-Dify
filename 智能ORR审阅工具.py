import streamlit as st
import os
import dotenv

st.set_page_config(
    page_title="ORR on LLM",
    page_icon="👋",
)

# 加载.env文件（如果存在）
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(dotenv_path):
    dotenv.load_dotenv(dotenv_path)

# 初始化会话状态，优先使用环境变量
if 'dify_api_key' not in st.session_state:
    st.session_state.dify_api_key = os.environ.get('DIFY_API_KEY', "dataset-pJPuLRgQ5nxTH84GYEb8QBin")
if 'dify_api_base_url' not in st.session_state:
    st.session_state.dify_api_base_url = os.environ.get('DIFY_API_BASE_URL', "http://54.200.9.115/v1")
if 'dify_consol_api_base_url' not in st.session_state:
    st.session_state.dify_consol_api_base_url = os.environ.get('DIFY_CONSOL_API_BASE_URL', "http://54.200.9.115/console/api/apps")
if 'dify_consol_api_key' not in st.session_state:
    st.session_state.dify_consol_api_key = os.environ.get('DIFY_CONSOL_API_KEY', "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZDYyMDYzZmUtZGQ3OC00MTI5LTgxMjktY2U5MzI5MmQ0MTUyIiwiZXhwIjoxNzMzOTkyMDM4LCJpc3MiOiJTRUxGX0hPU1RFRCIsInN1YiI6IkNvbnNvbGUgQVBJIFBhc3Nwb3J0In0.ASN8pExHXJ7w1-wn8qm13Bw1d8X0x_xZIuO9nKF1FDU")

st.write("# 欢迎使用 ORR on LLM 👋")

# 移除侧边栏显示设置链接

st.markdown(
    """
    这是一个面向ORR的生产力工具，你可以通过这个工具自动化的基于公司ORR的模版审阅你的应用程序设计文档，并得到相应的ORR审阅报告
    
    ### 你需要做什么:
    #### 在开始之前请先在“设置”中完成dify的配置
    - 第一步，在侧边框选择"上传文档"，将应用程序对应的设计文档上传到知识库中
    - 第二步，在侧边框选择"审阅应用"，选择应用程序对应的知识库和你要使用的ORR模版，并点击"开始审阅"
"""
)
