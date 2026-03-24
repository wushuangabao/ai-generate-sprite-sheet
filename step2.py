# Step2: 基于 Draft 视频生成正式视频
# 如果确认 Draft 视频符合预期，可基于 Step1 返回的 Draft 视频任务 ID，再次调用POST /contents/generations/tasks接口，生成最终视频。
# 说明
# 平台将自动复用 Draft 视频使用的用户输入（ model、content.text、content.image_url、generate_audio、seed、ratio、duration、camera_fixed ），生成正式视频。
# 其余参数支持指定，不指定将使用本模型的默认值。例如：指定正式视频的分辨率、是否包含水印、是否使用离线推理、是否返回尾帧等。
# 基于 Draft 视频生成最终视频属于正常推理过程，按照正常视频消耗 token 量计费。
# Draft 视频任务 ID 的有效期为 7 天（从 created at 时间戳开始计算），超时后将无法使用该 Draft 视频生成正式视频。
import os
import time
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# Install SDK:  pip install 'volcengine-python-sdk[ark]'
from volcenginesdkarkruntime import Ark 

# Make sure that you have stored the API Key in the environment variable ARK_API_KEY
# Initialize the Ark client to read your API Key from an environment variable
client = Ark(
    # This is the default path. You can configure it based on the service location
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    # Get API Key：https://console.volcengine.com/ark/region:ark+cn-beijing/apikey
    api_key=os.environ.get("ARK_API_KEY"),
)

if __name__ == "__main__":
    print("----- create request -----")
    create_result = client.content_generation.tasks.create(
        model="doubao-seedance-1-5-pro-251215", # Replace with Model ID
        content=[
            {
                "type": "draft_task",
                "draft_task": {
                    "id": "cgt-2026****-pzjqb"
                }
            }
        ],
        watermark= False,
        resolution= "720p",
        return_last_frame= True,
        service_tier= "default",
    )
    print(create_result)
    
    # Polling query section
    print("----- polling task status -----")
    task_id = create_result.id
    while True:
        get_result = client.content_generation.tasks.get(task_id=task_id)
        status = get_result.status
        if status == "succeeded":
            print("----- task succeeded -----")
            print(get_result)
            break
        elif status == "failed":
            print("----- task failed -----")
            print(f"Error: {get_result.error}")
            break
        else:
            print(f"Current status: {status}, Retrying after 10 seconds...")
            time.sleep(10)