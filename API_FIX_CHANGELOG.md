# API修复变更日志

## 修复日期
2025-08-22

## 修复问题
针对用户报告的UUID错误和API变更问题进行了全面修复。

### 原始错误信息
```
Run failed: (psycopg2.errors.InvalidTextRepresentation) invalid input syntax for type uuid: "b209b190-7f1d-11f0-86d6-16aaa01fe9f4_0"
LINE 3: WHERE tool_files.id = 'b209b190-7f1d-11f0-86d6-16aaa01fe9f4_...
```

## 修复内容

### 1. 根本原因分析
- UUID错误不是插件代码直接造成的问题
- 这是Dify平台在处理工具文件时的数据库查询问题
- 错误的UUID格式包含了不符合标准的后缀`_0`

### 2. API路径修复
- **修复前**: `/async-result/{id}`
- **修复后**: `/async/result/{id}`
- 影响文件:
  - `tools/text2video.py`
  - `tools/image2video.py`

### 3. 模型名称标准化
- **修复前**: `CogVideoX-Flash`, `CogVideoX`
- **修复后**: `cogvideox-flash`, `cogvideox`
- 影响文件:
  - `tools/text2video.py`
  - `tools/image2video.py`
  - `tools/text2video.yaml`
  - `tools/image2video.yaml`

### 4. 增强错误处理
#### 4.1 HTTP状态码检查
- 添加详细的HTTP错误状态码检查
- 区分不同类型的HTTP错误
- 提供更具体的错误信息

#### 4.2 任务状态处理优化
- **支持的成功状态**: `SUCCESS`
- **支持的失败状态**: `FAIL`, `FAILED`
- **支持的处理中状态**: `PROCESSING`, `PENDING`, `RUNNING`
- 添加未知状态的处理逻辑

#### 4.3 响应解析增强
- 增强JSON响应解析的容错性
- 添加响应内容的详细日志
- 改进视频结果验证逻辑

#### 4.4 调试信息优化
- 保留原有的状态码和响应日志
- 添加完整的异常堆栈信息
- 区分网络错误和其他异常

## 详细修改

### tools/text2video.py
1. 更新默认模型名称为 `cogvideox-flash`
2. 修复API路径为 `/async/result/{task_id}`
3. 增强任务创建的错误处理
4. 优化任务状态轮询逻辑
5. 改进异常处理和日志记录

### tools/image2video.py
1. 更新默认模型名称为 `cogvideox-flash`
2. 修复API路径为 `/async/result/{task_id}`
3. 增强任务创建的错误处理
4. 优化任务状态轮询逻辑
5. 改进异常处理和日志记录

### tools/text2video.yaml
1. 更新模型描述和默认值
2. 统一模型名称格式
3. 更新相关参数说明

### tools/image2video.yaml
1. 更新模型描述和默认值
2. 统一模型名称格式
3. 更新相关参数说明

## 预期效果

### 1. UUID错误解决
虽然UUID错误是Dify平台级别的问题，但通过API路径和错误处理的修复，可以减少因API调用失败导致的相关问题。

### 2. API兼容性提升
- 修复的API路径符合最新的智谱AI API规范
- 模型名称标准化避免了因命名不一致导致的调用失败

### 3. 错误诊断能力增强
- 提供更详细的错误信息，便于问题定位
- 支持多种任务状态，提高容错性
- 改进的日志记录有助于调试

### 4. 用户体验改善
- 更准确的错误提示
- 更稳定的视频生成流程
- 更好的异常恢复能力

## 测试建议

1. **基本功能测试**
   - 测试文生视频功能
   - 测试图生视频功能
   - 验证不同模型参数的正确性

2. **错误处理测试**
   - 测试无效API密钥的处理
   - 测试网络异常的处理
   - 测试API服务不可用的处理

3. **边界条件测试**
   - 测试大文件上传
   - 测试长时间任务的处理
   - 测试并发调用的稳定性

## 注意事项

1. 如果UUID错误仍然出现，需要检查Dify平台的文件处理机制
2. 建议定期检查智谱AI API文档的更新
3. 保持与最新API规范的同步

## 联系信息
如有问题，请联系开发团队或查看项目文档。