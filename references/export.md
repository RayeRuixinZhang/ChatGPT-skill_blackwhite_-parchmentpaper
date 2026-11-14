# 排版与导出

用 Python 3.10+，安装 Pillow、ReportLab 和 fonttools。将图稿准备为 RGB 或带透明度的 PNG；其他常见图片格式也可读取。建议最终放置尺寸下至少 300 ppi。图稿路径相对 JSON 清单解析。

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

- [Lucida Handwriting 字体资料](https://learn.microsoft.com/en-us/typography/font-list/lucida-handwriting)
