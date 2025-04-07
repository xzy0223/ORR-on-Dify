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

### 安装步骤

1. 克隆代码库：

```bash
git clone <repository-url>
cd orr-on-dify
```

2. 部署Dify服务：

```bash
cd deploy/dify
chmod +x deploy-dify.sh
./deploy-dify.sh
```

3. 部署Lambda API：

```bash
cd ../lambda
chmod +x deploy-lambda.sh
./deploy-lambda.sh
```

4. 导入Well-Architected自定义镜头：

```bash
cd ../wa-tool
chmod +x deploy-wa-tool.sh
./deploy-wa-tool.sh
```

5. 在Dify控制台创建API密钥：
   - 访问Dify部署脚本输出的Dify URL
   - 注册并登录Dify控制台
   - 创建一个新应用
   - 在API密钥设置中生成Dataset API Key和Console API Key

6. 设置环境变量：

```bash
# Dify环境变量（从Dify部署脚本输出获取URL）
export DIFY_API_BASE_URL=http://your-dify-url
export DIFY_API_KEY=your-dataset-api-key
export DIFY_CONSOL_API_KEY=your-console-api-key

# Lambda API环境变量（从Lambda部署脚本输出获取URL）
export GET_LENS_INFO_API_URL=https://xxxxx.execute-api.region.amazonaws.com/dev/get_lens_info
export OPERATE_WA_TOOL_API_URL=https://xxxxx.execute-api.region.amazonaws.com/dev/workload

# Well-Architected Tool环境变量（从WA-Tool部署脚本输出获取ARN）
export ORR_LENS_ARN=arn:aws:wellarchitected:region:account:lens/...
```

7. 运行安装脚本：

```bash
cd ../..  # 返回到项目根目录
chmod +x setup.sh
./setup.sh
```

8. 启动应用程序：

```bash
./start_app.sh
```

## 部署流程详解

### 1. Dify部署

Dify是应用程序的知识库和AI引擎。部署脚本会在AWS上创建必要的资源，并输出访问URL。详细说明请参考[Dify部署文档](./deploy/dify/README.md)。

### 2. Lambda API部署

Lambda API提供了与AWS Well-Architected Tool交互的接口。部署脚本会创建两个API：
- `get_lens_info` - 获取Well-Architected镜头信息
- `operate-wa-tool` - 创建和更新工作负载评审

详细说明请参考[Lambda部署文档](./deploy/lambda/README.md)。

### 3. Well-Architected自定义镜头导入

应用程序使用自定义的AWS Operational Readiness Review镜头来评估应用程序。导入脚本会将此镜头导入到您的AWS账户中，并发布为可用版本。导入后，您将获得镜头ARN，用于创建工作负载评审。详细说明请参考[WA-Tool部署文档](./deploy/wa-tool/README.md)。

### 4. 工作流配置更新

安装脚本会自动使用环境变量中的API URL更新工作流配置文件(`orr-on-llm-workflow-v5.yml`)。这确保了应用程序能够正确地与部署的API交互。

## 配置

应用程序启动后，可以通过"设置"页面验证API连接：

1. Dify API配置 - 自动从环境变量配置
2. Lambda API配置 - 自动从工作流配置文件获取

## 使用方法

1. 在"上传文档"页面，将应用程序设计文档上传到知识库
2. 在"审阅应用"页面，选择知识库和ORR模板（使用导入的自定义镜头ARN）
3. 点击"开始审阅"，等待审阅完成
4. 查看生成的审阅报告

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
- `DIFY_API_KEY`: Dify Dataset API密钥
- `DIFY_API_BASE_URL`: Dify API基础URL
- `DIFY_CONSOL_API_BASE_URL`: Dify Console API基础URL（自动从基础URL生成）
- `DIFY_CONSOL_API_KEY`: Dify Console API密钥

### Lambda API配置
- `GET_LENS_INFO_API_URL`: Get Lens Info API的URL
- `OPERATE_WA_TOOL_API_URL`: Operate WA Tool API的URL

### Well-Architected Tool配置
- `ORR_LENS_ARN`: 导入的自定义镜头ARN

这些环境变量会被setup.sh脚本用于配置应用程序和更新工作流文件。
