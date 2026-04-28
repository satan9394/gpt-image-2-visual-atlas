"""Parse gallery markdown and templates into structured data.json."""
import json, re, os
from pathlib import Path
from datetime import datetime
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = ROOT / "data" / "images"
OUTPUT = Path(__file__).resolve().parent / "data.json"

CATEGORY_RULES = [
    ("historical", [
        (10, "历史"), (10, "古风"), (10, "汉服"), (9, "唐朝"), (9, "宋朝"),
        (9, "大明"), (9, "清朝"), (8, "古代"), (8, "国风"), (8, "赤壁"),
        (8, "短歌行"), (9, "敦煌"), (9, "飞天"), (8, "唐制"), (8, "明制"),
    ]),
    ("documents", [
        (10, "试卷"), (10, "处方笺"), (10, "报纸版式"), (10, "教科书"),
        (9, "手写笔记"), (9, "简历"), (9, "药方"), (9, "论文"),
        (8, "文档"), (8, "报纸"), (8, "杂志内页"), (8, "notebook"),
        (7, "菜单"), (7, "日历"), (7, "成绩单"), (7, "课本"),
    ]),
    ("characters", [
        (10, "人物设定"), (10, "角色设计"), (10, "立绘"), (10, "三面图"),
        (9, "圣斗士"), (9, "表情差分"), (9, "人设图"), (8, "character"),
        (7, "精灵"), (7, "人物角色"), (6, "人物"), (6, "角色"),
    ]),
    ("ecommerce", [
        (10, "电商"), (10, "直播带货"), (10, "商品图"), (9, "卖货"),
        (9, "产品展示"), (8, "双十一"), (8, "双十二"), (7, "售卖"),
        (7, "促销"), (6, "商品"),
    ]),
    ("branding", [
        (10, "品牌识别"), (10, "Logo设计"), (10, "VI系统"), (9, "标志设计"),
        (9, "视觉识别"), (9, "品牌视觉"), (8, "企业形象"), (8, "brand identity"),
        (7, "logo"),
    ]),
    ("ui", [
        (10, "界面设计"), (10, "APP界面"), (10, "APP首页"), (10, "UI界面"),
        (9, "手机截图"), (9, "微信聊天记录"), (9, "朋友圈截图"),
        (9, "APP截图"), (9, "小红书截图"), (9, "抖音截图"),
        (8, "手机界面"), (8, "用户界面"), (8, "仪表盘设计"),
        (7, "界面UI"), (7, "社交媒体帖子"), (7, "screenshot"),
        (6, "微信"), (6, "APP"), (6, "手机"), (6, "直播"),
    ]),
    ("infographic", [
        (10, "信息图可视化"), (10, "信息图表"), (10, "图解"), (10, "技术分解"),
        (10, "分解图"), (9, "信息图"), (9, "infographic"), (9, "一览图"),
        (9, "爆炸图"), (9, "拆解图"), (8, "图谱"), (8, "百科图"),
        (8, "结构图"), (8, "diagram"), (8, "导览图"),
        (7, "可视化"), (7, "流程图"), (7, "架构图"), (7, "全览"),
        (7, "切面图"), (7, "剖面图"), (7, "关系图"),
    ]),
    ("architecture", [
        (10, "建筑设计"), (10, "室内设计"), (10, "空间设计"), (9, "园林设计"),
        (9, "建筑效果图"), (8, "城市设计"), (8, "interior design"),
        (7, "建筑"), (7, "室内"), (7, "园林"), (7, "architecture"),
        (6, "空间"), (6, "景观"),
    ]),
    ("photography", [
        (10, "摄影"), (10, "写真"), (9, "写实摄影"), (9, "街拍"),
        (9, "photography"), (8, "胶片"), (8, "cinematic"),
        (7, "写实"), (7, "照片"), (7, "相机"), (7, "photorealistic"),
    ]),
    ("illustration", [
        (10, "插画"), (10, "手绘"), (9, "水彩"), (9, "漫画风格"),
        (9, "二次元"), (8, "涂鸦"), (8, "illustration"), (8, "anime"),
        (7, "绘画"), (7, "童话"), (7, "绘本"), (7, "日系"),
        (6, "艺术"), (6, "扁平"),
    ]),
    ("poster", [
        (10, "海报设计"), (10, "海报排版"), (10, "宣传海报"), (9, "封面设计"),
        (9, "明信片"), (9, "poster"), (8, "卡牌设计"), (8, "版式设计"),
        (7, "海报"), (7, "广告"), (7, "banner"), (7, "flyer"),
        (7, "封面图"), (6, "封面"), (6, "排版"),
    ]),
    ("scenes", [
        (10, "场景图"), (10, "叙事场景"), (9, "场景设计"), (9, "世界观"),
        (8, "scene"), (8, "narrative"), (7, "场景"),
    ]),
]


def infer_category(title, prompt):
    text = (title + " " + prompt[:300]).lower()
    scores = {}
    for cat, keywords in CATEGORY_RULES:
        for score, kw in keywords:
            if kw.lower() in text:
                scores[cat] = scores.get(cat, 0) + score
    if scores:
        return max(scores, key=scores.get)
    return "other"


def normalize_source(source_text):
    text = source_text.strip()
    if not text or text == "未提供":
        return text, "unknown"
    if "小红书" in text:
        return text, "xiaohongshu"
    if "x.com" in text or "twitter.com" in text:
        return text, "twitter"
    if "苍何" in text:
        return text, "canghe_original"
    return text, "other"


def parse_gallery(filepath, book):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    parts = re.split(r'<a\s+name="case-(\d+)"></a>', text)
    cases = []

    for i in range(1, len(parts), 2):
        case_num = int(parts[i])
        body = parts[i + 1]

        title_m = re.search(r'###\s+例\s+\d+\s*[：:]\s*(.+?)(?:\n|$)', body)
        title = title_m.group(1).strip() if title_m else ""

        img_m = re.search(r'!\[(.*?)\]\(\.\.\/data\/images\/(case\d+\.\w+)\)', body)
        alt = img_m.group(1).strip() if img_m else ""
        img_file = img_m.group(2) if img_m else ""

        src_m = re.search(r'\*\*来源[：:]\*\*\s*(.*?)\s*\*\*提示词[：:]\*\*', body, re.DOTALL)
        if src_m:
            source_raw = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', src_m.group(1).strip())
            source_raw = re.sub(r'<[^>]+>', '', source_raw)
        else:
            source_raw = "未提供"
        source, source_type = normalize_source(source_raw)

        prompt_m = re.search(r'\*\*提示词[：:]\*\*\s*(?:[\s\S]*?)```\w*\n(.*?)```', body, re.DOTALL)
        prompt = prompt_m.group(1).strip() if prompt_m else ""

        prompt_type = "text"
        if prompt.strip().startswith('{') and prompt.strip().endswith('}'):
            if '{argument name=' in prompt or 'argument name="' in prompt:
                prompt_type = "template_json"
            else:
                try:
                    json.loads(prompt)
                    prompt_type = "json"
                except:
                    prompt_type = "template_json"

        if '[中文]' in prompt and '[English]' in prompt:
            prompt_type = "bilingual"

        category = infer_category(title, prompt)

        cases.append({
            "id": case_num, "title": title, "image": img_file,
            "alt": alt, "source": source, "source_type": source_type,
            "prompt": prompt, "prompt_type": prompt_type,
            "category": category, "book": book,
        })

    return cases


def parse_templates(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    sections = re.split(r'\n(?=### )', text)
    templates = []

    cat_to_id = {
        "UI与界面": "ui", "图表与信息可视化": "infographic",
        "海报与排版": "poster", "商品与电商": "ecommerce",
        "品牌与标志": "branding", "建筑与空间": "architecture",
        "摄影与写实": "photography", "插画与艺术": "illustration",
        "人物与角色": "characters", "场景与叙事": "scenes",
        "历史与古风题材": "historical", "文档与出版物": "documents",
        "其他应用场景": "other",
    }

    for section in sections[1:]:
        header_m = re.match(r'###\s+(.+)', section)
        if not header_m:
            continue
        category_name = header_m.group(1).strip()
        cat_id = cat_to_id.get(category_name, category_name)

        text_tmpl_m = re.search(r'常规模板.*?\n```(?:text)?\n(.*?)```', section, re.DOTALL)
        text_template = text_tmpl_m.group(1).strip() if text_tmpl_m else ""

        json_tmpl_m = re.search(r'JSON\s*进阶模板.*?\n```(?:json)?\n(.*?)```', section, re.DOTALL)
        json_template = json_tmpl_m.group(1).strip() if json_tmpl_m else ""

        tips_m = re.search(r'避坑指南.*?\n(.*?)(?:\n(?=###)|\Z)', section, re.DOTALL)
        tips = []
        if tips_m:
            tips_text = tips_m.group(1).strip()
            tip_items = re.findall(r'[-*]\s+\*\*(.+?)\*\*[：:]?(.*?)(?=\n[-*]|\Z)', tips_text, re.DOTALL)
            if tip_items:
                tips = [{"title": t[0].strip(), "detail": t[1].strip()} for t in tip_items]

        templates.append({
            "id": cat_id, "category": category_name,
            "text_template": text_template,
            "json_template": json_template,
            "tips": tips,
        })

    return templates


def main():
    print("Parsing gallery files...")
    cases1 = parse_gallery(ROOT / "docs" / "gallery-part-1.md", 1)
    cases2 = parse_gallery(ROOT / "docs" / "gallery-part-2.md", 2)
    all_cases = cases1 + cases2

    print(f"  Part 1: {len(cases1)} cases")
    print(f"  Part 2: {len(cases2)} cases")
    print(f"  Total: {len(all_cases)} cases")

    for c in all_cases:
        if not c['image']:
            for ext in ['.jpg', '.png']:
                if (IMAGES_DIR / f"case{c['id']}{ext}").exists():
                    c['image'] = f"case{c['id']}{ext}"
                    break

    missing = [c['id'] for c in all_cases if not c['image']]
    if missing:
        print(f"  WARNING: missing images for cases: {missing}")

    print("Parsing templates...")
    templates = parse_templates(ROOT / "docs" / "templates.md")
    print(f"  {len(templates)} templates")

    cat_counts = Counter(c['category'] for c in all_cases)

    categories_meta = {
        "ui": {"name": "UI与界面", "eng": "UI/Interface", "icon": "📱"},
        "infographic": {"name": "图表与信息可视化", "eng": "Infographic", "icon": "📊"},
        "poster": {"name": "海报与排版", "eng": "Poster/Typography", "icon": "🎨"},
        "ecommerce": {"name": "商品与电商", "eng": "E-commerce", "icon": "🛒"},
        "branding": {"name": "品牌与标志", "eng": "Branding", "icon": "🏷️"},
        "architecture": {"name": "建筑与空间", "eng": "Architecture", "icon": "🏛️"},
        "photography": {"name": "摄影与写实", "eng": "Photography", "icon": "📷"},
        "illustration": {"name": "插画与艺术", "eng": "Illustration", "icon": "🖌️"},
        "characters": {"name": "人物与角色", "eng": "Characters", "icon": "👤"},
        "scenes": {"name": "场景与叙事", "eng": "Scenes", "icon": "🎬"},
        "historical": {"name": "历史与古风题材", "eng": "Historical", "icon": "🏮"},
        "documents": {"name": "文档与出版物", "eng": "Documents", "icon": "📄"},
        "other": {"name": "其他应用场景", "eng": "Other", "icon": "✨"},
    }

    data = {
        "meta": {
            "total_cases": len(all_cases),
            "total_templates": len(templates),
            "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "categories": {k: {**v, "count": cat_counts.get(k, 0)}
                          for k, v in categories_meta.items()},
        },
        "cases": all_cases,
        "templates": templates,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nOutput: {OUTPUT} ({OUTPUT.stat().st_size // 1024}KB)")
    print("\nCategory distribution:")
    for cat_id, meta in categories_meta.items():
        count = cat_counts.get(cat_id, 0)
        print(f"  [{cat_id:15s}] {meta['name']}: {count}")

    print("\nDone!")


if __name__ == "__main__":
    main()
