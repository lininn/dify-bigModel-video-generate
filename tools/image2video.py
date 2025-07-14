import os
import time
import requests
import jwt
import base64
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


class Image2VideoTool(Tool):
    def _get_image_mime_type(self, image_bytes: bytes) -> str:
        if image_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
            return 'image/png'
        elif image_bytes.startswith(b'\xff\xd8'):
            return 'image/jpeg'
        return 'image/jpeg'

    def _encode_image(self, image_bytes: bytes) -> str:
        return base64.b64encode(image_bytes).decode("utf-8")

    def _invoke(self, tool_parameters: dict) -> Generator[ToolInvokeMessage, None, None]:
        """
        Invoke image-to-video generation tool using BigModel CogVideoX.
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

        image_file = tool_parameters.get("image")
        if not image_file:
            yield self.create_text_message("图片文件是必需的。")
            return

        try:
            image_bytes = None
            # Handle image from URL
            if hasattr(image_file, 'url') and image_file.url:
                file_url = image_file.url
                yield self.create_text_message(f"图片下载中: {file_url}")
                try:
                    # Get Dify base URL from environment variable, with a fallback.
                    # You should set DIFY_API_URL in your environment for production.
                    dify_base_url = os.environ.get('DIFY_API_URL', 'http://dify.d-1.top').rstrip('/')
                    full_url = f"{dify_base_url}/{file_url.lstrip('/')}"
                    response = requests.get(full_url, timeout=60)
                    response.raise_for_status()
                    image_bytes = response.content
                    yield self.create_text_message(f"图片下载完毕，大小: {len(image_bytes) / 1024:.2f} KB")
                except Exception as e:
                    yield self.create_text_message(f"图片下载失败: {e}")
                    # Fallback to blob below

            # Handle image from blob if URL download fails or no URL is provided
            if image_bytes is None and hasattr(image_file, 'blob'):
                image_bytes = image_file.blob

            if not image_bytes:
                yield self.create_text_message("无法读取图片文件。")
                return

            mime_type = self._get_image_mime_type(image_bytes)
            encoded_image = self._encode_image(image_bytes)
            image_url = f"data:{mime_type};base64,{encoded_image}"

            # 1. Create generation task
            payload = {
                "model": tool_parameters.get("model") or "CogVideoX-Flash",
                "image_url": image_url,
                "prompt": tool_parameters.get("prompt"),
                "quality": tool_parameters.get("quality"),
                "with_audio": tool_parameters.get("with_audio"),
                "size": tool_parameters.get("size"),
                "fps": tool_parameters.get("fps"),
            }
            payload = {k: v for k, v in payload.items() if v is not None}

            yield self.create_text_message("正在创建视频生成任务...")
            response = requests.post(f"{base_url}/videos/generations", headers=headers, json=payload)
            response.raise_for_status()
            task_id = response.json().get("id")
            if not task_id:
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
                        yield self.create_text_message("视频生成成功!")
                        yield self.create_link_message(video_url)
                    else:
                        yield self.create_text_message("任务成功，但未找到视频 URL。")
                    return
                elif status == "FAIL":
                    error_msg = task_data.get("error", "Unknown error")
                    yield self.create_text_message(f"视频生成失败: {error_msg}")
                    return
                
                yield self.create_text_message(f"已经等待 {(i + 1) * 5} 秒...")

            yield self.create_text_message("视频生成超时。")

        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"发生错误: {e}")
        except Exception as e:
            yield self.create_text_message(f"发生意外错误: {e}")
