# ORR on Dify 部署指南

本目录包含了用于部署 ORR on Dify 应用所需的各种部署脚本和模板。

## 目录结构

- `dify/` - 包含 Dify 服务的部署脚本和 CloudFormation 模板
- `lambda/` - 包含 Lambda API 的部署脚本和 CloudFormation 模板
- `wa-tool/` - 包含 Well-Architected 自定义镜头导入工具

## 部署流程

完整的部署流程如下：

1. 部署 Dify 服务：
```bash
cd dify
chmod +x deploy-dify.sh
./deploy-dify.sh
```

2. 部署 Lambda API：
```bash
cd ../lambda
chmod +x deploy-lambda.sh
./deploy-lambda.sh
```

3. 导入 Well-Architected 自定义镜头：
```bash
cd ../wa-tool
chmod +x deploy-wa-tool.sh
./deploy-wa-tool.sh
```

4. 配置环境变量：
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

5. 返回项目根目录并运行安装脚本：
```bash
cd ../..
chmod +x setup.sh
./setup.sh
```

6. 启动应用程序：
```bash
./start_app.sh
```

## 详细说明

每个部署组件的详细说明请参考各子目录中的 README.md 文件：

- [Dify 部署说明](./dify/README.md)
- [Lambda API 部署说明](./lambda/README.md)
- [Well-Architected 自定义镜头导入说明](./wa-tool/README.md)
