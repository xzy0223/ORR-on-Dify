# ORR on Dify 部署指南

本目录包含了用于部署 ORR on Dify 应用所需的各种部署脚本和模板。

## 目录结构

- `dify/` - 包含 Dify 服务的部署脚本和 CloudFormation 模板
- `lambda/` - 包含 Lambda API 的部署脚本和 CloudFormation 模板
- `wa-tool/` - 包含 Well-Architected 自定义镜头导入工具

## 部署流程概述

ORR on Dify 应用需要部署三个主要组件：

1. **Dify 服务** - 提供知识库和AI引擎功能
2. **Lambda API** - 提供与AWS Well-Architected Tool交互的接口
3. **Well-Architected 自定义镜头** - 提供ORR评估模板

每个组件都有独立的部署脚本，部署完成后需要配置相应的环境变量。

## 详细部署指南

请参考各组件目录中的详细部署说明：

- [Dify 部署说明](./dify/README.md)
- [Lambda API 部署说明](./lambda/README.md)
- [Well-Architected 自定义镜头导入说明](./wa-tool/README.md)

## 部署后配置

完成所有组件部署后，请返回项目根目录并按照[主README](../README.md)中的说明配置环境变量并启动应用程序。
