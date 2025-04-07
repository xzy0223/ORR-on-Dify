#!/bin/bash

# 检查必要的环境变量
if [ -z "$DIFY_API_BASE_URL" ]; then
    echo "错误: 环境变量 DIFY_API_BASE_URL 未设置"
    echo "请先运行 Dify 部署脚本并设置环境变量:"
    echo "export DIFY_API_BASE_URL=http://your-dify-url"
    exit 1
fi

if [ -z "$DIFY_API_KEY" ]; then
    echo "错误: 环境变量 DIFY_API_KEY 未设置"
    echo "请在 Dify 控制台生成 API Key 并设置环境变量:"
    echo "export DIFY_API_KEY=your-api-key"
    exit 1
fi

if [ -z "$DIFY_CONSOL_API_KEY" ]; then
    echo "错误: 环境变量 DIFY_CONSOL_API_KEY 未设置"
    echo "请在 Dify 控制台生成 Console API Key 并设置环境变量:"
    echo "export DIFY_CONSOL_API_KEY=your-console-api-key"
    exit 1
fi

# 检查 Dataset API Key
if [ -z "$DIFY_DATASET_API_KEY" ]; then
    echo "警告: 环境变量 DIFY_DATASET_API_KEY 未设置"
    echo "将使用 DIFY_API_KEY 作为 Dataset API Key"
    echo "如需上传文档功能，请在 Dify 控制台知识库页面生成 Dataset API Key 并设置环境变量:"
    echo "export DIFY_DATASET_API_KEY=your-dataset-api-key"
fi

# 检查 Lambda API 环境变量
if [ -z "$GET_LENS_INFO_API_URL" ]; then
    echo "警告: 环境变量 GET_LENS_INFO_API_URL 未设置"
    echo "请先运行 Lambda 部署脚本并设置环境变量:"
    echo "export GET_LENS_INFO_API_URL=https://your-api-gateway-url/stage/get_lens_info"
    echo "将使用默认 API URL"
fi

if [ -z "$OPERATE_WA_TOOL_API_URL" ]; then
    echo "警告: 环境变量 OPERATE_WA_TOOL_API_URL 未设置"
    echo "请先运行 Lambda 部署脚本并设置环境变量:"
    echo "export OPERATE_WA_TOOL_API_URL=https://your-api-gateway-url/stage/workload"
    echo "将使用默认 API URL"
fi

# 检查 Well-Architected Tool 环境变量
if [ -z "$ORR_LENS_ARN" ]; then
    echo "警告: 环境变量 ORR_LENS_ARN 未设置"
    echo "请先运行 WA-Tool 部署脚本并设置环境变量:"
    echo "export ORR_LENS_ARN=arn:aws:wellarchitected:region:account:lens/..."
    echo "将使用默认镜头 ARN"
fi

# 更新系统包
echo "正在更新系统包..."
sudo yum update -y

# 创建并激活虚拟环境
echo "正在创建虚拟环境..."
python -m venv venv
source venv/bin/activate

# 安装项目依赖
echo "正在安装项目依赖..."
pip install -r requirements.txt

# 设置环境变量文件
echo "正在设置环境变量..."
cat > .env << EOL
# Dify API 配置
DIFY_API_KEY=${DIFY_API_KEY}
DIFY_API_BASE_URL=${DIFY_API_BASE_URL}/v1
DIFY_CONSOL_API_BASE_URL=${DIFY_API_BASE_URL}/console/api/apps
DIFY_CONSOL_API_KEY=${DIFY_CONSOL_API_KEY}
# Dify Dataset API Key (用于上传文档)
DIFY_DATASET_API_KEY=${DIFY_DATASET_API_KEY:-${DIFY_API_KEY}}
EOL

# 设置启动脚本
echo "正在创建启动脚本..."
cat > start_app.sh << EOL
#!/bin/bash
source venv/bin/activate
streamlit run 智能ORR审阅工具.py --server.port=8501 --server.address=0.0.0.0
EOL

chmod +x start_app.sh

# 更新工作流文件中的 API URL
echo "正在更新工作流配置文件..."
WORKFLOW_FILE="orr-on-llm-workflow-v5.yml"

# 备份原始文件
cp "$WORKFLOW_FILE" "${WORKFLOW_FILE}.bak"

# 更新 get_lens_info API URL
if [ ! -z "$GET_LENS_INFO_API_URL" ]; then
    echo "更新 get_lens_info API URL 为: $GET_LENS_INFO_API_URL"
    sed -i "s|https://[^/]*/[^/]*/get_lens_info|$GET_LENS_INFO_API_URL|g" "$WORKFLOW_FILE"
fi

# 更新 operate_wa_tool API URL (workload endpoint)
if [ ! -z "$OPERATE_WA_TOOL_API_URL" ]; then
    echo "更新 operate_wa_tool API URL 为: $OPERATE_WA_TOOL_API_URL"
    sed -i "s|https://[^/]*/[^/]*/workload|$OPERATE_WA_TOOL_API_URL|g" "$WORKFLOW_FILE"
    
    # 更新 workload/review endpoint
    REVIEW_URL="${OPERATE_WA_TOOL_API_URL}/review"
    sed -i "s|https://[^/]*/[^/]*/workload/review|$REVIEW_URL|g" "$WORKFLOW_FILE"
fi

# 更新工作流中的镜头 ARN
if [ ! -z "$ORR_LENS_ARN" ]; then
    echo "更新 ORR 镜头 ARN 为: $ORR_LENS_ARN"
    # 这里假设工作流文件中有一个默认的镜头 ARN 需要替换
    # 实际替换模式可能需要根据工作流文件中的实际格式调整
    sed -i "s|arn:aws:wellarchitected:[^:]*:[^:]*:lens/[^\"]*|$ORR_LENS_ARN|g" "$WORKFLOW_FILE"
fi

echo "安装完成！"
echo "运行 './start_app.sh' 启动应用程序"
