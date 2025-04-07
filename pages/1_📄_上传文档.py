import streamlit as st
import numpy as np
import requests
import json
import mimetypes
import os
import dotenv

st.set_page_config(page_title="上传文档", page_icon="📄")

# 加载.env文件（如果存在）
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(dotenv_path):
    dotenv.load_dotenv(dotenv_path)

# 初始化会话状态，优先使用环境变量
if 'dify_dataset_api_key' not in st.session_state:
    st.session_state.dify_dataset_api_key = os.environ.get('DIFY_DATASET_API_KEY', "dataset-pJPuLRgQ5nxTH84GYEb8QBin")
if 'dify_api_base_url' not in st.session_state:
    st.session_state.dify_api_base_url = os.environ.get('DIFY_API_BASE_URL', "http://54.200.9.115/v1")

# 使用会话状态中的配置
DIFY_DATASET_API_KEY = st.session_state.dify_dataset_api_key
DIFY_API_BASE_URL = st.session_state.dify_api_base_url

# 移除侧边栏显示Dify配置和设置链接

def is_text_file(file):
    mime_type, _ = mimetypes.guess_type(file.name)
    return mime_type and mime_type.startswith('text')

def create_kb(name):
    url = f"{DIFY_API_BASE_URL}/datasets"
    headers = {
        "Authorization": f"Bearer {DIFY_DATASET_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {"name": name}
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # 检查HTTP错误
        return response.json()
    except requests.exceptions.JSONDecodeError as e:
        st.error(f"无法解析API响应。请检查API端点是否正确: {str(e)}")
        return {"error": "JSON解析错误"}
    except requests.exceptions.RequestException as e:
        st.error(f"创建知识库时发生请求错误: {str(e)}")
        return {"error": f"请求错误: {str(e)}"}
    except Exception as e:
        st.error(f"创建知识库时发生未知错误: {str(e)}")
        return {"error": f"未知错误: {str(e)}"}

def get_kb_list():
    url = f"{DIFY_API_BASE_URL}/datasets"
    headers = {"Authorization": f"Bearer {DIFY_DATASET_API_KEY}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查HTTP错误
        return response.json().get("data", [])
    except requests.exceptions.JSONDecodeError:
        st.error("无法解析API响应。请检查API端点是否正确。")
        return []
    except requests.exceptions.RequestException as e:
        st.error(f"获取知识库列表时发生错误: {str(e)}")
        return []

def get_kb_documents(kb_id, page=1, limit=20):
    url = f"{DIFY_API_BASE_URL}/datasets/{kb_id}/documents"
    headers = {"Authorization": f"Bearer {DIFY_DATASET_API_KEY}"}
    params = {
        "page": page,
        "limit": limit
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching documents: {response.status_code} - {response.text}")

def upload_document(kb_id, file_content, file_name, is_text=True):
    
    if is_text:
        url = f"{DIFY_API_BASE_URL}/datasets/{kb_id}/document/create_by_text"
        headers = {
            "Authorization": f"Bearer {DIFY_DATASET_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "name": file_name,
            "text": file_content,
            "indexing_technique": "high_quality",
            "process_rule": {
                "rules": {
                    "pre_processing_rules": [
                        {"id": "remove_extra_spaces", "enabled": True},
                        {"id": "remove_urls_emails", "enabled": True}
                    ],
                    "segmentation": {
                        "separator": "\n",
                        "max_tokens": 500
                    },
                },
                "mode":"custom"
            }
        }
        response = requests.post(url, headers=headers, json=data)
    else:
        url = f"{DIFY_API_BASE_URL}/datasets/{kb_id}/document/create_by_file"
        headers = {
            "Authorization": f"Bearer {DIFY_DATASET_API_KEY}",
        }
        files = {
            'file': (file_name, file_content, mimetypes.guess_type(file_name)[0])
        }
        data = {
            'data': json.dumps({
                "indexing_technique": "high_quality",
                "process_rule": {
                    "rules": {
                        "pre_processing_rules": [
                            {"id": "remove_extra_spaces", "enabled": True},
                            {"id": "remove_urls_emails", "enabled": True}
                        ],
                        "segmentation": {
                            "separator": "###",
                            "max_tokens": 500
                        }
                    },
                    "mode": "custom"
                }
            })
        }
        
        response = requests.post(url, headers=headers, files=files, data=data)
        print(response)
    return response.json()

st.title("知识库管理助手")

# 显示提示信息
st.info("注意：上传文档需要使用 Dify Dataset API Key，请确保在设置页面中正确配置。")

# 选择知识库
kb_option = st.radio("选择知识库操作", ("使用现有知识库", "创建新知识库"))

if kb_option == "使用现有知识库":
    kb_list = get_kb_list()
    if not kb_list:
        st.warning("没有找到任何知识库或无法连接到API。请检查API配置或创建新的知识库。")
    else:
        kb_names = [kb["name"] for kb in kb_list]
        selected_kb = st.selectbox("选择知识库", kb_names)
        selected_kb_id = next(kb["id"] for kb in kb_list if kb["name"] == selected_kb)
        
        # 将选择的知识库ID存储在session_state中
        st.session_state.selected_kb_id = selected_kb_id
        
        # 分页控制
        try:
            documents = get_kb_documents(selected_kb_id)
            
            st.write(f"总文档数: {documents['total']}")
            st.write(f"当前页: {documents['page']}")
            
            # 创建一个表格来显示文档
            table_data = []
            for doc in documents['data']:
                table_data.append([doc['id'], doc['name'], doc['created_at']])

            st.dataframe(
                data=table_data,
                column_config={
                    1: st.column_config.TextColumn("文档ID"),
                    2: st.column_config.TextColumn("文档名称"),
                    3: st.column_config.DatetimeColumn("创建时间")
                },
                hide_index=True
            )
                
        except Exception as e:
            st.error(f"获取文档时发生错误: {str(e)}")
else:
    new_kb_name = st.text_input("输入新知识库名称")
    if st.button("创建知识库"):
        if new_kb_name:
            result = create_kb(new_kb_name)
            if "error" in result:
                st.error(f"创建知识库失败: {result['error']}")
            elif "id" in result:
                st.success(f"知识库 '{new_kb_name}' 创建成功！")
                selected_kb_id = result["id"]
                # 将新创建的知识库ID存储在session_state中
                st.session_state.selected_kb_id = selected_kb_id
            else:
                st.error(f"创建知识库失败，返回了意外的响应: {result}")
        else:
            st.warning("请输入知识库名称。")

# 文件上传
uploaded_file = st.file_uploader("选择要上传的文档", type=["txt", "pdf", "doc", "docx"])

if uploaded_file is not None:
    is_text = True
    if st.button("上传文档"):
        if is_text_file(uploaded_file):
            try:
                file_content = uploaded_file.getvalue().decode("utf-8")
            except UnicodeDecodeError:
                st.error(f"无法解码文件 '{uploaded_file.name}'。可能不是文本文件或编码不是UTF-8。")
                st.stop()
        else:
            is_text = False
            file_content = uploaded_file.getvalue()
            st.warning(f"'{uploaded_file.name}' 不是文本文件。将以二进制形式上传。")
        
        file_name = uploaded_file.name
        
        if "selected_kb_id" in st.session_state:
            try:
                result = upload_document(st.session_state.selected_kb_id, file_content, file_name, is_text)
                if "id" in result["document"]:
                    st.success(f"文档 '{file_name}' 上传成功！")
                else:
                    st.error(f"文档上传失败: {result.get('message', '未知错误')}")
                    st.write(result)
            except Exception as e:
                st.error(f"上传过程中发生错误: {str(e)}")
        else:
            st.warning("请先选择或创建一个知识库。")

        st.experimental_rerun()

# st.sidebar.info("注意：请确保您已经正确配置了Dify API密钥。")

# 显示当前选择的知识库ID（用于调试）
# if "selected_kb_id" in st.session_state:
#     st.sidebar.write(f"当前选择的知识库ID: {st.session_state.selected_kb_id}")
