import boto3
import json

def lambda_handler(event, context):
    
    print(event)
    # 从事件中获取lens_alias
    
    lens_alias = event['headers']['lens_alias']
    
    if not lens_alias:
        return {
            'statusCode': 400,
            'body': "lens_alias is required"
        }
    
    # 初始化 AWS Well-Architected 客户端
    wa_client = boto3.client('wellarchitected')
    
    try:
        # 获取指定Custom Lens的信息
        response = wa_client.get_lens(LensAlias=lens_alias)
        
        # 提取Lens信息
        lens_info = response['Lens']
        
        # 获取Lens的问题和选项
        lens_content = wa_client.export_lens(
            LensAlias=lens_alias,
            LensVersion=lens_info['LensVersion']
        )
        
        # 解析JSON内容
        lens_json = json.loads(lens_content['LensJSON'])
        
        # 提取问题和选项
        questions = []
        
        for pillar in lens_json['pillars']:
            i = 1
            for question in pillar['questions']:
                question_info = {
                    'Pillar': pillar['name'],
                    'QuestionId': question['id'],
                    'QuestionTitle': question['title'],
                    'Choices': [{'ChoiceId': choice['id'], 'Title': choice['title']} for choice in question['choices']]
                }
                questions.append(question_info)
                # 每个pillar选择3个采样问题，为了避免测试账号bedrock RPM和TPM报错
                i = i + 1
                if i > 3:
                    break
              
        
        print(questions)
        
        # 构造结构化数据
        structured_data = {
            'LensInfo': lens_info,
            'Questions': questions
        }
        
        return {
            'statusCode': 200,
            "headers": {
            "Content-Type": "application/json"
            },
            'body': json.dumps(structured_data)
        }
    
    except wa_client.exceptions.ResourceNotFoundException:
        return {
            'statusCode': 404,
            'body': json.dumps(f"Custom Lens with alias '{lens_alias}' not found.")
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"An error occurred: {str(e)}")
        }