# 《凸优化》中文 LaTeX 译稿

底本为用户上传的 Stephen Boyd、Lieven Vandenberghe 著 *Convex Optimization*（Cambridge University Press，714页 PDF）。译稿按原书顺序逐段翻译，保留章节、公式、例题、图、算法和习题编号。当前中文编译稿为677页，包含11章、3个附录和337道习题。

正文与公式采用可编辑 LaTeX；图形从原书 PDF 矢量提取，图注译为中文。参考文献保留原著录信息。源码中的 `Source PDF page` 注释标明对应底本页码。

## 下载

[LaTeX 完整源码包](output/latex.zip?raw=true) · [中文 PDF](output/convex-optimization-zh.pdf?raw=true)

## 编译

```sh
cd bv-translation
latexmk -xelatex main.tex
```

使用完整 TeX Live 或 Overleaf，选择 **XeLaTeX**，以 `main.tex` 为主文件。所需图形已包含在 `figures/` 中；参考文献直接写在 LaTeX 中，无需 BibTeX、Biber 或额外脚本。

## 文件

- `bv-translation/chapters/`：逐章译稿、三个附录、参考文献与记号表。
- `bv-translation/figures/`：原书图形的矢量裁剪。
- `bv-translation/TRANSLATION.txt`：底本标识与翻译约定。
- `bv-translation/SOURCE-ISSUES.txt`：对照原 PDF 核实的底本疑点。
- `bv-translation/VALIDATION.txt`：覆盖、编号和编译检查记录。

原书作者、出版及版权信息保留于译稿书前页。此前的通信优化教材保留在 `latex/`；本次译稿以 `bv-translation/` 为准。
