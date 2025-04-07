#!/bin/bash

# 部署脚本 - 使用 AWS CLI 部署 CloudFormation 模板

# 设置变量
STACK_NAME="orr-on-dify-lambda-api"
STAGE="dev"
S3_BUCKET="orr-on-dify-lambda-code-$(date +%s)"  # 使用时间戳创建唯一的桶名
REGION="us-west-2"  # 替换为您的 AWS 区域

# 创建 Lambda 函数代码目录（如果不存在）
mkdir -p get_lens_info operate_wa_tool

# 检查 Lambda 函数代码文件是否存在
if [ ! -f "get_lens_info/get_lens_info.py" ] || [ ! -f "operate_wa_tool/operate_wa_tool.py" ]; then
    echo "错误：Lambda 函数代码文件不存在。请确保 get_lens_info/get_lens_info.py 和 operate_wa_tool/operate_wa_tool.py 文件存在。"
    exit 1
fi

# 打包 Lambda 函数代码
echo "打包 Lambda 函数代码..."
zip -j get_lens_info.zip get_lens_info/get_lens_info.py
zip -j operate_wa_tool.zip operate_wa_tool/operate_wa_tool.py

# 检查 S3 存储桶是否存在，如果不存在则创建
echo "检查 S3 存储桶是否存在..."
if ! aws s3 ls "s3://$S3_BUCKET" 2>&1 > /dev/null; then
    echo "创建 S3 存储桶: $S3_BUCKET..."
    aws s3 mb "s3://$S3_BUCKET" --region $REGION
fi

# 上传 Lambda 函数代码到 S3 存储桶
echo "上传 Lambda 函数代码到 S3 存储桶..."
aws s3 cp get_lens_info.zip "s3://$S3_BUCKET/" --region $REGION
aws s3 cp operate_wa_tool.zip "s3://$S3_BUCKET/" --region $REGION

# 检查堆栈是否已存在
echo "检查堆栈是否已存在..."
if aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION 2>&1 > /dev/null; then
    # 更新现有堆栈
    echo "更新现有堆栈: $STACK_NAME..."
    aws cloudformation update-stack \
        --stack-name $STACK_NAME \
        --template-body file://template.yaml \
        --parameters \
            ParameterKey=Stage,ParameterValue=$STAGE \
            ParameterKey=GetLensInfoCodeS3Bucket,ParameterValue=$S3_BUCKET \
            ParameterKey=GetLensInfoCodeS3Key,ParameterValue=get_lens_info.zip \
            ParameterKey=OperateWaToolCodeS3Bucket,ParameterValue=$S3_BUCKET \
            ParameterKey=OperateWaToolCodeS3Key,ParameterValue=operate_wa_tool.zip \
        --capabilities CAPABILITY_IAM \
        --region $REGION

    # 检查更新是否成功
    if [ $? -eq 0 ]; then
        echo "堆栈更新已启动。等待更新完成..."
        aws cloudformation wait stack-update-complete --stack-name $STACK_NAME --region $REGION
        echo "堆栈更新完成。"
    else
        echo "堆栈更新失败或没有更改。"
    fi
else
    # 创建新堆栈
    echo "创建新堆栈: $STACK_NAME..."
    aws cloudformation create-stack \
        --stack-name $STACK_NAME \
        --template-body file://template.yaml \
        --parameters \
            ParameterKey=Stage,ParameterValue=$STAGE \
            ParameterKey=GetLensInfoCodeS3Bucket,ParameterValue=$S3_BUCKET \
            ParameterKey=GetLensInfoCodeS3Key,ParameterValue=get_lens_info.zip \
            ParameterKey=OperateWaToolCodeS3Bucket,ParameterValue=$S3_BUCKET \
            ParameterKey=OperateWaToolCodeS3Key,ParameterValue=operate_wa_tool.zip \
        --capabilities CAPABILITY_IAM \
        --region $REGION

    # 检查创建是否成功
    if [ $? -eq 0 ]; then
        echo "堆栈创建已启动。等待创建完成..."
        aws cloudformation wait stack-create-complete --stack-name $STACK_NAME --region $REGION
        echo "堆栈创建完成。"
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
echo "              重要 API 端点信息                      "
echo "===================================================="

# 获取 API 端点
GET_LENS_INFO_API=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --query "Stacks[0].Outputs[?OutputKey=='GetLensInfoApiEndpoint'].OutputValue" --output text --region $REGION)
OPERATE_WA_TOOL_API=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --query "Stacks[0].Outputs[?OutputKey=='OperateWaToolApiEndpoint'].OutputValue" --output text --region $REGION)

echo "Get Lens Info API 端点: $GET_LENS_INFO_API"
echo "Operate WA Tool API 端点: $OPERATE_WA_TOOL_API"

# 获取 Lambda 函数 ARN
GET_LENS_INFO_FUNCTION=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --query "Stacks[0].Outputs[?OutputKey=='GetLensInfoFunction'].OutputValue" --output text --region $REGION)
OPERATE_WA_TOOL_FUNCTION=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --query "Stacks[0].Outputs[?OutputKey=='OperateWaToolFunction'].OutputValue" --output text --region $REGION)

echo "Get Lens Info Lambda 函数 ARN: $GET_LENS_INFO_FUNCTION"
echo "Operate WA Tool Lambda 函数 ARN: $OPERATE_WA_TOOL_FUNCTION"

echo ""
echo "请将以下环境变量添加到您的配置中:"
echo "export GET_LENS_INFO_API_URL=\"$GET_LENS_INFO_API\""
echo "export OPERATE_WA_TOOL_API_URL=\"$OPERATE_WA_TOOL_API\""
echo "===================================================="

echo "部署完成！"
