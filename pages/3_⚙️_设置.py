import streamlit as st
import os
import dotenv

st.set_page_config(page_title="设置", page_icon="⚙️")

# 加载.env文件（如果存在）
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
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
    st.session_state.dify_consol_api_key = os.environ.get('DIFY_CONSOL_API_KEY', "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZDYyMDYzZmUtZGQ3OC00MTI5LTgxMjktY2U5MzI5MmQ0MTUyIiwiZXhwIjoxNzQ1NzU1OTEzLCJpc3MiOiJTRUxGX0hPU1RFRCIsInN1YiI6IkNvbnNvbGUgQVBJIFBhc3Nwb3J0In0.3iM2eg0EUHII-3LlsEIEzoGYpYLOjEL3m_7NDUm8fxY")

st.title("应用程序设置")

st.header("Dify API 配置")

with st.form("dify_settings_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("API URLs")
        dify_api_base_url = st.text_input(
            "Dify API Base URL", 
            value=st.session_state.dify_api_base_url,
            help="Dify API的基础URL，例如: http://your-dify-instance/v1"
        )
        
        dify_consol_api_base_url = st.text_input(
            "Dify Console API Base URL", 
            value=st.session_state.dify_consol_api_base_url,
            help="Dify Console API的基础URL，例如: http://your-dify-instance/console/api/apps"
        )
    
    with col2:
        st.subheader("API Keys")
        dify_api_key = st.text_input(
            "Dify API Key", 
            value=st.session_state.dify_api_key, 
            type="password",
            help="用于访问Dify API的密钥"
        )
        
        dify_consol_api_key = st.text_input(
            "Dify Console API Key", 
            value=st.session_state.dify_consol_api_key, 
            type="password",
            help="用于访问Dify Console API的密钥"
        )
    
    save_to_env = st.checkbox("保存到.env文件", value=False, help="将配置保存到.env文件中，以便在应用重启后保持配置")
    submit_button = st.form_submit_button("保存配置")
    
    if submit_button:
        st.session_state.dify_api_base_url = dify_api_base_url
        st.session_state.dify_api_key = dify_api_key
        st.session_state.dify_consol_api_base_url = dify_consol_api_base_url
        st.session_state.dify_consol_api_key = dify_consol_api_key
        
        if save_to_env:
            try:
                # 创建或更新.env文件
                with open(dotenv_path, 'w') as f:
                    f.write(f"DIFY_API_KEY={dify_api_key}\n")
                    f.write(f"DIFY_API_BASE_URL={dify_api_base_url}\n")
                    f.write(f"DIFY_CONSOL_API_BASE_URL={dify_consol_api_base_url}\n")
                    f.write(f"DIFY_CONSOL_API_KEY={dify_consol_api_key}\n")
                st.success("配置已保存到.env文件!")
            except Exception as e:
                st.error(f"保存到.env文件失败: {str(e)}")
        else:
            st.success("配置已保存到会话状态!")

# 显示当前配置
st.header("当前配置")
st.info(f"""
**Dify API Base URL**: {st.session_state.dify_api_base_url}  
**Dify Console API Base URL**: {st.session_state.dify_consol_api_base_url}
""")

# 测试连接
st.header("测试连接")
if st.button("测试Dify API连接"):
    import requests
    try:
        # 测试Dify API
        response = requests.get(
            f"{st.session_state.dify_api_base_url}/datasets", 
            headers={"Authorization": f"Bearer {st.session_state.dify_api_key}"}
        )
        if response.status_code == 200:
            st.success("Dify API连接成功!")
        else:
            st.error(f"Dify API连接失败: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"连接错误: {str(e)}")

# 高级设置
with st.expander("高级设置"):
    st.write("这里可以添加更多高级配置选项")
    
    # 重置为默认值
    if st.button("重置为默认值"):
        default_api_key = "dataset-pJPuLRgQ5nxTH84GYEb8QBin"
        default_api_base_url = "http://54.200.9.115/v1"
        default_consol_api_base_url = "http://54.200.9.115/console/api/apps"
        default_consol_api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZDYyMDYzZmUtZGQ3OC00MTI5LTgxMjktY2U5MzI5MmQ0MTUyIiwiZXhwIjoxNzQ1NzU1OTEzLCJpc3MiOiJTRUxGX0hPU1RFRCIsInN1YiI6IkNvbnNvbGUgQVBJIFBhc3Nwb3J0In0.3iM2eg0EUHII-3LlsEIEzoGYpYLOjEL3m_7NDUm8fxY"
        
        st.session_state.dify_api_key = default_api_key
        st.session_state.dify_api_base_url = default_api_base_url
        st.session_state.dify_consol_api_base_url = default_consol_api_base_url
        st.session_state.dify_consol_api_key = default_consol_api_key
        
        # 更新.env文件
        try:
            with open(dotenv_path, 'w') as f:
                f.write(f"DIFY_API_KEY={default_api_key}\n")
                f.write(f"DIFY_API_BASE_URL={default_api_base_url}\n")
                f.write(f"DIFY_CONSOL_API_BASE_URL={default_consol_api_base_url}\n")
                f.write(f"DIFY_CONSOL_API_KEY={default_consol_api_key}\n")
        except:
            pass
            
        st.success("已重置为默认值!")
