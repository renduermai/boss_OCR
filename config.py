import os
from dotenv import load_dotenv

# 加载 .env文件
load_dotenv()

# ======================文件存储路径======================
# 数据文件路径
DATA_PATH = os.path.join(os.path.dirname(__file__),"DATA","deepseek百度百科.png") # 更改文件类型这里也要改

# chromaDB持久化路径
CHROMA_PATH =os.path.join(os.path.dirname(__file__),"DATA","CHROMA_DATA")

# ======================模型配置 API key==================
# 阿里云
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY","")
DASHSCOPE_API_URL = os.getenv("DASHSCOPE_API_URL","")
DASHSCOPE_API_MODEL = os.getenv("DASHSCOPE_API_MODEL","")
DASHSCOPE_API_EMBEDDING_MODEL = os.getenv("DASHSCOPE_API_EMBEDDING_MODEL","")
# 【新增】视觉大模型(给image_reader模块用)
DASHSCOPE_API_VL_MODEL = os.getenv("DASHSCOPE_API_VL_MODEL","")

# 腾讯云
TENCENT_API_URL = os.getenv("TENCENT_API_URL","")
TENCENT_API_MODEL = os.getenv("TENCENT_API_MODEL","")
TENCENT_API_KEY = os.getenv("TENCENT_API_KEY","")


# DeepSeek
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY","")
DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL","")
DEEPSEEK_API_MODEL = os.getenv("DEEPSEEK_API_MODEL","")

#openai
# 中转网站：https://pay.lllapi.top/keys
#（要开vpn才能用）
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY","")
OPENAI_API_URL = os.getenv("OPENAI_API_URL","")
OPENAI_API_MODEL = os.getenv("OPENAI_API_MODEL","")

# 中转网站：https://token.nbaky.cn/
#（不用开vpn）
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY_1","")
OPENAI_API_URL = os.getenv("OPENAI_API_URL_1","")
OPENAI_API_MODEL = os.getenv("OPENAI_API_MODEL_1","")
# 【新增】本地 VPN / 代理地址（访问境外中转用），留空则直连
OPENAI_LOCAL_PROXY = os.getenv("OPENAI_LOCAL_PROXY","")
# ---新增--- anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY","")
ANTHROPIC_API_URL = os.getenv("ANTHROPIC_API_URL","")
ANTHROPIC_API_MODEL = os.getenv("ANTHROPIC_API_MODEL","")

# ====================== 文本切分配置 ======================
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE","150"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP","30"))
SEPARATORS = ["\n\n","\n","。","？","，",""] # 分隔符优先级

# ====================== 批处理设置 ======================
BATCH_SIZE = int(os.getenv("BATCH_SIZE","10")) # 防止 API 限流
TOP_K = int(os.getenv("TOP_K","5"))
TEMPERATURE = float(os.getenv("TEMPERATURE","0")) # 温度

# ====================== 集合名称 ======================
COLLECTION_NAME = "demo"