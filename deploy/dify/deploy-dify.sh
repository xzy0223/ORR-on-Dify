#!/bin/bash

# 设置变量
STACK_NAME="dify-on-aws"
REGION="us-west-2"  # 可以根据需要修改区域
TEMPLATE_FILE="$(dirname "$0")/dify.yaml"

# 检查模板文件是否存在
if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "错误：CloudFormation 模板文件不存在: $TEMPLATE_FILE"
    exit 1
fi

# 检查堆栈是否已存在
echo "检查堆栈是否已存在..."
if aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION 2>&1 > /dev/null; then
    # 更新现有堆栈
    echo "更新现有堆栈: $STACK_NAME..."
    aws cloudformation update-stack \
        --stack-name $STACK_NAME \
        --template-body file://$TEMPLATE_FILE \
        --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND \
        --region $REGION

    # 检查更新是否成功启动
    if [ $? -eq 0 ]; then
        echo "堆栈更新已启动。等待更新完成..."
        aws cloudformation wait stack-update-complete --stack-name $STACK_NAME --region $REGION
        
        if [ $? -eq 0 ]; then
            echo "堆栈更新完成。"
        else
            echo "堆栈更新失败或超时。"
            exit 1
        fi
    else
        echo "堆栈更新失败或没有更改。"
    fi
else
    # 创建新堆栈
    echo "创建新堆栈: $STACK_NAME..."
    aws cloudformation create-stack \
        --stack-name $STACK_NAME \
        --template-body file://$TEMPLATE_FILE \
        --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND \
        --region $REGION

    # 检查创建是否成功
    if [ $? -eq 0 ]; then
        echo "堆栈创建已启动。等待创建完成..."
        aws cloudformation wait stack-create-complete --stack-name $STACK_NAME --region $REGION
        
        if [ $? -eq 0 ]; then
            echo "堆栈创建完成。"
        else
            echo "堆栈创建失败或超时。"
            exit 1
        fi
    else
        echo "堆栈创建失败。"
        exit 1
    fi
fi

# 获取并显示堆栈输出
echo ""
echo "===================================================="
echo "              CloudFormation 堆栈输出                "
echo "===================================================="
aws cloudformation describe-stacks --stack-name $STACK_NAME --query "Stacks[0].Outputs" --output table --region $REGION

# 提取并单独显示重要输出
echo ""
echo "===================================================="
echo "              重要输出信息                           "
echo "===================================================="
HOST_URL=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --query "Stacks[0].Outputs[?OutputKey=='Host'].OutputValue" --output text --region $REGION)
echo "Dify 访问地址: $HOST_URL"

# 获取其他可能的重要输出
INSTANCE_ID=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --query "Stacks[0].Outputs[?contains(OutputKey,'Instance')].OutputValue" --output text --region $REGION)
if [ ! -z "$INSTANCE_ID" ]; then
    echo "实例 ID: $INSTANCE_ID"
fi

echo ""
echo "部署完成！您可以通过上面的地址访问 Dify 服务。"
echo "默认用户名和密码请参考 Dify 文档。"
echo "===================================================="
