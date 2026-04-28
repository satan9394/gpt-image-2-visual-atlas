# GPT Image 2 Visual Atlas Site

这里是静态站点目录。

## 使用

直接打开：

```text
index.html     # 中文版
index-en.html  # 英文版
```

两个入口都已经内联数据，不需要启动本地服务，也不会因为浏览器限制 `file://` 读取 `data.json` 而空白。

## 数据来源

结构化数据来自根目录的 Markdown 文档，并由 `generate.py` 生成：

```bash
python generate.py
```

本项目感谢 `freestylefly/awesome-gpt-image-2` 的公开整理，但当前站点是独立可视化版本。
