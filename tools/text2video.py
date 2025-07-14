import time
import requests
import jwt
from collections.abc import Generator
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


def generate_token(api_key: str, exp_seconds: int = 3600):
    """
    Generates a JWT token for ZhipuAI API authentication.
    """
    try:
        id, secret = api_key.split('.')
    except Exception as e:
        raise ValueError(f"Invalid API Key format: {e}")

    payload = {
        "api_key": id,
        "exp": int(round(time.time() * 1000)) + exp_seconds * 1000,
        "timestamp": int(round(time.time() * 1000)),
    }

    return jwt.encode(
        payload,
        secret,
        algorithm="HS256",
        headers={"alg": "HS256", "sign_type": "SIGN"},
    )


class Text2VideoTool(Tool):
    def _invoke(self, tool_parameters: dict) -> Generator[ToolInvokeMessage, None, None]:
        """
        Invoke text-to-video generation tool using BigModel CogVideoX.
        """
        api_key = self.runtime.credentials.get("api_key")
        if not api_key:
            yield self.create_text_message("API 密钥未设置。")
            return

        try:
            token = generate_token(api_key)
        except ValueError as e:
            yield self.create_text_message(f"API 密钥错误: {e}")
            return

        base_url = "https://open.bigmodel.cn/api/paas/v4"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        prompt = tool_parameters.get("prompt", "")
        if not prompt:
            yield self.create_text_message("提示词是必需的。")
            return

        payload = {
            "model": tool_parameters.get("model") or "CogVideoX-Flash",
            "prompt": prompt,
            "quality": tool_parameters.get("quality"),
            "with_audio": tool_parameters.get("with_audio"),
            "size": tool_parameters.get("size"),
            "fps": tool_parameters.get("fps"),
        }
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}

        try:
            # 1. Create generation task
            yield self.create_text_message("正在创建视频生成任务...")
            response = requests.post(f"{base_url}/videos/generations", headers=headers, json=payload)
            print("Status code:", response.status_code)
            print("Raw response:", response.text)
            try:
                response.raise_for_status()
                task_id = response.json().get("id")
            except Exception as e:
                yield self.create_text_message(f"创建任务失败: {response.text}")
                return
            
            yield self.create_text_message(f"任务已创建，ID: {task_id}。正在等待完成...")

            # 2. Poll for task result
            max_retries = 60
            for i in range(max_retries):
                time.sleep(5)
                task_response = requests.get(f"{base_url}/async-result/{task_id}", headers=headers)
                task_response.raise_for_status()
                task_data = task_response.json()

                status = task_data.get("task_status")
                if status == "SUCCESS":
                    video_result = task_data.get("video_result")
                    if video_result and isinstance(video_result, list) and video_result[0].get("url"):
                        video_url = video_result[0]["url"]
                        yield self.create_text_message("视频生成成功！")
                        yield self.create_link_message(video_url)
                    else:
                        yield self.create_text_message("任务成功，但未找到视频 URL。")
                    return
                elif status == "FAIL":
                    error_msg = task_data.get("error", "Unknown error")
                    yield self.create_text_message(f"视频生成失败: {error_msg}")
                    return
                
                yield self.create_text_message(f"已等待 {(i + 1) * 5} 秒...")

            yield self.create_text_message("视频生成超时。")

        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"发生错误: {e}")
        except Exception as e:
            yield self.create_text_message(f"发生意外错误: {e}")