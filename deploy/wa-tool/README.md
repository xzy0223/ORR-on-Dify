# AWS Well-Architected Tool 自定义镜头导入工具

这个目录包含了用于导入和发布 AWS Operational Readiness Review 自定义镜头到 AWS Well-Architected Tool 的脚本和文件。

## 文件说明

- `AWS Operational Readiness Review.json` - 自定义镜头的 JSON 定义文件
- `deploy-wa-tool.sh` - 用于导入和发布自定义镜头的脚本

## 使用方法

### 导入和发布自定义镜头

```bash
chmod +x deploy-wa-tool.sh
./deploy-wa-tool.sh
```

这个脚本会执行以下操作：
1. 导入自定义镜头到 AWS Well-Architected Tool
2. 获取新镜头的 ARN
3. 发布镜头，版本为 1.0

### 脚本输出

脚本成功执行后，会显示以下重要信息：

```
====================================================
              重要输出信息                           
====================================================
镜头 ARN: arn:aws:wellarchitected:region:account:lens/...

请将以下环境变量添加到您的配置中:
export ORR_LENS_ARN="arn:aws:wellarchitected:region:account:lens/..."
====================================================
```

请记录输出的镜头 ARN，您将在应用程序中使用它来创建工作负载评审。

### 使用自定义镜头

导入和发布成功后，您可以在 AWS Well-Architected Tool 中使用这个自定义镜头：

1. 登录 AWS 管理控制台
2. 导航到 AWS Well-Architected Tool
3. 创建新的工作负载或选择现有工作负载
4. 在"应用镜头"部分，选择 "AWS Operational Readiness Review" 自定义镜头
5. 应用该镜头后，开始回答镜头中的问题，评估您的工作负载是否符合 AWS 运营就绪审查的最佳实践

## 自定义镜头说明

AWS Operational Readiness Review 自定义镜头是 AWS 运营就绪审查程序的适配版本，包含一系列问题，旨在捕获和帮助纠正常见的故障点。这个镜头可以帮助您确保工作负载在投入生产前已经做好了充分的运营准备。
