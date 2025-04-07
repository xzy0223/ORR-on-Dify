# Lambda and API Gateway Deployment

这个目录包含用于部署 Lambda 函数和 API Gateway 的 CloudFormation 模板，用于 orr-on-dify 项目。

## 模板概述

`template.yaml` 文件定义了以下资源：

1. **Lambda 函数**:
   - `get_lens_info` - 从 AWS Well-Architected Tool 获取镜头信息
   - `operate_wa_tool` - 创建工作负载和更新工作负载评审

2. **API Gateway APIs**:
   - `get_lens_info-API` - 用于获取镜头信息的 API
   - `operate-wa-tool-API` - 用于创建工作负载和更新工作负载评审的 API

## API 端点

### get_lens_info API
- **端点**: `/get_lens_info` (GET)
- **必需的请求头**: `lens_alias`
- **描述**: 从 AWS Well-Architected Tool 获取特定镜头的信息

### operate-wa-tool API
- **端点**: `/workload` (POST)
  - **描述**: 创建新的工作负载
  - **请求体**: 具有以下属性的 JSON 对象:
    - `workloadName` (必需): 工作负载的名称
    - `description`: 工作负载的描述
    - `environment` (必需): 工作负载的环境 (PRODUCTION, PREPRODUCTION, 或 DEVELOPMENT)
    - `lenses` (必需): 应用于工作负载的镜头 ARN 数组
    - `reviewOwner` (必需): 工作负载评审的所有者

- **端点**: `/workload/review` (PUT)
  - **描述**: 更新工作负载评审
  - **请求体**: 具有以下属性的 JSON 对象:
    - `workloadId` (必需): 工作负载的唯一标识符
    - `lensAlias` (必需): 镜头的 ARN
    - `questionId` (必需): 正在回答的问题的标识符
    - `choiceUpdates` (必需): 包含以下内容的对象:
      - `selectedChoices` (必需): 选定的选项标识符数组
      - `notes`: 答案的附加说明

## 使用部署脚本

为了简化部署过程，我们提供了一个自动化部署脚本 `deploy-lambda.sh`。该脚本会自动执行以下操作：

1. 打包 Lambda 函数代码
2. 创建唯一的 S3 存储桶
3. 上传 Lambda 函数代码到 S3 存储桶
4. 部署或更新 CloudFormation 堆栈
5. 显示部署输出和 API 端点信息

使用方法：

```bash
# 确保脚本有执行权限
chmod +x deploy-lambda.sh

# 运行部署脚本
./deploy-lambda.sh
```

部署完成后，脚本将显示所有 CloudFormation 输出，包括 API 端点和 Lambda 函数 ARN。您可以使用这些输出来配置应用程序。

### 环境变量设置

部署脚本会输出可以直接复制使用的环境变量设置命令：

```bash
export GET_LENS_INFO_API_URL="https://xxxxx.execute-api.us-west-2.amazonaws.com/dev/get_lens_info"
export OPERATE_WA_TOOL_API_URL="https://xxxxx.execute-api.us-west-2.amazonaws.com/dev/workload"
```

您可以将这些环境变量添加到您的应用程序配置中。

## 参数

- `Stage`: 部署阶段 (dev, test, prod)。默认为 'dev'。
- `GetLensInfoCodeS3Bucket`: 包含 get_lens_info Lambda 函数代码的 S3 存储桶
- `GetLensInfoCodeS3Key`: get_lens_info Lambda 函数代码的 S3 键
- `OperateWaToolCodeS3Bucket`: 包含 operate_wa_tool Lambda 函数代码的 S3 存储桶
- `OperateWaToolCodeS3Key`: operate_wa_tool Lambda 函数代码的 S3 键

## 输出

- `GetLensInfoApiEndpoint`: get_lens_info API 的 URL
- `OperateWaToolApiEndpoint`: operate-wa-tool API 的 URL
- `GetLensInfoFunction`: get_lens_info Lambda 函数的 ARN
- `OperateWaToolFunction`: operate-wa-tool Lambda 函数的 ARN
