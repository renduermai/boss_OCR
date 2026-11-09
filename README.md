# PythonProject_bossOCR

## 能干什么

把招聘岗位截图批量 OCR 成结构化 Excel：

- 扫描指定文件夹里的岗位截图，识别文字；
- 用大模型从 OCR 文本中提取**公司名、薪资、地点、经验年限、学历、职位详情**；
- 按预设规则给岗位打 **1-5 分推荐等级**，写明推荐依据；
- 结果追加到 `AI岗位筛选汇总.xlsx`，附图片缩略图；
- **增量运行**：按文件内容 SHA256 去重，已入库的图片下次自动跳过，不重复花 API 费用；
- 长截图自动分片 OCR，避免缩小后小字糊掉；
- OCR 与岗位解析在线程池里并行，只有写 Excel 串行，保证文件不损坏。

## 每个文件是干什么的

| 文件 | 说明 |
| --- | --- |
| `quiker_png2excel.py` | **主程序（推荐使用）**。并发版：OCR + 解析并行，仅写 Excel 串行。 |
| `png2excel.py` | 串行版主程序，功能相同但逐张处理，慢一些。作为稳定回退方案保留。 |
| `models.py` | 模型客户端工厂。核心是 `get_tx_model_client()`，默认返回腾讯 hy4 的 LangChain 客户端；也提供阿里/DeepSeek/OpenAI/Claude 的获取函数，供其他实验使用。 |
| `config.py` | 读取 `.env` 并暴露为配置常量（各平台 key/url/model、切分配置、`BATCH_SIZE` 等）。 |
| `.env` | 密钥与实际模型配置。`TENCENT_API_KEY` / `TENCENT_API_URL` / `TENCENT_API_MODEL` 是主程序必需的三个值。 |
| `test.py` | 连通性自检脚本，验证 hy4 与阿里模型能否正常返回。 |
| `IMAGE_FOLDER/` | 截图存放目录，需要自己创建。Excel 与失败日志也生成在这里。 |

## 运行前准备

```bash
pip install -U langchain langchain-core langchain-community langchain-openai openai dashscope openpyxl pillow python-dotenv requests httpx
```

`.env` 中确认这三项存在：

```ini
TENCENT_API_KEY='...'
TENCENT_API_URL='https://tokenhub.tencentmaas.com/v1'
TENCENT_API_MODEL='hy4'
```

## 怎么运行

1. 把截图放进 `IMAGE_FOLDER`（默认 `D:\PythonProject_bossOCR\IMAGE_FOLDER`，可在主程序配置区改）。
2. 执行：

```bash
python quiker_png2excel.py
```

3. 结果在 `IMAGE_FOLDER\AI岗位筛选汇总.xlsx`，工作表「岗位汇总」；
   「去重记录」是隐藏表，存 SHA256，**不要手动删除或改表头**。
4. 想验证模型是否通，先跑：

```bash
python test.py
```

## 常用参数（主程序配置区）

| 参数 | 作用 |
| --- | --- |
| `IMAGE_FOLDER` | 截图目录，改成自己的路径 |
| `SCAN_SUBFOLDERS` | 是否扫描子目录 |
| `BATCH_SIZE` | 并行数，默认 `min(config.BATCH_SIZE, 5)`；报 429 就降到 3 |
| `CALL_INTERVAL` | 每批完成后的间隔秒数，防限流 |
| `OCR_MAX_TOKENS` / `PARSE_MAX_TOKENS` | OCR 与解析的输出上限 |

## 输出字段

`图片 | 文字 | 公司名 | 薪资范围 | 地点 | 经验年限 | 学历 | 职位详情 | 推荐依据 | 推荐等级（1-5分）`

评分含义：1 命中一票排除，2 明显偏离，3 信息缺失需核实，4 较匹配，5 高度适配。

## 注意事项

- 同一张图**只改文件名**会被跳过（按内容哈希判断，与文件名无关）。
- 同一画面**换了格式或重新压缩**（png→jpg、微信转运）字节不同，会被当作新图再识别一次。
- 失败的图片不记入去重表，下次运行会自动重试，错误写入 `IMAGE_FOLDER\识别失败记录.txt`。
- Excel 单格超过 32767 字符时，完整文字另存为 `图片名.完整文字.txt`。