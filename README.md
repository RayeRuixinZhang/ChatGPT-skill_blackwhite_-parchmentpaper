# 黑底硫酸纸画卡

`black-parchment-cards` 把参考照片、画作或现有卡片做成一套黑底硫酸纸画卡。它从每张参考图中选出可辨认的主体，将轮廓、姿态或倒影提取成独立插画，并在黑底的空白处排英文标题和一句短诗。

| 项目 | 默认做法 |
| --- | --- |
| 尺寸和底色 | 50 × 100 mm 竖卡，纯黑底 |
| 主体 | 保留辨识度，按题材选画法。未指定数量时，每张参考图做一张 |
| 英文文字 | 标题用 Times New Roman，诗句用 Lucida Handwriting。提供的文案按原文排版 |
| 配色 | 低饱和版采用清冷、克制的色调。彩色版使用参考图中对应元素的颜色 |
| 交付 | 两版使用相同的主体、黑底、文案和排版，分别导出可编辑 PDF。按需加 A4 打印版 |

## 在 ChatGPT 或 Codex 中使用

1. 在支持 Skills 的环境中添加本仓库的 skill，保留 [SKILL.md](SKILL.md)、`scripts/`、`references/` 和 `agents/` 的目录结构。
2. 上传参考图。多张图可以按成品顺序上传，或用编号说明图与卡片的对应关系。若有必须保留的细节，比如天鹅颈部的姿态、雪枝的走向或雕塑的手势，和图片一起说明。
3. 调用 `$black-parchment-cards`。如果已有英文标题或诗句，可以按卡片编号粘贴原文。需要 A4 排版、不同尺寸或先看试样时，在同一条指令里说明。

> 用 $black-parchment-cards 把这 4 张参考图做成 4 张 50 × 100 mm 的纯黑底硫酸纸卡。保留天鹅的姿态和雪枝的轮廓，其余按题材选画法。为每张卡写英文标题和一句短诗，直接给我两版对照预览、低饱和与原图取色的 Affinity 可编辑 PDF，以及带出血和裁切标记的 A4 版。

## 字体与本地导出

正式导出需要 **Times New Roman** 和 **Lucida Handwriting** 的授权字体文件。缺少字体时，可以先完成图稿和文案，等字体齐备再导出正式印稿。编辑电脑上也应安装这两款字体。

备好两套同构图的透明 PNG 和文字后，可在仓库根目录运行排版脚本。需要 Python 3.10+。清单格式、坐标和排版选项见 [排版与导出](references/export.md)。

```bash
python -m pip install Pillow ReportLab fonttools
python scripts/build_pdf.py cards.json cards-editable.pdf --palette both --title-font /path/to/times.ttf --poem-font /path/to/LHANDW.TTF
python scripts/build_pdf.py cards.json cards-a4.pdf --palette both --title-font /path/to/times.ttf --poem-font /path/to/LHANDW.TTF --a4
```

同一次导出生成带 `-low-saturation` 与 `-original-color` 后缀的两份 PDF。单张版 PDF 每页一张成品卡。带 `--a4` 的版本在 A4 页面上排版，并在每张卡外加 3 mm 出血和裁切标记。打印时选择 **实际大小 / 100%**。

## 在 Affinity Designer 中修改

1. 用 **文件 → 打开** 导入 PDF。如果导入对话框提供 **优先保留可编辑文本**，可启用该选项。
2. 用文字工具修改英文标题和诗句。用选择工具单独选中黑底矩形换色，或移动、缩放、替换插画。
3. 插画以独立位图保留。需要修改笔触、倒影或视窗内部细节时，编辑原图稿后替换插画。

## 世界系列样稿

两版各 10 页，每页 50 × 100 mm。这组样稿使用 Liberation Serif 和 Z003 替代字体。

- [低饱和版 PDF](examples/black-vellum-10-low-saturation.pdf)
- [原图取色彩色版 PDF](examples/black-vellum-10-original-color.pdf)
