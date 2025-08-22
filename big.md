CogVideoX
CogVideoX 是由智谱AI开发的视频生成大模型，具备强大的视频生成能力，只需输入文本或图片就可以轻松完成视频制作。

模型编码：cogvideox-2、cogvideox-flash；
了解cogvideox系列模型差异，选择最适合你的的大模型；
查看 产品价格 ；
在 体验中心 体验模型能力；
查看模型 速率限制；
查看您的 API Key；
视频生成任务
接口请求
类型	说明
传输方式	https
请求地址	https://open.bigmodel.cn/api/paas/v4/videos/generations
调用方式	异步调用，需通过查询接口获取结果
字符编码	UTF-8
接口请求格式	JSON
响应格式	JSON
接口请求类型	POST
开发语言	任意可发起 http 请求的开发语言
请求参数
参数名称	类型	是否必填	参数说明
model	String	是	模型编码
duration	int	否	视频持续时长，默认5秒，支持5、10
prompt	String	可选	视频的文本描述，最大输入长度为 512 Tokens, image_url和prompt二选一或者同时传入。
quality	String	否	输出模式，默认为 "speed"。 "quality"：质量优先，生成质量高。 "speed"：速度优先，生成时间更快，质量相对降低。
with_audio	Bool	否	是否生成 AI 音效。默认值: False（不生成音效）。
image_url	String	可选	提供基于其生成内容的图像。如果传入此参数，系统将以该图像为基础进行操作。支持通过URL或Base64编码传入图片。图片要求如下：图片支持.png、jpeg、.jpg 格式、图片大小：不超过5M。image_url和prompt二选一或者同时传入。
size	String	否	默认值: 若不指定，默认生成视频的短边为 1080，长边根据原图片比例缩放。最高支持 4K 分辨率。分辨率选项：720x480、1024x1024、1280x960、960x1280、1920x1080、1080x1920、2048x1080、3840x2160
fps	int	否	视频帧率（FPS），可选值为 30 或 60。默认值: 30。
request_id	String	否	由用户端传参，需保证唯一性；用于区分每次请求的唯一标识，用户端不传时平台会默认生成。
user_id	String	否	终端用户的唯一ID，协助平台对终端用户的违规行为、生成违法及不良信息或其他滥用行为进行干预。ID长度要求：最少6个字符，最多128个字符。 了解更多
说明：cogvideox-flash：不支持quality 、size 、fps 参数设置

响应参数
参数名称	类型	参数说明
request_id	String	用户在客户端请求时提交的任务编号或者平台生成的任务编号
id	String	智谱 AI 开放平台生成的任务订单号，调用请求结果接口时请使用此订单号
model	String	本次调用的模型名称
task_status	string	处理状态，PROCESSING（处理中），SUCCESS（成功），FAIL（失败）。需通过查询获取结果
调用示例
文生视频

from zhipuai import ZhipuAI
client = ZhipuAI(api_key="") # 请填写您自己的APIKey

response = client.videos.generations(
    model="cogvideox-2",
    prompt="比得兔开小汽车，游走在马路上，脸上的表情充满开心喜悦。",
    quality="quality",  # 输出模式，"quality"为质量优先，"speed"为速度优先
    with_audio=True,
    size="1920x1080",  # 视频分辨率，支持最高4K（如: "3840x2160"）
    fps=30,  # 帧率，可选为30或60
)
print(response)
图生视频

from zhipuai import ZhipuAI

# 初始化客户端，请填写您自己的APIKey
client = ZhipuAI(api_key="YOUR_API_KEY")

# 定义图片的URL地址
image_url = "https://example.com/path/to/your/image.jpg"  # 替换为您的图片URL地址

# 调用视频生成接口
response = client.videos.generations(
    model="cogvideox-2",  # 使用的视频生成模型
    image_url=image_url,  # 提供的图片URL地址或者 Base64 编码
    prompt="让画面动起来",  
    quality="quality",  # 输出模式，"quality"为质量优先，"speed"为速度优先
    with_audio=True,
    size="1920x1080",  # 视频分辨率，支持最高4K（如: "3840x2160"）
    fps=30,  # 帧率，可选为30或60
)

# 打印返回结果
print(response)

响应示例
id='8868902201637896192' request_id='654321' model='cogvideox-2' task_status='PROCESSING'
任务结果查询
接口请求
传输方式	https
请求地址	https://open.bigmodel.cn/api/paas/v4/async-result/{id}
调用方式	同步调用，等待模型执行完成并返回最终结果
字符编码	UTF-8
接口请求格式	JSON
响应格式	JSON
接口请求类型	GET
开发语言	任意可发起 http 请求的开发语言
请求参数
参数名称	类型	是否必填	参数说明
id	String	是	任务 id
响应参数
参数名称	类型	参数说明
model	String	模型名称
video_result	List	视频生成结果
 url	String	视频url
 cover_image_url	String	视频封面url
task_status	String	处理状态，PROCESSING（处理中），SUCCESS（成功），FAIL（失败） 注：处理中状态需通过查询获取结果
request_id	String	用户在客户端请求时提交的任务编号或者平台生成的任务编号
调用示例
请求示例
from zhipuai import ZhipuAI
client = ZhipuAI(api_key="") # 请填写您自己的APIKey

response = client.videos.retrieve_videos_result(
    id="8868902201637896192"
)
print(response)
响应示例
{
    "model": "cogvideox-2",
    "request_id": "8868902201637896192",
    "task_status": "SUCCESS",
    "video_result": [
        {
            "cover_image_url": "https://sfile.chatglm.cn/testpath/video_cover/4d3c5aad-8c94-5549-93b7-97af6bd353c6_cover_0.png",
            "url": "https://sfile.chatglm.cn/testpath/video/4d3c5aad-8c94-5549-93b7-97af6bd353c6_0.mp4"
        }
    ]
}





