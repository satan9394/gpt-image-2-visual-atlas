# GPT Image 2 Visual Atlas

一个面向 GPT Image 2 提示词案例的静态可视化浏览器。

本项目基于 [freestylefly/awesome-gpt-image-2](https://github.com/freestylefly/awesome-gpt-image-2) 的公开案例内容整理而来，重点是把 Markdown 案例转成可搜索、可筛选、可复制提示词的视觉图谱。感谢原项目作者和社区贡献者持续整理案例数据。

> 说明：这是独立整理与可视化版本，不代表原项目作者维护。仓库内移除了与本项目无关的原作者联系方式、社群入口和推广信息，仅保留必要的数据来源致谢。

## 功能

- 中英双入口：`site/index.html` 为中文版，`site/index-en.html` 为英文版，避免界面文案中英混排。
- 左侧分类筛选，避免横向分类栏溢出或遮挡页面。
- 实时搜索标题、来源、图片描述和提示词正文。
- 图片画廊卡片浏览，点击查看完整提示词。
- 模板库视图，支持一键复制文本模板和 JSON 模板。
- 纯静态页面，无需后端服务，可直接部署到 GitHub Pages、Vercel、Netlify 或任意静态服务器。

## 文件结构

```text
.
├── data/images/          # 案例图片资源
├── docs/                 # 原始 Markdown 案例与模板
├── site/
│   ├── index.html        # 中文版静态可视化站点，可直接打开
│   ├── index-en.html     # 英文版静态可视化站点，可直接打开
│   ├── data.json         # 从 Markdown 提取的结构化数据
│   ├── generate.py       # 数据生成脚本
│   └── README.md         # 站点说明
├── LICENSE
└── README.md
```

## 本地预览

直接打开中文版本：

```text
site/index.html
```

或打开英文版本：

```text
site/index-en.html
```

两个 HTML 都已经内联 `data.json`，无需启动本地服务。

## 更新数据

当 `docs/` 或 `data/images/` 更新后，重新生成结构化数据：

```bash
cd site
python generate.py
```

`generate.py` 会读取根目录下的 `docs/gallery-part-*.md` 和 `docs/templates.md`，输出 `site/data.json`。

## 项目定位

原项目更像持续更新的案例资料库；本项目更像一个浏览、检索和复用提示词的前端工具。后续可以继续增加：

- 图片尺寸与来源统计
- 按 prompt 类型筛选
- 收藏/标记功能
- GitHub Pages 自动部署
- 从上游自动同步数据的工作流

## License

本仓库沿用 MIT License。案例内容与图片的来源请以原始贡献者和原项目说明为准。
