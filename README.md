# 智谱 AI 视频生成插件 (dify-big-model-video-generate)

[![Author](https://img.shields.io/badge/Author-lininn-blue.svg)](https://github.com/lininn)
[![Version](https://img.shields.io/badge/Version-0.0.1-brightgreen.svg)](https://github.com/lininn/dify-bigModel-video-generate)
[![Dify](https://img.shields.io/badge/Powered%20by-Dify-blue.svg)](https://dify.ai/)

一个为 [Dify](https://dify.ai/) 平台开发的插件，用于调用智谱 AI (BigModel) 的 [CogVideoX API](https://bigmodel.cn/dev/api#cogvideox) 来生成视频。

## ✨ 功能特性

*   **文生视频**: 根据文本描述生成视频。
*   **图生视频**: 根据输入的图片和可选的文本描述生成视频。

## 🚀 安装与配置

### 1. 环境要求

*   Python 3.12+
*   一个正在运行的 Dify 实例

### 2. 安装依赖

克隆本仓库后，在项目根目录下执行以下命令安装所需的依赖：

```bash
pip install -r requirements.txt
```

### 3. 配置 API Key

1.  前往 [智谱 AI 开放平台](https://bigmodel.cn/dev/api) 获取您的 API Key。
2.  在 Dify 平台的 `设置 > 工具 > Big Video Generator` 中，填入您获取到的 `BigModel API Key`。

## 🛠️ 使用方法

本插件提供了两个核心工具来帮助您生成视频。

### 1. 文生视频 (`text2video`)

通过提供一段文本提示词来生成视频。

**参数:**

| 参数名      | 类型      | 是否必须 | 默认值            | 描述                                                                                               |
| :---------- | :-------- | :------- | :---------------- | :------------------------------------------------------------------------------------------------- |
| `prompt`    | `string`  | 是       | -                 | 用于生成视频的文本提示。                                                                           |
| `model`     | `string`  | 否       | `CogVideoX-Flash` | 使用的模型。默认为 `CogVideoX-Flash`。                                                             |
| `quality`   | `select`  | 否       | `speed`           | 输出模式 (`speed`/`quality`)。**注意：仅 `CogVideoX` 模型支持。**                                    |
| `with_audio`| `boolean` | 否       | `false`           | 是否生成 AI 音效。                                                                                 |
| `size`      | `select`  | 否       | -                 | 视频分辨率（如 `1920x1080`）。**注意：仅 `CogVideoX` 模型支持。**                                   |
| `fps`       | `select`  | 否       | `30`              | 视频帧率（`30`/`60`）。**注意：仅 `CogVideoX` 模型支持。**                                           |

### 2. 图生视频 (`image2video`)

通过提供一张图片和可选的文本提示来生成视频。

**参数:**

| 参数名      | 类型      | 是否必须 | 默认值            | 描述                                                                                               |
| :---------- | :-------- | :------- | :---------------- | :------------------------------------------------------------------------------------------------- |
| `image`     | `file`    | 是       | -                 | 用于生成视频的源图片。                                                                             |
| `prompt`    | `string`  | 否       | -                 | 用于指导视频生成的文本提示。                                                                       |
| `model`     | `string`  | 否       | `CogVideoX-Flash` | 使用的模型。默认为 `CogVideoX-Flash`。                                                             |
| `quality`   | `select`  | 否       | `speed`           | 输出模式 (`speed`/`quality`)。**注意：仅 `CogVideoX` 模型支持。**                                    |
| `with_audio`| `boolean` | 否       | `false`           | 是否生成 AI 音效。                                                                                 |
| `size`      | `select`  | 否       | -                 | 视频分辨率（如 `1920x1080`）。**注意：仅 `CogVideoX` 模型支持。**                                   |
| `fps`       | `select`  | 否       | `30`              | 视频帧率（`30`/`60`）。**注意：仅 `CogVideoX` 模型支持。**                                           |

> **模型说明**:
> *   `CogVideoX-Flash`: 默认模型，生成速度更快，但不支持 `quality`, `size`, 和 `fps` 参数的自定义。
> *   `CogVideoX`: 支持更丰富的自定义参数，可以生成更高质量和分辨率的视频。
