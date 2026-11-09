# models.py
# 可用模型列表，以及获得访问模型的客户端
#     实际使用时可以根据自己的实际情况调整

import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatTongyi

from config import BATCH_SIZE, DASHSCOPE_API_VL_MODEL, OPENAI_LOCAL_PROXY
# ---新增--- 导入 anthropic 相关配置
from config import (
    BATCH_SIZE, DASHSCOPE_API_VL_MODEL, OPENAI_LOCAL_PROXY,
    ANTHROPIC_API_KEY, ANTHROPIC_API_URL, ANTHROPIC_API_MODEL,
)

load_dotenv()

# 阿里的通义千问大模型（主要使用）
#    官网: https://bailian.console.aliyun.com/#/home
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_API_URL = os.getenv("DASHSCOPE_API_URL")
DASHSCOPE_API_MODEL = os.getenv("DASHSCOPE_API_MODEL")
DASHSCOPE_API_EMBEDDING_MODEL = os.getenv("DASHSCOPE_API_EMBEDDING_MODEL")

# 腾讯云
TENCENT_API_URL = os.getenv("TENCENT_API_URL")
TENCENT_API_MODEL = os.getenv("TENCENT_API_MODEL")
TENCENT_API_KEY = os.getenv("TENCENT_API_KEY")


# DeepSeek
#   官网：https://platform.deepseek.com/api_keys
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL")
DEEPSEEK_API_MODEL = os.getenv("DEEPSEEK_API_MODEL")
DEEPSEEK_REASONER_MODEL = "deepseek-reasoner"

# openai
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = os.getenv("OPENAI_API_URL")
OPENAI_API_MODEL = os.getenv("OPENAI_API_MODEL")

OPENAI_API_KEY_1 = os.getenv("OPENAI_API_KEY_1")
OPENAI_API_URL_1 = os.getenv("OPENAI_API_URL_1")
OPENAI_API_MODEL_1 = os.getenv("OPENAI_API_MODEL_1")

import inspect
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import DashScopeEmbeddings, HunyuanEmbeddings

# 【新增】OpenAI 中转专用依赖
import httpx
import requests


# 【不要用这个，只是方便后面return】通过LangChain获得指定平台和模型的客户端 (默认是：阿里通义千问)
def get_lc_model_client(api_key=DASHSCOPE_API_KEY,
                        base_url=DASHSCOPE_API_URL,
                        model=DASHSCOPE_API_MODEL,
                        temperature=0.7, verbose=False,
                        debug=False,
                        extra_body=None):
    """
        通过LangChain获得指定平台和模型的客户端，设定的默认平台和模型为阿里百炼qwen
        也可以通过传入api_key，base_url，model三个参数来覆盖默认值
        verbose，debug两个参数，分别控制是否输出调试信息，是否输出详细调试信息，默认不打印
    """
    function_name = inspect.currentframe().f_code.co_name
    if (verbose):
        print(f"{function_name}-平台：{base_url},模型：{model},温度：{temperature}")
    if (debug):
        print(f"{function_name}-平台：{base_url},模型：{model},温度：{temperature},key：{api_key}")
    if extra_body is None:
        extra_body = {"enable_thinking": False}  # 保持阿里原有行为
    return ChatOpenAI(api_key=api_key,
                      base_url=base_url,
                      model=model,
                      temperature=temperature,
                      extra_body=extra_body or None)



# 【正常使用】通过LangChain使用阿里大模型ChatTongyi
qwen = ChatTongyi(
    model='qwen-plus', # 注意这个方法只支持：qwen-plus,qwen-turbo,qwen-max,qwen-max-longcontext,qwen-vl-plus / qwen-vl-max,qwen-audio-turbo
    temperature=0.2,
    max_tokens=2048,
    stream=False,
    enable_search=False, # 禁用搜索功能
)


# 【正常使用】通过LangChain使用阿里大模型
def get_ali_model_client(model=DASHSCOPE_API_MODEL,
                         temperature=None, verbose=False, debug=False):
    """通过LangChain使用阿里大模型"""
    return get_lc_model_client(api_key=DASHSCOPE_API_KEY,
                               base_url=DASHSCOPE_API_URL,
                               model=model,
                               temperature=temperature,
                               verbose=verbose,
                               debug=debug)

# 【正常使用】通过LangChain使用腾讯大模型
def get_tx_model_client(model=TENCENT_API_MODEL,
                         temperature=None, verbose=False, debug=False):
    """通过LangChain使用腾讯大模型"""
    return get_lc_model_client(api_key=TENCENT_API_KEY,
                               base_url=TENCENT_API_URL,
                               model=model,
                               temperature=temperature,
                               verbose=verbose,
                               debug=debug)


# 【正常使用】通过LangChain使用 DeepSeek大模型
def get_ds_model_client(model=DEEPSEEK_API_MODEL,
                        temperature=0.7, verbose=False, debug=False):
    """通过LangChain使用DeepSeek大模型"""
    return get_lc_model_client(api_key=DEEPSEEK_API_KEY,
                               base_url=DEEPSEEK_API_URL,
                               model=model,
                               temperature=temperature,
                               verbose=verbose,
                               debug=debug)

# 【正常使用】通过LangChain使用openai大模型(不开vpn能用）
# 中转网站：https://token.nbaky.cn/
def get_openai_model_client_1(model=OPENAI_API_MODEL_1,
                         temperature=0.7, verbose=False, debug=False):
    """通过LangChain使用openai大模型"""
    return get_lc_model_client(api_key=OPENAI_API_KEY_1,
                               base_url=OPENAI_API_URL_1,
                               model=model,
                               temperature=temperature,
                               verbose=verbose,
                               debug=debug)

# ================= OpenAI 中转（改造部分） =================
# 特性：
#   1. 自动探测可用代理（OPENAI_PROXY，默认来自 .env，可留空表示全局 TUN）
#   2. 自动选择 /chat/completions 还是 /responses 协议
#   3. 首次调用打印中转支持的全部模型，方便切换 OPENAI_API_MODEL

_openai_probe_cache = None


def _openai_base_url() -> str:
    url = (OPENAI_API_URL or "").rstrip("/")
    if not url:
        raise RuntimeError("OPENAI_API_URL 未配置，请检查 .env")
    return url if url.endswith("/v1") else url + "/v1"

def _openai_proxy_candidates():
    """把 OPENAI_LOCAL_PROXY 展开成候选列表：http / socks5h / socks5 / 直连"""
    raw = (OPENAI_LOCAL_PROXY or "").strip()
    if not raw:
        return [None]
    if "://" in raw:
        return [raw, None]
    return [f"http://{raw}", f"socks5h://{raw}", f"socks5://{raw}", None]

def _openai_probe(verbose: bool = False) -> dict:
    """探测代理、模型列表、协议。结果进程内缓存，只探测一次。"""
    global _openai_probe_cache
    if _openai_probe_cache is not None:
        return _openai_probe_cache

    base = _openai_base_url()
    hdrs = {"Authorization": f"Bearer {OPENAI_API_KEY}"}

    working_proxy = None
    models = None
    last_err = None

    for p in _openai_proxy_candidates():
        req_proxies = {"http": p, "https": p} if p else None
        try:
            r = requests.get(f"{base}/models", headers=hdrs,
                             timeout=(5, 20), proxies=req_proxies)
            if verbose:
                print(f"[OpenAI] 代理={p or '直连'} GET /models → {r.status_code}")
            if r.ok:
                models = [m.get("id") for m in r.json().get("data", []) if m.get("id")]
                working_proxy = p
                break
            if r.status_code in (401, 403):
                raise RuntimeError(f"key 被拒（HTTP {r.status_code}）：{r.text[:200]}")
        except RuntimeError:
            raise
        except Exception as e:
            last_err = e
            if verbose:
                print(f"[OpenAI] 代理={p or '直连'} 失败：{type(e).__name__}: {str(e)[:80]}")

    if working_proxy is None and models is None:
        raise RuntimeError(f"OpenAI 中转不可达（检查 VPN/代理端口 OPENAI_PROXY）。最后一次错误：{last_err!r}")

    # 协议探测：先试 chat/completions，若路由不存在再试 responses
    protocol = "chat"
    req_proxies = {"http": working_proxy, "https": working_proxy} if working_proxy else None
    try:
        r = requests.post(
            f"{base}/chat/completions",
            headers={**hdrs, "Content-Type": "application/json"},
            json={"model": OPENAI_API_MODEL,
                  "messages": [{"role": "user", "content": "ping"}],
                  "max_tokens": 1},
            timeout=(5, 30), proxies=req_proxies,
        )
        if r.status_code in (404, 405):
            # 路由不存在，试 /responses
            r2 = requests.post(
                f"{base}/responses",
                headers={**hdrs, "Content-Type": "application/json"},
                json={"model": OPENAI_API_MODEL, "input": "ping", "store": False},
                timeout=(5, 30), proxies=req_proxies,
            )
            if r2.status_code not in (404, 405):
                protocol = "responses"
    except Exception:
        pass

    if verbose:
        print(f"[OpenAI] 使用协议：{protocol}")

    _openai_probe_cache = {"proxy": working_proxy, "models": models or [], "protocol": protocol}
    return _openai_probe_cache

def _print_openai_models(models):
    print(f"[OpenAI] 中转共 {len(models)} 个可用模型：")
    for m in models:
        mark = "   ← 当前使用" if m == OPENAI_API_MODEL else ""
        print(f"   - {m}{mark}")
    if OPENAI_API_MODEL not in models:
        print(f"[OpenAI] ⚠ 当前配置 '{OPENAI_API_MODEL}' 不在列表中，请更换 OPENAI_API_MODEL")

def _build_openai_client(proxy, protocol, model, temperature):
    kwargs = dict(
        api_key=OPENAI_API_KEY,
        base_url=_openai_base_url(),
        model=model,
        temperature=temperature,
        timeout=120,
        max_retries=2,
        openai_proxy=None,      # ← 关键：显式置 None，防止 langchain 从环境变量读到值后与 http_client 冲突
    )
    try:
        http_client = httpx.Client(proxy=proxy,
                                   timeout=httpx.Timeout(120.0, connect=30.0))
    except TypeError:  # 老版本 httpx
        http_client = httpx.Client(proxies=proxy,
                                   timeout=httpx.Timeout(120.0, connect=30.0))
    kwargs["http_client"] = http_client
    if protocol == "responses":
        kwargs["use_responses_api"] = True

    try:
        return ChatOpenAI(**kwargs)
    except TypeError:
        kwargs.pop("use_responses_api", None)
        return ChatOpenAI(**kwargs)

# 【正常使用】通过LangChain使用openai大模型（要开vpn才能用）
def get_openai_model_client(model=OPENAI_API_MODEL,
                            temperature=0.7,
                            verbose=False,
                            debug=False,
                            show_models=True):
    """
    通过LangChain使用 OpenAI（含 lllapi 中转）
    - 自动探测可用代理（OPENAI_PROXY，来自 .env，可留空走全局 TUN）
    - 自动选择 /chat/completions 或 /responses 协议
    - 首次调用打印中转支持的全部模型（show_models=False 关闭）
    """
    probe = _openai_probe(verbose=verbose)
    if show_models and probe["models"]:
        _print_openai_models(probe["models"])
    if debug:
        print(f"get_openai_model_client-代理={probe['proxy']} 协议={probe['protocol']} "
              f"模型={model} key={str(OPENAI_API_KEY)[:8]}...")
    return _build_openai_client(
        proxy=probe["proxy"],
        protocol=probe["protocol"],
        model=model,
        temperature=temperature,
    )


# ================= ---新增--- Anthropic Claude 中转 =================
# 【！不正常使用】claude报错400 建议用另一个中转站调claude
_anthropic_probe_cache = None

def _anthropic_root_url() -> str:
    """把带 /v1 的地址归一成根地址，ChatAnthropic 会自动拼 /v1/messages"""
    url = (ANTHROPIC_API_URL or "").rstrip("/")
    if url.endswith("/v1"):
        url = url[:-3]
    if not url:
        raise RuntimeError("ANTHROPIC_API_URL 未配置，请检查 .env")
    return url

def _anthropic_probe(verbose: bool = False) -> dict:
    global _anthropic_probe_cache
    if _anthropic_probe_cache is not None:
        return _anthropic_probe_cache

    base = _anthropic_root_url()
    hdrs = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
    }

    working_proxy = None
    models = []
    last_err = None

    for p in _openai_proxy_candidates():
        req_proxies = {"http": p, "https": p} if p else None
        try:
            r = requests.get(f"{base}/v1/models", headers=hdrs,
                             timeout=(5, 20), proxies=req_proxies)
            if verbose:
                print(f"[Anthropic] 代理={p or '直连'} GET /v1/models → {r.status_code}")
            if r.ok:
                working_proxy = p
                data = r.json().get("data", [])
                models = [m.get("id") for m in data if m.get("id")]
                break
            if r.status_code in (401, 403):
                raise RuntimeError(f"Anthropic key 被拒（HTTP {r.status_code}）：{r.text[:200]}")
        except RuntimeError:
            raise
        except Exception as e:
            last_err = e
            if verbose:
                print(f"[Anthropic] 代理={p or '直连'} 失败：{type(e).__name__}: {str(e)[:80]}")

    if working_proxy is None and not models:
        raise RuntimeError(
            f"Anthropic 中转不可达（检查 VPN / OPENAI_LOCAL_PROXY）。最后错误：{last_err!r}"
        )

    _anthropic_probe_cache = {"proxy": working_proxy, "base_url": base, "models": models}
    return _anthropic_probe_cache

def _print_anthropic_models(models):
    print(f"[Anthropic] 中转共 {len(models)} 个可用模型：")
    for m in models:
        mark = "   ← 当前使用" if m == ANTHROPIC_API_MODEL else ""
        print(f"   - {m}{mark}")
    if ANTHROPIC_API_MODEL not in models:
        print(f"[Anthropic] ⚠ 当前配置 '{ANTHROPIC_API_MODEL}' 不在列表中，请更换 ANTHROPIC_API_MODEL")

# ---新增--- 新版 SDK 用 httpx2，老版用 httpx，哪个 SDK 接受就用哪个
def _build_anthropic_sdk_client(proxy, base_url):
    from anthropic import Anthropic

    for mod_name in ("httpx2", "httpx"):
        try:
            mod = __import__(mod_name)
        except ImportError:
            continue
        try:
            kw = {"timeout": 120.0}
            if proxy:
                try:
                    c = mod.Client(proxy=proxy, **kw)
                except TypeError:
                    c = mod.Client(proxies=proxy, **kw)
            else:
                c = mod.Client(**kw)
        except Exception:
            continue

        try:
            return Anthropic(api_key=ANTHROPIC_API_KEY,
                             base_url=base_url,
                             http_client=c)
        except TypeError:
            continue

    return Anthropic(api_key=ANTHROPIC_API_KEY, base_url=base_url)

# ---新增--- max_tokens 默认 8192；claude 5.x 不支持自定义 temperature
# 【！不正常使用】目前claude报错400，可以用另一个中转站调用claude
def get_anthropic_model_client(model=ANTHROPIC_API_MODEL,
                               temperature=None,
                               max_tokens=8192,
                               verbose=False,
                               show_models=True):
    """
    通过 LangChain 使用 Anthropic Claude（lllapi 中转）
    - 代理复用 OPENAI_LOCAL_PROXY
    - max_tokens 默认 8192（Kiro 上游对较小的值会 400）
    - claude 5.x 不支持自定义 temperature，默认 None 即可
    """
    from langchain_anthropic import ChatAnthropic

    probe = _anthropic_probe(verbose=verbose)
    if show_models and probe["models"]:
        _print_anthropic_models(probe["models"])

    base_kwargs = {"model": model, "max_tokens": max_tokens}
    if temperature is not None:
        base_kwargs["temperature"] = temperature

    llm = None
    last_type_err = None
    for extra in (
        {"anthropic_api_key": ANTHROPIC_API_KEY, "anthropic_api_url": probe["base_url"]},
        {"api_key": ANTHROPIC_API_KEY, "base_url": probe["base_url"]},
    ):
        try:
            llm = ChatAnthropic(**base_kwargs, **extra)
            break
        except TypeError as e:
            last_type_err = e
    if llm is None:
        raise RuntimeError(f"ChatAnthropic 参数不兼容，建议 pip install -U langchain-anthropic。{last_type_err}")

    sdk_client = _build_anthropic_sdk_client(probe["proxy"], probe["base_url"])
    if hasattr(llm, "_client"):
        try:
            llm._client = sdk_client
        except Exception:
            try:
                object.__setattr__(llm, "_client", sdk_client)
            except Exception:
                pass

    return llm


# [向量化]该平台限制单次请求最多 20 条文本，需要按 BATCH_SIZE 分批调用
class BatchedDashScopeEmbeddings(DashScopeEmbeddings):
    """按小批次调用 DashScope 向量模型，避免超出平台单次批量上限"""

    def embed_documents(self, texts):
        batch_size = min(BATCH_SIZE, 20)  # 平台限制：单次最多 20 条
        embeddings = []
        for i in range(0, len(texts), batch_size):
            embeddings.extend(super().embed_documents(texts[i : i + batch_size]))
        return embeddings


# [向量化]通过LangChain获得一个阿里通义千问向量化模型的实例
def get_ali_embeddings(model=DASHSCOPE_API_EMBEDDING_MODEL):
    """通过LangChain获得一个阿里通义千问向量化模型的实例"""
    return BatchedDashScopeEmbeddings(
        model=model,
        dashscope_api_key=DASHSCOPE_API_KEY,
    )

# [视觉模型]通过LangChain获得一个阿里通义千问视觉模型的实例
def get_ali_vl_model_client(model=DASHSCOPE_API_VL_MODEL,  # 使用视觉模型的环境变量
                          temperature=0.7, verbose=False, debug=False):
    """通过LangChain获得一个阿里通义千问视觉模型的实例"""
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        api_key=DASHSCOPE_API_KEY,
        base_url=DASHSCOPE_API_URL,
        model=model,
        temperature=temperature,
        verbose=verbose

    )