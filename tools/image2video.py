import os
import time
import requests
import jwt
import base64
import logging
from collections.abc import Generator
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

# 配置日志
logger = logging.getLogger(__name__)


def generate_token(api_key: str, exp_seconds: int = 3600):
    """
    Generates a JWT token for ZhipuAI API authentication.
    """
    logger.info(f"开始生成JWT token，有效期: {exp_seconds}秒")
    try:
        id, secret = api_key.split('.')
        logger.info(f"API Key解析成功，ID: {id[:8]}***")
    except Exception as e:
        logger.error(f"API Key格式错误: {e}")
        raise ValueError(f"Invalid API Key format: {e}")

    payload = {
        "api_key": id,
        "exp": int(round(time.time() * 1000)) + exp_seconds * 1000,
        "timestamp": int(round(time.time() * 1000)),
    }

    token = jwt.encode(
        payload,
        secret,
        algorithm="HS256",
        headers={"alg": "HS256", "sign_type": "SIGN"},
    )
    logger.info("JWT token生成成功")
    return token


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
        logger.info(f"开始图生视频任务，参数: {tool_parameters}")
        
        api_key = self.runtime.credentials.get("api_key")
        if not api_key:
            error_msg = "API 密钥未设置。"
            logger.error(error_msg)
            yield self.create_text_message(error_msg)
            return

        try:
            token = generate_token(api_key)
        except ValueError as e:
            error_msg = f"API 密钥错误: {e}"
            logger.error(error_msg)
            yield self.create_text_message(error_msg)
            return

        base_url = "https://open.bigmodel.cn/api/paas/v4"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        logger.info(f"设置请求头和基础URL: {base_url}")

        image_file = tool_parameters.get("image")
        if not image_file:
            error_msg = "图片文件是必需的。"
            logger.error(error_msg)
            yield self.create_text_message(error_msg)
            return

        try:
            image_bytes = None
            # Handle image from URL
            if hasattr(image_file, 'url') and image_file.url:
                file_url = image_file.url
                logger.info(f"开始下载图片: {file_url}")
                yield self.create_text_message(f"图片下载中: {file_url}")
                try:
                    # Get Dify base URL from environment variable, with a fallback.
                    # You should set DIFY_API_URL in your environment for production.
                    dify_base_url = os.environ.get('DIFY_API_URL', 'http://dify.d-1.top').rstrip('/')
                    full_url = f"{dify_base_url}/{file_url.lstrip('/')}"
                    logger.info(f"完整下载地址: {full_url}")
                    
                    response = requests.get(full_url, timeout=60)
                    response.raise_for_status()
                    image_bytes = response.content
                    success_msg = f"图片下载完毕，大小: {len(image_bytes) / 1024:.2f} KB"
                    logger.info(success_msg)
                    yield self.create_text_message(success_msg)
                except Exception as e:
                    error_msg = f"图片下载失败: {e}"
                    logger.warning(error_msg)
                    yield self.create_text_message(error_msg)
                    # Fallback to blob below

            # Handle image from blob if URL download fails or no URL is provided
            if image_bytes is None and hasattr(image_file, 'blob'):
                logger.info("使用blob数据读取图片")
                image_bytes = image_file.blob

            if not image_bytes:
                error_msg = "无法读取图片文件。"
                logger.error(error_msg)
                yield self.create_text_message(error_msg)
                return

            mime_type = self._get_image_mime_type(image_bytes)
            encoded_image = self._encode_image(image_bytes)
            image_url = f"data:{mime_type};base64,{encoded_image}"
            logger.info(f"图片编码完成，类型: {mime_type}, Base64长度: {len(encoded_image)}")

            # 1. Create generation task
            payload = {
                "model": tool_parameters.get("model") or "cogvideox-flash",
                "image_url": image_url,
                "prompt": tool_parameters.get("prompt"),
                "quality": tool_parameters.get("quality"),
                "with_audio": tool_parameters.get("with_audio"),
                "size": tool_parameters.get("size"),
                "fps": tool_parameters.get("fps"),
                "duration": tool_parameters.get("duration"),
            }
            payload = {k: v for k, v in payload.items() if v is not None}
            logger.info(f"请求载荷: {payload}")

            session = requests.Session()
            session.headers.update(headers)

            yield self.create_text_message("正在创建视频生成任务...")
            logger.info("开始创建图生视频任务")
            
            response = session.post(
                f"{base_url}/videos/generations",
                json=payload,
                timeout=30  # 设置30秒超时
            )
            
            logger.info(f"HTTP响应状态码: {response.status_code}")
            logger.debug(f"原始响应内容: {response.text}")
            print("Status code:", response.status_code)
            print("Raw response:", response.text)
            try:
                response.raise_for_status()
                task_data = response.json()
                task_id = task_data.get("id")
                if not task_id:
                    error_msg = f"创建任务失败: 未返回任务ID - {response.text}"
                    logger.error(error_msg)
                    yield self.create_text_message(error_msg)
                    return
                logger.info(f"任务创建成功，任务ID: {task_id}")
            except requests.exceptions.HTTPError as e:
                error_msg = f"HTTP错误 {response.status_code}: {response.text}"
                logger.error(error_msg)
                yield self.create_text_message(error_msg)
                return
            except Exception as e:
                error_msg = f"创建任务失败: {e} - {response.text}"
                logger.error(error_msg)
                yield self.create_text_message(error_msg)
                return
            
            yield self.create_text_message(f"任务已创建，ID: {task_id}。正在等待完成...")

            # 2. Poll for task result with improved error handling
            max_retries = 60
            consecutive_failures = 0  # 连续失败计数器
            max_consecutive_failures = 5  # 最大连续失败次数
            
            logger.info(f"开始轮询任务状态，最大重试次数: {max_retries}")
            
            for i in range(max_retries):
                time.sleep(5)
                logger.debug(f"轮询第 {i+1} 次，查询任务 {task_id} 状态")
                
                try:
                    task_response = session.get(
                        f"{base_url}/async-result/{task_id}",
                        timeout=30  # 设置30秒超时
                    )
                    
                    if task_response.status_code != 200:
                        consecutive_failures += 1
                        error_msg = f"查询任务状态失败，HTTP {task_response.status_code}: {task_response.text}"
                        logger.warning(error_msg)
                        yield self.create_text_message(error_msg)
                        
                        if consecutive_failures >= max_consecutive_failures:
                            final_error = f"连续 {consecutive_failures} 次查询失败，任务终止"
                            logger.error(final_error)
                            yield self.create_text_message(final_error)
                            return
                        continue
                    
                    # 重置连续失败计数器
                    consecutive_failures = 0
                
                    try:
                        task_data = task_response.json()
                        logger.debug(f"任务响应数据: {task_data}")
                    except Exception as e:
                        consecutive_failures += 1
                        error_msg = f"解析响应失败: {e}"
                        logger.warning(error_msg)
                        yield self.create_text_message(error_msg)
                        
                        if consecutive_failures >= max_consecutive_failures:
                            final_error = f"连续 {consecutive_failures} 次解析失败，任务终止"
                            logger.error(final_error)
                            yield self.create_text_message(final_error)
                            return
                        continue

                    status = task_data.get("task_status")
                    logger.info(f"任务状态: {status}")
                    
                    if status == "SUCCESS":
                        video_result = task_data.get("video_result")
                        if video_result and isinstance(video_result, list) and len(video_result) > 0 and video_result[0].get("url"):
                            video_url = video_result[0]["url"]
                            success_msg = "视频生成成功!"
                            logger.info(f"{success_msg} URL: {video_url}")
                            yield self.create_text_message(success_msg)
                            yield self.create_text_message(video_url)
                        else:
                            error_msg = f"任务成功，但未找到视频 URL。响应内容: {task_data}"
                            logger.error(error_msg)
                            yield self.create_text_message(error_msg)
                        return
                    elif status == "FAIL" or status == "FAILED":
                        error_msg = task_data.get("error", task_data.get("error_message", "Unknown error"))
                        final_error = f"视频生成失败: {error_msg}"
                        logger.error(final_error)
                        yield self.create_text_message(final_error)
                        return
                    elif status in ["PROCESSING", "PENDING", "RUNNING"]:
                        # Continue polling
                        logger.debug(f"任务仍在处理中: {status}")
                        pass
                    else:
                        warning_msg = f"未知任务状态: {status}"
                        logger.warning(warning_msg)
                        yield self.create_text_message(warning_msg)
                    
                    progress_msg = f"已经等待 {(i + 1) * 5} 秒..."
                    yield self.create_text_message(progress_msg)
                
                except requests.exceptions.Timeout:
                    consecutive_failures += 1
                    timeout_msg = f"请求超时，连续失败次数: {consecutive_failures}"
                    logger.warning(timeout_msg)
                    yield self.create_text_message(timeout_msg)
                    
                    if consecutive_failures >= max_consecutive_failures:
                        final_error = f"连续 {consecutive_failures} 次请求超时，任务终止"
                        logger.error(final_error)
                        yield self.create_text_message(final_error)
                        return
                    continue
                except requests.exceptions.RequestException as e:
                    consecutive_failures += 1
                    network_error = f"网络请求错误: {e}"
                    logger.warning(network_error)
                    yield self.create_text_message(network_error)
                    
                    if consecutive_failures >= max_consecutive_failures:
                        final_error = f"连续 {consecutive_failures} 次网络错误，任务终止"
                        logger.error(final_error)
                        yield self.create_text_message(final_error)
                        return
                    continue

            timeout_msg = "视频生成超时。"
            logger.error(f"5分钟轮询超时: {timeout_msg}")
            yield self.create_text_message(timeout_msg)

        except requests.exceptions.RequestException as e:
            error_msg = f"网络请求错误: {e}"
            logger.error(error_msg)
            yield self.create_text_message(error_msg)
        except Exception as e:
            error_msg = f"发生意外错误: {e}"
            logger.error(error_msg)
            yield self.create_text_message(error_msg)
            import traceback
            full_error = f"完整错误信息: {traceback.format_exc()}"
            logger.error(full_error)
            print(full_error)
