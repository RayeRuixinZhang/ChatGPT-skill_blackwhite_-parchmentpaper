# 排版与导出

用 Python 3.10+，安装 Pillow、ReportLab 和 fonttools。将图稿准备为 RGB 或带透明度的 PNG；其他常见图片格式也可读取。使用原尺寸图层和无损 PNG，保留透明度。导出器以原像素尺寸无损嵌入两版插画。图稿路径相对 JSON 清单解析。

```json
{
  "cards": [
    {
      "image": "art/swan-low-saturation.png",
      "image_color": "art/swan-original-color.png",
      "image_box": [5, 12, 40, 53],
      "title": "Winter’s End",
      "poem": "The snow melts, the ice thaws, and swans arrive.",
      "text_box": [6, 73, 38, 19],
      "align": "left"
    }
  ]
}
```

`image` 指向低饱和图稿，`image_color` 指向从同页原图取色的彩色图稿。两张图使用尺寸一致的透明画布、相同的主体位置和边缘。`--palette both` 要求每张卡都提供两个文件。

坐标为毫米，以成品左上角为原点。两个框均为 `[x, y, 宽, 高]`。图片等比放进图框并居中，文字在字框中按词换行。默认居左，也可以用 `"center"`。可用 `title_pt` 和 `poem_pt` 指定字号，默认 10 pt 和 7.25 pt。导出器会报告超出字框和缺字，请调整构图或换行。用户指定文案时保留措辞和标点。

```bash
python scripts/build_pdf.py cards.json cards-editable.pdf --palette both \
  --title-font /path/to/times.ttf \
  --poem-font /path/to/LHANDW.TTF
```

该命令生成 `cards-editable-low-saturation.pdf` 和 `cards-editable-original-color.pdf`。也可用 `--palette low-saturation` 或 `--palette original-color` 只输出一个版本到指定文件。省略 `--palette` 时沿用原有的 `image` 字段，可直接导出旧清单。

默认每页一张 50 × 100 mm 成品。用 `--size-mm 宽 高` 改尺寸。用 `--a4` 输出 A4 版，每张卡有 3 mm 出血和裁切标记。若装有 Fontconfig，可以省略字体参数，由脚本尝试按名称查找。脚本校验字体的内部名称并检查是否允许以可编辑方式嵌入。请勿随仓库分发授权字体或用户素材。

对照两份 PDF 的页面尺寸、顺序、图像位置和文字。用 `pdffonts` 核对嵌入字体，用 `pdftotext -layout` 核对原文，用 `pdftoppm -r 160 -png` 渲染检查。Affinity Designer 中用「文件 → 打开」导入 PDF。若导入对话框有「优先保留可编辑文本」和「将多行文本组合到文本框」，可按编辑需要启用。编辑电脑也要安装这两款字体。独立位图可以移动、缩放和替换，图稿内部笔触仍是像素。

## 细节修复与检查

1. 用最高质量的原图或原尺寸透明图层作修复底稿。两版共用同一构图、比例和透明轮廓。从源文件核对模糊、褪色或失真的区域，只恢复有依据的纹理和色彩。原始细节有限时，优先采用清晰源图，避免靠插值像素或生成纹理补足精度。
2. 在纯黑底和放大视图检查边缘。定点处理游离杂点、背景残留、透明针孔和误叠造成的接缝。保留真实遮挡、反光断点、枝叶空隙、船索和自然笔触。保持人物五官及比例、发型、服装与配饰、姿态和表情。二维画稿直接检查轮廓和透明图层。
3. 在原像素上轻量增强局部亮度细节和中间调，按材质分别核对皮肤、布料、石材、木纹和水面。保留原光向和各版本的色彩关系。每轮以原图和上次通过检查的版本为对照，同时检查成品实际大小和放大细节。保留清晰且忠实于原图的改进，发现白边、噪点、色偏或形态变化就减弱或撤回对应调整。
4. 按插画在 PDF 中的实际置入宽高计算有效分辨率。将横纵各自的像素数除以对应的放置英寸数，取较低值。两版每张都须达到 300 ppi。源图能提供更高有效分辨率时，保留原有像素。脚本对不达标的图稿会给出色版、卡片编号、实际 ppi 和放置尺寸，并在写入任何 PDF 前中止。可用 `pdfimages -list` 复核最终 PDF 的 `x-ppi` 与 `y-ppi`，再用高倍率渲染检查细线、边缘与局部纹理。报告最终各页的有效 ppi 范围及源图仍然存在的限制。

- [Lucida Handwriting 字体资料](https://learn.microsoft.com/en-us/typography/font-list/lucida-handwriting)
