# ORR on Dify

这是一个基于Streamlit和Dify的应用程序，用于自动化审阅应用程序设计文档，并生成ORR（Operational Readiness Review）审阅报告。

## 功能特点

- 上传文档到Dify知识库
- 基于AWS Well-Architected Tool的ORR模板审阅应用程序
- 生成详细的审阅报告
- 可配置的Dify API连接和Lambda API端点

## 安装与设置

### 前提条件

- Python 3.8+
- AWS账户（用于部署Dify、Lambda函数和Well-Architected自定义镜头）

### 快速安装指南

1. 克隆代码库并进入项目目录
2. 部署必要的AWS组件（详细说明请参考[部署指南](./deploy/README.md)）：
   - Dify服务 - 提供知识库和AI引擎
   - Lambda API - 与AWS Well-Architected Tool交互
   - Well-Architected自定义镜头 - 提供ORR评估模板
3. 配置API密钥：
   - 在Dify控制台创建应用并生成API Key和Console API Key
   - 在Dify知识库页面创建知识库并生成Dataset API Key
4. 设置环境变量：

```bash
# Dify环境变量
export DIFY_HOST_URL=http://your-dify-host-url
export DIFY_API_KEY=your-api-key
export DIFY_CONSOL_API_KEY=your-console-api-key
export DIFY_DATASET_API_KEY=your-dataset-api-key

# Lambda API环境变量
export GET_LENS_INFO_API_URL=https://xxxxx.execute-api.region.amazonaws.com/dev/get_lens_info
export OPERATE_WA_TOOL_API_URL=https://xxxxx.execute-api.region.amazonaws.com/dev/workload

# Well-Architected Tool环境变量
export ORR_LENS_ARN=arn:aws:wellarchitected:region:account:lens/...
```

5. 运行安装脚本并启动应用：

```bash
chmod +x setup.sh
./setup.sh
./start_app.sh
```

### 详细部署流程

各组件的详细部署说明请参考[部署指南](./deploy/README.md)，其中包含：

- Dify服务部署 - 知识库和AI引擎
- Lambda API部署 - 与AWS Well-Architected Tool交互的接口
- Well-Architected自定义镜头导入 - ORR评估模板

安装脚本会自动配置工作流文件，确保应用程序能够正确地与部署的API交互。

## 配置

应用程序启动后，可以通过"设置"页面验证API连接：

1. Dify API配置 - 自动从环境变量配置
2. Lambda API配置 - 自动从工作流配置文件获取

## 使用方法

1. 在"上传文档"页面，将应用程序设计文档上传到知识库
2. 在"审阅应用"页面，选择知识库和ORR模板（使用导入的自定义镜头ARN）
3. 点击"开始审阅"，等待审阅完成
4. 查看生成的审阅报告，此外也会更新对应WA工具中的工作负载

## 项目结构

```
orr-on-dify/
├── 智能ORR审阅工具.py      # 主应用程序入口
├── pages/                 # Streamlit页面
├── requirements.txt       # Python依赖
├── setup.sh               # 安装脚本
├── start_app.sh           # 启动脚本
├── orr-on-llm-workflow-v5.yml  # Dify工作流配置
└── deploy/                # 部署脚本和模板
    ├── dify/              # Dify部署脚本和模板
    ├── lambda/            # Lambda API部署脚本和模板
    └── wa-tool/           # Well-Architected自定义镜头导入工具
```

## 环境变量

应用程序通过以下环境变量进行配置：

### Dify配置
- `DIFY_HOST_URL`: Dify服务器主机URL（从CloudFormation输出获取）
- `DIFY_API_KEY`: Dify API密钥（从应用API密钥设置获取）
- `DIFY_CONSOL_API_KEY`: Dify Console API密钥（从应用API密钥设置获取）
- `DIFY_DATASET_API_KEY`: Dify Dataset API密钥（从知识库页面获取，用于上传文档）
- `DIFY_API_BASE_URL`: Dify API基础URL（自动从DIFY_HOST_URL生成，添加/v1路径）
- `DIFY_CONSOL_API_BASE_URL`: Dify Console API基础URL（自动从DIFY_HOST_URL生成）

### Lambda API配置
- `GET_LENS_INFO_API_URL`: Get Lens Info API的URL
- `OPERATE_WA_TOOL_API_URL`: Operate WA Tool API的URL

### Well-Architected Tool配置
- `ORR_LENS_ARN`: 导入的自定义镜头ARN

这些环境变量会被setup.sh脚本用于配置应用程序和更新工作流文件。
