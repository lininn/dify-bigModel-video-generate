from dify_plugin import Plugin, DifyPluginEnv
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 设置超时时间为6分钟，确保轮询能够完成
# 轮询最大时间：60次 × 5秒 = 300秒，加上缓冲时间
plugin = Plugin(DifyPluginEnv(MAX_REQUEST_TIMEOUT=360))
logger.info("插件初始化完成，超时设置为360秒")

if __name__ == '__main__':
    plugin.run()
