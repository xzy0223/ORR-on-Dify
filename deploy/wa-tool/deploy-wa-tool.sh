#!/bin/bash

# 设置变量
REGION="us-west-2"  # 替换为您的 AWS 区域
LENS_FILE="/home/ec2-user/orr-on-dify/deploy/wa-tool/AWS Operational Readiness Review.json"
LENS_VERSION="1.0"

# 检查文件是否存在
if [ ! -f "$LENS_FILE" ]; then
    echo "错误：Custom Lens 文件不存在: $LENS_FILE"
    exit 1
fi

# 直接使用 AWS CLI 导入自定义镜头
echo "正在导入自定义镜头..."
IMPORT_RESULT=$(aws wellarchitected import-lens \
    --json-string file://"$LENS_FILE" \
    --region "$REGION")

# 检查导入是否成功
if [ $? -eq 0 ]; then
    echo "自定义镜头导入成功！"
    echo "$IMPORT_RESULT"
    
    # 提取 LensArn
    LENS_ARN=$(echo "$IMPORT_RESULT" | grep -o '"LensArn": "[^"]*' | cut -d'"' -f4)
    
    echo ""
    echo "===================================================="
    echo "              重要输出信息                           "
    echo "===================================================="
    echo "镜头 ARN: $LENS_ARN"
    echo ""
    echo "请将以下环境变量添加到您的配置中:"
    echo "export ORR_LENS_ARN=\"$LENS_ARN\""
    echo "===================================================="
    
    # 等待几秒钟确保导入完成
    echo "等待导入完成..."
    sleep 5
    
    # 发布镜头
    echo "正在发布镜头版本 $LENS_VERSION..."
    PUBLISH_RESULT=$(aws wellarchitected create-lens-version \
        --lens-alias "$LENS_ARN" \
        --lens-version "$LENS_VERSION" \
        --region "$REGION")
    
    # 检查发布是否成功
    if [ $? -eq 0 ]; then
        echo "镜头发布成功！"
        echo "$PUBLISH_RESULT"
    else
        echo "镜头发布失败。"
        exit 1
    fi
else
    echo "自定义镜头导入失败。"
    exit 1
fi
