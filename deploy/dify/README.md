# Dify on AWS 部署脚本

这个目录包含了用于在 AWS 上部署 Dify 的脚本和 CloudFormation 模板。

## 文件说明

- `deploy-dify.sh` - 用于部署 Dify CloudFormation 模板的脚本
- `dify.yaml` - Dify 的 CloudFormation 模板

## 使用方法

### 部署 Dify

```bash
./deploy-dify.sh
```

这个脚本会执行以下操作：
1. 检查是否已存在名为 "dify-on-aws" 的 CloudFormation 堆栈
2. 如果堆栈存在，则更新堆栈；如果不存在，则创建新堆栈
3. 等待堆栈创建或更新完成
4. 显示堆栈输出，包括 Dify 服务的访问 URL

### 参数说明

脚本中的默认参数：
- 堆栈名称：`dify-on-aws`
- AWS 区域：`us-west-2`

如果需要修改这些参数，请编辑脚本中的相应变量。

## 部署后配置

部署完成后，脚本会显示 Dify 服务的访问 URL。请按照以下步骤配置环境变量：

1. 记录部署脚本输出的 Dify URL，例如 `http://12.34.56.78:80`

2. 设置环境变量：
```bash
export DIFY_HOST_URL=http://12.34.56.78:80
```

3. 访问 Dify 控制台并创建 API 密钥：
   - 打开浏览器访问 Dify URL
   - 注册并登录 Dify 控制台
   - 创建一个新应用
   - 在 API 密钥设置中生成 API Key
   - 设置环境变量：
   ```bash
   export DIFY_API_KEY=your-api-key
   ```

4. 创建知识库并获取 Dataset API Key：
   - 在 Dify 控制台中，进入知识库页面
   - 在知识库页面，生成 Dataset API Key（重要：上传文档功能需要使用此密钥）
   - 设置环境变量：
   ```bash
   export DIFY_DATASET_API_KEY=your-dataset-api-key
   ```

5. 获取 Console API 密钥：
   - 打开浏览器访问 Dify URL
   - 打开浏览器开发者模式
   - 通过网络请求找到 Console API Key
   ```bash
   export DIFY_CONSOL_API_KEY=your-console-api-key
   ```

6. 配置模型供应商
   - 在Dify控制台中，进入Settings
   - 在Model Provider中选择AWS Bedrock
   - 提前准备好具有Bedrock访问权限IAM User的Access Key和Secret Key
   - 填入必要信息并保存

7. 返回项目根目录并运行安装脚本：
```bash
cd ../..
./setup.sh
```

## 注意事项

- 确保您的 AWS 账户有足够的权限来创建和管理 CloudFormation 堆栈
- 部署过程可能需要几分钟时间
- 如果部署失败，请检查 CloudFormation 事件日志以获取详细错误信息
- Dify 服务启动后可能需要几分钟才能完全初始化
