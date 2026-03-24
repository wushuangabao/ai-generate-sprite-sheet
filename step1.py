# Step1: 生成 Draft 视频
# 创建 Draft 视频任务并轮询任务状态；
# 当任务状态变为 succeeded后，您可在 content.video_url 字段处，下载生成的 Draft 视频文件，检视效果是否符合预期。
# 若不符合预期，可重新调整参数并再次创建 Draft 视频生成任务。当确认 Draft 视频效果符合预期后，即可按照后续步骤生成最终视频。
import os
import time
import base64
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

def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def get_image_url(image_path):
    try:
        base64_image = encode_image(image_path)
        # 获取图片扩展名
        image_ext = image_path.split('.')[-1].lower()
        if image_ext == 'jpg':
            image_ext = 'jpeg'
        return f"data:image/{image_ext};base64,{base64_image}"
    except FileNotFoundError:
        print(f"Error: 找不到本地图片 {image_path}，请确保路径正确。")
        exit(1)

if __name__ == "__main__":
    print("----- create request -----")
    
    # 获取本地图片并转为 Base64 格式
    # 请替换为你实际的本地首尾帧图片路径
    first_frame_path = r"E:\github\seedance\workspace\1.png"
    last_frame_path = r"E:\github\seedance\workspace\2.png"
    
    first_frame_url = get_image_url(first_frame_path)
    last_frame_url = get_image_url(last_frame_path)

    create_result = client.content_generation.tasks.create(
        model="doubao-seedance-1-5-pro-251215", # Replace with Model ID
        content=[
            {
                # Combination of text prompt and parameters
                "type": "text",
                "text": "她驻足原地，衣带飘动。保持她在相机中的位置不动，保持视角不动。背景纯白色"
            },
            {
                # 首帧图片
                "type": "image_url",
                "image_url": {
                    "url": first_frame_url
                },
                "role": "first_frame"
            },
            {
                # 尾帧图片
                "type": "image_url",
                "image_url": {
                    "url": last_frame_url
                },
                "role": "last_frame"
            }
        ],
        seed= 20,
        duration= 6,
        draft= True,
        generate_audio=False,
        watermark=False,
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