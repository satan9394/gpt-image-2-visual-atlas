# GPT Image 2 Visual Atlas Site

这里是静态站点目录。

## 使用

推荐用本地静态服务预览：

```bash
python -m http.server 8080
```

然后打开：

```text
http://localhost:8080
```

也可以直接打开 `index.html`，但部分浏览器会限制本地文件读取 `data.json`。

## 数据来源

结构化数据来自根目录的 Markdown 文档，并由 `generate.py` 生成：

```bash
python generate.py
```

本项目感谢 `freestylefly/awesome-gpt-image-2` 的公开整理，但当前站点是独立可视化版本。
