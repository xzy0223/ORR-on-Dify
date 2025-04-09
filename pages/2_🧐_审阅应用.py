import streamlit as st
import yaml
import requests
import os
import json
import boto3
import uuid
from sseclient import SSEClient
import pandas as pd
import dotenv

# 假设在另一个页面中，我们已经选择了知识库并保存在session state中
# 例如：st.session_state.selected_kb = "my_knowledge_base"

# 加载.env文件（如果存在）
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(dotenv_path):
    dotenv.load_dotenv(dotenv_path)

# 初始化会话状态，优先使用环境变量
if 'dify_api_key' not in st.session_state:
    st.session_state.dify_api_key = os.environ.get('DIFY_API_KEY', "dataset-pJPuLRgQ5nxTH84GYEb8QBin")
if 'dify_dataset_api_key' not in st.session_state:
    st.session_state.dify_dataset_api_key = os.environ.get('DIFY_DATASET_API_KEY', os.environ.get('DIFY_API_KEY', "dataset-pJPuLRgQ5nxTH84GYEb8QBin"))
if 'dify_api_base_url' not in st.session_state:
    st.session_state.dify_api_base_url = os.environ.get('DIFY_API_BASE_URL', "http://54.200.9.115/v1")
if 'dify_consol_api_base_url' not in st.session_state:
    st.session_state.dify_consol_api_base_url = os.environ.get('DIFY_CONSOL_API_BASE_URL', "http://54.200.9.115/console/api/apps")
if 'dify_consol_api_key' not in st.session_state:
    st.session_state.dify_consol_api_key = os.environ.get('DIFY_CONSOL_API_KEY', "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZDYyMDYzZmUtZGQ3OC00MTI5LTgxMjktY2U5MzI5MmQ0MTUyIiwiZXhwIjoxNzMzOTkyMDM4LCJpc3MiOiJTRUxGX0hPU1RFRCIsInN1YiI6IkNvbnNvbGUgQVBJIFBhc3Nwb3J0In0.ASN8pExHXJ7w1-wn8qm13Bw1d8X0x_xZIuO9nKF1FDU")

# 使用会话状态中的配置
DIFY_API_KEY = st.session_state.dify_dataset_api_key  # 使用dataset API key而不是普通API key
DIFY_API_BASE_URL = st.session_state.dify_api_base_url
DIFY_CONSOL_API_BASE_URL = st.session_state.dify_consol_api_base_url
DIFY_CONSOL_API_KEY = st.session_state.dify_consol_api_key

# 移除侧边栏显示Dify配置和设置链接

# 初始化会话状态，session setp用于保存当前的流程状态
if 'step' not in st.session_state:
    st.session_state.step = 1

# 定义步骤数
TOTAL_STEPS = 5


def load_yaml_file(file_path):
    with open(file_path, 'r') as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as e:
            st.error(f"Error loading YAML file: {e}")
            return None

def get_kb_list():
    url = f"{DIFY_API_BASE_URL}/datasets"
    headers = {"Authorization": f"Bearer {DIFY_API_KEY}"}
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            st.error(f"API错误: {response.status_code} - {response.text}")
            return []
            
        data = response.json()
        
        if "data" not in data:
            st.warning("API响应中不包含'data'字段")
            return []
            
        return data.get("data", [])
    except Exception as e:
        st.error(f"获取知识库列表时发生错误: {str(e)}")
        return []

def create_workflow(config):
    url = f"{DIFY_CONSOL_API_BASE_URL}/import"
    headers = {
        "Authorization": f"Bearer {DIFY_CONSOL_API_KEY}", 
        "Content-Type": "application/json"
    }
    data = {
            'data': json.dumps(config)
        }

    response = requests.post(url, headers=headers, json=data)
    return response

def get_workflow_api_key(workflow_id):
    url = f"{DIFY_CONSOL_API_BASE_URL}/{workflow_id}/api-keys"
    headers = {"Authorization": f"Bearer {DIFY_CONSOL_API_KEY}"}
    response = requests.post(url, headers=headers)
    # if response.status_code == 200:
    #     response = requests.get(url, headers=headers)
    return response.json().get("token", {})

def run_workflow(api_key, payload):
    url = f"{DIFY_API_BASE_URL}/workflows/run"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }


    response_area = st.empty()
    
    response = requests.post(url, headers=headers, json=payload, stream=True)

    # 使用SSEClient处理响应
    client = SSEClient(response)

    with response_area.container():

        for event in client.events():
            try:
                event_data = json.loads(event.data)
                event_type = event_data.get('event')
                
                if event_type == 'workflow_started':
                    st.write("工作流开始执行")
                elif event_type == 'node_started':
                    st.write(f"节点开始: {event_data['data']['title']}")
                elif event_type == 'node_finished':
                    st.write(f"节点完成: {event_data['data']['title']}")
                    if 'outputs' in event_data['data']:
                        print(f"输出: {event_data['data']['outputs']}")
                elif event_type == 'workflow_finished':
                    outputs = event_data['data'].get('outputs', {})
                    print(outputs['workload_id'])
                    st.write("工作流执行完成")
                    st.write(f"总耗时: {event_data['data']['elapsed_time']} 秒")
                    return outputs['workload_id']
                else:
                    print(f"未知事件类型: {event_type}")
            except json.JSONDecodeError:
                print(f"无法解析JSON: {event.data}")

# get lens arn from AWS WA custom lens
def get_custom_lenses():
    """
    获取AWS Well-Architected Tool中的自定义镜头列表
    
    返回:
    - 包含自定义镜头名称和ARN的字典列表
    """
    # 创建Well-Architected Tool客户端
    wa_client = boto3.client('wellarchitected')
    
    custom_lenses = []
    next_token = None
    
    # 使用分页获取所有自定义镜头
    while True:
        if next_token:
            response = wa_client.list_lenses(
                LensType='CUSTOM_SELF',
                NextToken=next_token
            )
        else:
            response = wa_client.list_lenses(LensType='CUSTOM_SELF')
        
        for lens in response['LensSummaries']:
            custom_lenses.append({
                'name': lens['LensName'],
                'arn': lens['LensArn']
            })
        
        # 检查是否有更多结果
        if 'NextToken' in response:
            next_token = response['NextToken']
        else:
            break
    
    return custom_lenses

def get_lens_review_result(workload_id, lens_alias):
    wa_client = boto3.client('wellarchitected')
    # 获取workload详情
    workload = wa_client.get_workload(WorkloadId=workload_id)
    print(f"Workload Name: {workload['Workload']['WorkloadName']}")
    
    # 获取lens review result
    lens_result = wa_client.get_lens_review(
        WorkloadId=workload_id,
        LensAlias=lens_alias,
        # PillarId='ALL'
    )

    return lens_result
   
def show_progress():
    st.progress(st.session_state.step / TOTAL_STEPS)
    st.write(f"Step {st.session_state.step} of {TOTAL_STEPS}")

def step_1():
    st.header("Step 1: Select YAML Configuration File")
    # 步骤1的逻辑
    current_dir = os.getcwd()
    yaml_files = [f for f in os.listdir(current_dir) if f.endswith(('.yaml', '.yml'))]
    
    if yaml_files:
        # 处理文件
        selected_file = st.selectbox("Select a YAML configuration file:", yaml_files)
        st.session_state.selected_file = selected_file

        if selected_file:
            file_path = os.path.join(current_dir, selected_file)
            config = load_yaml_file(file_path)
            st.session_state.config = config

            if config:
                st.success(f"Successfully loaded {selected_file}")
                if st.button("Next"):
                    st.session_state.step = 2
                    st.experimental_rerun()
        
def step_2():
    st.header("Step 2: 选择知识库")
    
    # 显示API配置信息
    with st.expander("API配置信息"):
        st.write(f"Dify API Base URL: {DIFY_API_BASE_URL}")
        st.write(f"Dify Dataset API Key: {DIFY_API_KEY[:5]}...{DIFY_API_KEY[-5:] if len(DIFY_API_KEY) > 10 else ''}")
        st.write(f"使用的API密钥类型: {'Dataset API Key' if DIFY_API_KEY.startswith('dataset-') else 'Regular API Key'}")
    
    # 添加手动刷新按钮
    if st.button("🔄 刷新知识库列表"):
        st.session_state.kb_list_cache = None
        st.experimental_rerun()
    
    # 获取知识库列表
    try:
        if 'kb_list_cache' not in st.session_state:
            with st.spinner("正在获取知识库列表..."):
                kb_list = get_kb_list()
                st.session_state.kb_list_cache = kb_list
        else:
            kb_list = st.session_state.kb_list_cache
        
        # 检查是否有预先选择的知识库ID
        if 'selected_kb_id' in st.session_state:
            kb_id = st.session_state.selected_kb_id
            
            # 查找匹配的知识库
            kb_name = None
            for kb in kb_list:
                if kb['id'] == kb_id:
                    kb_name = kb['name']
                    st.session_state.selected_kb = kb_name
                    break
            
            if kb_name:
                st.success(f"已选择知识库: {kb_name}")
                
                if st.button("下一步"):
                    st.session_state.step = 3
                    st.experimental_rerun()
            else:
                st.warning(f"找不到ID为 {kb_id} 的知识库，请重新选择")
                # 重置选择
                if 'selected_kb_id' in st.session_state:
                    del st.session_state.selected_kb_id
                if 'selected_kb' in st.session_state:
                    del st.session_state.selected_kb
        
        # 显示可用的知识库列表
        if kb_list:
            st.subheader("可用的知识库")
            kb_options = [f"{kb['name']} (ID: {kb['id']})" for kb in kb_list]
            selected_option = st.selectbox("选择知识库:", kb_options)
            
            if selected_option:
                selected_id = selected_option.split("ID: ")[1].strip(")")
                selected_name = selected_option.split(" (ID:")[0]
                
                if st.button("使用此知识库"):
                    st.session_state.selected_kb_id = selected_id
                    st.session_state.selected_kb = selected_name
                    st.success(f"已选择知识库: {selected_name}")
                    st.experimental_rerun()
        else:
            st.error("没有找到任何知识库。请先在「上传文档」页面创建知识库。")
            
    except Exception as e:
        st.error(f"获取知识库列表时发生错误: {str(e)}")
        st.info("请检查API配置是否正确，并确保Dify服务可访问。")
        
        # 提供修复建议
        st.subheader("可能的解决方案")
        st.markdown("""
        1. 检查「设置」页面中的API配置是否正确
        2. 确保使用的是Dataset API Key而不是普通API Key
        3. 确认Dify服务器是否正常运行
        4. 检查网络连接是否正常
        """)
        
        # 提供手动输入选项
        st.subheader("手动输入知识库信息")
        manual_kb_id = st.text_input("知识库ID:", value=st.session_state.get('selected_kb_id', ''))
        manual_kb_name = st.text_input("知识库名称:", value=st.session_state.get('selected_kb', ''))
        
        if st.button("使用手动输入的知识库"):
            if manual_kb_id and manual_kb_name:
                st.session_state.selected_kb_id = manual_kb_id
                st.session_state.selected_kb = manual_kb_name
                st.success(f"已手动设置知识库: {manual_kb_name}")
                
                if st.button("继续下一步"):
                    st.session_state.step = 3
                    st.experimental_rerun()
    
def step_3():
    st.header("Step 3: Create Workflow")

    # 步骤3的逻辑
    if 'selected_kb_id' not in st.session_state:
        st.warning("No knowledge base selected. Please select a knowledge base in the other page first.")
        return
    else:
        selected_kb_id = st.session_state.selected_kb_id

    if 'config' not in st.session_state:
        st.warning("No configuration loaded. Please select a YAML configuration file in the previous step.")
        return
    else:
        config = st.session_state.config

    if 'selected_file' not in st.session_state:
        st.warning("No file selected. Please select a YAML configuration file in the previous step.")
        return
    else:
        file_name = st.session_state.selected_file
        yaml_file_name = file_name.split('.')[0]

    if 'selected_kb' not in st.session_state:
        st.warning("No knowledge base selected. Please select a knowledge base in the other page first.")
        return
    else:
        selected_kb = st.session_state.selected_kb
    
    workload_name = st.text_input("请输入应用名称", "example app")
    workload_desc = st.text_area("请输入应用描述", "example desc")
    workload_env = st.selectbox("请选择应用环境", ['PRODUCTION', 'PREPRODUCTION'])
    
    custom_lenses_list = get_custom_lenses()
    custom_lenses_name = [lens['name'] for lens in custom_lenses_list]
    orr_len_name = st.selectbox("请选择ORR模版", custom_lenses_name)
    orr_len_arn = next((lens['arn'] for lens in custom_lenses_list if lens['name'] == orr_len_name), None)

    st.session_state.workload_name = workload_name
    st.session_state.workload_desc = workload_desc
    st.session_state.workload_env = workload_env
    st.session_state.orr_len_arn = orr_len_arn

    workflow_name = workload_name + '-' + yaml_file_name + '-' + selected_kb
    config['workflow']['graph']['nodes'][6]['data']['dataset_ids'] = [selected_kb_id]
    config['app']['name'] = workflow_name

    if st.button("Create Workflow"):
        response = create_workflow(config)
        print(response.status_code)
        if response.status_code == 201:
            workflow_id = json.loads(response.text)['id']
            st.session_state.workflow_id = workflow_id
            st.success(f"Workflow {workflow_name}({workflow_id}) created successfully!")
            st.session_state.step = 4
            st.experimental_rerun()

        else:
            print(f"发生错误，状态码：{response.status_code}")
    
def step_4():
    st.header("Step 4: Start Workflow")

    button_container = st.container()

    if 'workflow_started' not in st.session_state:
        st.session_state.workflow_started = False

    # 步骤4的逻辑
    start_workflow = button_container.button("Start Workflow")
    workflow_id = st.session_state.workflow_id
    
    orr_len_arn = st.session_state.orr_len_arn
    workload_name = st.session_state.workload_name
    workload_desc = st.session_state.workload_desc
    workload_env = st.session_state.workload_env
    
    if start_workflow or st.session_state.workflow_started:
        if not st.session_state.workflow_started:
            workflow_api_key = get_workflow_api_key(workflow_id)
            payload = {
                "inputs": {
                    "orr_lens_arn": orr_len_arn,
                    "workload_name": workload_name + str(uuid.uuid4())[:15],
                    "description": workload_desc,
                    "environment": workload_env
                },
                "response_mode": "streaming",
                "user": "hlxiao"
            }

            wa_workload_id = run_workflow(workflow_api_key, payload)
            
            if wa_workload_id:
                st.session_state.wa_workload_id = wa_workload_id
                st.success(f"Workflow started successfully!")
                st.session_state.workflow_started = True

        next_button = button_container.button("Next")
        if next_button:
            st.session_state.step = 5
            st.experimental_rerun()

def step_5():
    st.header("Step 5: Workflow Result")

    review_result = get_lens_review_result(
        st.session_state.wa_workload_id, 
        st.session_state.orr_len_arn
        )
    
    if not review_result:
        st.error("No lens review result found. Please press \"Rerun\" to finish the whole process")

    else:
        # Extract LensName
        lens_name = review_result['LensReview']['LensName']

        # Display LensName
        st.title(f"Lens Review: {lens_name}")

        # Extract pillar names and risk counts
        pillar_data = []
        for pillar in review_result['LensReview']['PillarReviewSummaries']:
            pillar_name = pillar['PillarName']
            risk_counts = pillar['RiskCounts']
            pillar_data.append({
                'Pillar Name': pillar_name,
                'UNANSWERED': risk_counts['UNANSWERED'],
                'HIGH': risk_counts['HIGH'],
                'MEDIUM': risk_counts['MEDIUM'],
                'NONE': risk_counts['NONE'],
                'NOT_APPLICABLE': risk_counts['NOT_APPLICABLE']
            })

        # Create a DataFrame from the pillar data
        df = pd.DataFrame(pillar_data)

        # Display the DataFrame as a table
        st.table(df)

        # Create a bar chart of risk counts for each pillar
        st.bar_chart(df.set_index('Pillar Name'))

def main():
    st.title("应用ORR审阅工作流")

    # 创建一个固定位置的容器用于放置右上角按钮
    button_container = st.container()

    # 添加自定义CSS来调整按钮容器的位置
    st.markdown(
        """
        <style>
        #Reset {
            position: fixed;
            top: 60px;
            right: 10px;
            z-index: 999;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 在容器中添加按钮
    with button_container:
        st.markdown('<div id="Reset">', unsafe_allow_html=True)
        if st.button("Reset"):
            st.session_state.step = 1
            st.session_state.workflow_started = False
            st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    show_progress()

    if st.session_state.step == 1:
        step_1()
    elif st.session_state.step == 2:
        step_2()
    elif st.session_state.step == 3:
        step_3()
    elif st.session_state.step == 4:
        step_4()
    elif st.session_state.step == 5:
        step_5()
                        

if __name__ == "__main__":
    main()