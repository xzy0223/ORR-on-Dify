import streamlit as st
import numpy as np
import requests
import json
import mimetypes
import os
import dotenv
import pandas as pd
import time

st.set_page_config(page_title="上传文档", page_icon="📄")

# 加载.env文件（如果存在）
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(dotenv_path):
    dotenv.load_dotenv(dotenv_path)

# 初始化会话状态，优先使用环境变量
if 'dify_dataset_api_key' not in st.session_state:
    st.session_state.dify_dataset_api_key = os.environ.get('DIFY_DATASET_API_KEY', os.environ.get('DIFY_API_KEY', ""))

# 初始化session state变量
if 'selected_kb_id' not in st.session_state:
    st.session_state.selected_kb_id = None
if 'documents' not in st.session_state:
    st.session_state.documents = None
if 'doc_ids' not in st.session_state:
    st.session_state.doc_ids = []
if 'table_data' not in st.session_state:
    st.session_state.table_data = []
if 'dify_api_base_url' not in st.session_state:
    st.session_state.dify_api_base_url = os.environ.get('DIFY_API_BASE_URL', "http://54.200.9.115/v1")
if 'refresh_needed' not in st.session_state:
    st.session_state.refresh_needed = False

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
    except requests.exceptions.JSONDecodeError as e:
        st.error(f"无法解析API响应。请检查API端点是否正确。{str(e)}")
        st.error(os.environ.get('DIFY_API_BASE_URL', "http://54.200.9.115/v1"))
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
        
def delete_document(kb_id, doc_id):
    """删除知识库中的文档"""
    url = f"{DIFY_API_BASE_URL}/datasets/{kb_id}/documents/{doc_id}"
    headers = {"Authorization": f"Bearer {DIFY_DATASET_API_KEY}"}
    try:
        response = requests.delete(url, headers=headers)
        if response.status_code == 200 or response.status_code == 204:
            return True, "文档删除成功"
        else:
            return False, f"删除文档失败: {response.status_code} - {response.text}"
    except Exception as e:
        return False, f"删除文档时发生错误: {str(e)}"
        return "获取失败"
        return "获取失败"

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

st.title("📚 知识库管理助手")

# 添加一个美观的顶部卡片
st.markdown("""
<div style="padding: 15px; border-radius: 10px; background-color: #f0f7ff; margin-bottom: 20px; border-left: 5px solid #0068c9;">
    <h3 style="margin-top: 0; color: #0068c9;">欢迎使用知识库管理助手</h3>
    <p>在这里您可以创建知识库、上传文档和管理现有文档。上传文档需要使用 Dify Dataset API Key，请确保在设置页面中正确配置。</p>
</div>
""", unsafe_allow_html=True)

# 添加刷新按钮，使用更美观的布局
col1, col2 = st.columns([5, 1])
with col1:
    st.subheader("📋 文档管理")
with col2:
    st.write("")
    if st.button("🔄 刷新", key="refresh_docs", help="刷新文档列表"):
        st.session_state.refresh_needed = True
        st.session_state.documents = None  # 强制重新获取文档

# 选择知识库
kb_list = get_kb_list()

# 添加创建新知识库的功能 - 使用卡片样式
st.markdown("""
<div style="padding: 15px; border-radius: 10px; background-color: #f5f5f5; margin: 10px 0; border-left: 5px solid #4CAF50;">
    <h3 style="margin-top: 0; color: #4CAF50;">✨ 创建新知识库</h3>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])
with col1:
    new_kb_name = st.text_input("输入新知识库名称", key="new_kb_name", placeholder="例如：项目设计文档")
with col2:
    st.write("")
    st.write("")
    create_button = st.button("🆕 创建知识库", type="primary", help="创建一个新的知识库")
    if create_button:
        if new_kb_name:
            with st.spinner(f"正在创建知识库 '{new_kb_name}'..."):
                result = create_kb(new_kb_name)
                if "id" in result:
                    st.success(f"知识库 '{new_kb_name}' 创建成功！")
                    st.session_state.refresh_needed = True
                    st.rerun()  # 刷新页面以更新知识库列表
                else:
                    st.error(f"创建知识库失败: {result.get('error', '未知错误')}")
        else:
            st.warning("请输入知识库名称")

# 选择知识库部分 - 使用卡片样式
st.markdown("""
<div style="padding: 15px; border-radius: 10px; background-color: #f5f5f5; margin: 20px 0 10px 0; border-left: 5px solid #2196F3;">
    <h3 style="margin-top: 0; color: #2196F3;">🔍 选择知识库</h3>
</div>
""", unsafe_allow_html=True)

if not kb_list:
    st.warning("没有找到任何知识库或无法连接到API。请检查API配置或创建一个新的知识库。")
else:
    kb_names = [kb["name"] for kb in kb_list]
    
    # 检查是否有知识库选择变化
    if 'previous_kb_selection' not in st.session_state:
        st.session_state.previous_kb_selection = None
    
    # 如果已经有选择的知识库，则默认选择该知识库
    default_index = 0
    if st.session_state.previous_kb_selection in kb_names:
        default_index = kb_names.index(st.session_state.previous_kb_selection)
    
    selected_kb = st.selectbox("选择知识库", kb_names, index=default_index)
    selected_kb_id = next(kb["id"] for kb in kb_list if kb["name"] == selected_kb)
    
    # 检测知识库选择是否变化
    if st.session_state.previous_kb_selection != selected_kb:
        st.session_state.refresh_needed = True
        st.session_state.documents = None  # 清除当前文档缓存
        st.session_state.previous_kb_selection = selected_kb
    
    # 将选择的知识库ID存储在session_state中
    st.session_state.selected_kb_id = selected_kb_id
    
    # 如果需要刷新或者文档为空，则获取文档
    if st.session_state.refresh_needed or st.session_state.documents is None:
        try:
            with st.spinner("正在加载文档列表..."):
                documents = get_kb_documents(selected_kb_id)
                st.session_state.documents = documents  # 保存到session state
            
            # 使用更美观的方式显示文档数量信息
            col1, col2 = st.columns(2)
            with col1:
                st.metric("总文档数", documents['total'])
            with col2:
                st.metric("当前页", documents['page'])
            
            # 创建一个表格来显示文档
            table_data = []
            doc_ids = []  # 存储文档ID，用于删除操作
            
            for doc in documents['data']:
                # 获取文档状态
                status = doc.get('indexing_status', '未知')
                display_status = doc.get('display_status', '未知')
                
                # 获取文档名称和其他信息
                doc_name = doc.get('name', '未知文档名')
                doc_id = doc.get('id', '')
                doc_ids.append(doc_id)  # 添加到ID列表
                
                # 将时间戳转换为人类可读的日期时间格式
                timestamp = doc.get('created_at', '')
                if timestamp:
                    # 转换时间戳为datetime对象，然后格式化
                    from datetime import datetime
                    created_at = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    created_at = '未知时间'
                
                # 如果有错误信息，添加到状态中
                error_info = doc.get('error', None)
                status_display = f"{status}"
                if error_info:
                    status_display = f"{status} (错误: {error_info})"
                elif display_status != status:
                    status_display = f"{status} ({display_status})"
                
                table_data.append({"文档ID": doc_id, "文档名称": doc_name, "创建时间": created_at, "文档状态": status_display})

            # 保存到session state
            st.session_state.doc_ids = doc_ids
            st.session_state.table_data = table_data

            # 使用字典列表创建DataFrame，添加样式
            if table_data:
                df = pd.DataFrame(table_data)
                st.dataframe(df, hide_index=True, use_container_width=True)
            else:
                st.info("该知识库中没有文档。请上传新文档。")
                
        except Exception as e:
            st.error(f"获取文档时发生错误: {str(e)}")
            # 如果有之前保存的数据，则使用之前的数据
            if 'documents' in st.session_state and st.session_state.documents is not None:
                documents = st.session_state.documents
                doc_ids = st.session_state.doc_ids
                table_data = st.session_state.table_data
                
                # 显示之前的数据
                st.write("显示缓存的文档数据:")
                if documents and 'total' in documents:
                    st.metric("总文档数", documents['total'])
                if documents and 'page' in documents:
                    st.metric("当前页", documents['page'])
                    
                # 使用字典列表创建DataFrame
                if table_data:
                    df = pd.DataFrame(table_data)
                    st.dataframe(df, hide_index=True, use_container_width=True)
    else:
        # 如果不需要刷新且文档已存在，则显示现有文档
        if 'documents' in st.session_state and st.session_state.documents is not None:
            documents = st.session_state.documents
            
            # 使用更美观的方式显示文档数量信息
            col1, col2 = st.columns(2)
            with col1:
                if 'total' in documents:
                    st.metric("总文档数", documents['total'])
            with col2:
                if 'page' in documents:
                    st.metric("当前页", documents['page'])
            
            # 使用字典列表创建DataFrame
            if 'table_data' in st.session_state and st.session_state.table_data:
                df = pd.DataFrame(st.session_state.table_data)
                st.dataframe(df, hide_index=True, use_container_width=True)
            else:
                st.info("没有找到文档。请点击「刷新」按钮重新加载。")
            
    # 重置刷新标志
    st.session_state.refresh_needed = False

# 文件上传
st.markdown("""
<div style="padding: 15px; border-radius: 10px; background-color: #f5f5f5; margin: 20px 0 10px 0; border-left: 5px solid #FF9800;">
    <h3 style="margin-top: 0; color: #FF9800;">📤 上传新文档</h3>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])
with col1:
    uploaded_file = st.file_uploader("选择要上传的文档", type=["txt", "pdf", "doc", "docx"], help="支持txt、pdf、doc、docx格式")
with col2:
    st.write("")
    st.write("")

if uploaded_file is not None:
    is_text = True
    upload_button = st.button("📤 上传文档", type="primary", help="上传选择的文档到知识库")
    if upload_button:
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
                with st.spinner(f"正在上传文档 '{file_name}'..."):
                    result = upload_document(st.session_state.selected_kb_id, file_content, file_name, is_text)
                if "id" in result["document"]:
                    st.success(f"文档 '{file_name}' 上传成功！")
                    st.balloons()  # 添加气球效果庆祝成功
                    st.info("文档已上传，点击「刷新」按钮可查看最新文档。")
                else:
                    st.error(f"文档上传失败: {result.get('message', '未知错误')}")
                    st.write(result)
            except Exception as e:
                st.error(f"上传过程中发生错误: {str(e)}")
        else:
            st.warning("请先选择或创建一个知识库。")

# 添加分隔线
st.markdown("""
<hr style="height:2px;border:none;background-color:#e0e0e0;margin:30px 0">
""", unsafe_allow_html=True)

# 添加删除文档功能
st.markdown("""
<div style="padding: 15px; border-radius: 10px; background-color: #f5f5f5; margin: 10px 0; border-left: 5px solid #F44336;">
    <h3 style="margin-top: 0; color: #F44336;">🗑️ 删除文档</h3>
</div>
""", unsafe_allow_html=True)

if "selected_kb_id" in st.session_state and st.session_state.selected_kb_id:
    # 确保doc_ids已定义
    if 'doc_ids' in st.session_state and len(st.session_state.doc_ids) > 0:
        doc_ids = st.session_state.doc_ids
        table_data = st.session_state.table_data
        # 创建文档选择下拉框
        doc_options = [f"{i+1}. {table_data[i]['文档名称']} ({table_data[i]['文档ID']})" for i in range(len(table_data))]
        selected_doc = st.selectbox("选择要删除的文档", doc_options, help="选择要从知识库中删除的文档")
        
        if selected_doc:
            # 从选项中提取文档ID
            selected_index = doc_options.index(selected_doc)
            doc_id_to_delete = doc_ids[selected_index]
            doc_name_to_delete = table_data[selected_index]['文档名称']
            
            # 添加删除按钮
            col1, col2 = st.columns([3, 1])
            with col2:
                delete_button = st.button("🗑️ 删除文档", type="primary", help="从知识库中删除选中的文档")
                if delete_button:
                    with st.spinner("正在删除文档..."):
                        success, message = delete_document(st.session_state.selected_kb_id, doc_id_to_delete)
                        if success:
                            st.success(message)
                            # 标记需要刷新，而不是清除缓存
                            st.session_state.refresh_needed = True
                            st.rerun()  # 刷新页面以更新文档列表
                        else:
                            st.error(message)
            with col1:
                st.warning(f"确定要删除文档 '{doc_name_to_delete}' 吗？此操作不可撤销。")
    else:
        st.info("没有可删除的文档或文档列表尚未加载。请先上传文档或刷新文档列表。")
