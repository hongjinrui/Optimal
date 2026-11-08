# 通信中的优化问题

一本中文入门教材，按“通信模型 → 数学结构 → 求解方法 → 数值核验”组织。当前版本以 XeLaTeX 编译为 61 页，含 10 章正文、2 个附录、4 组可复现实验，以及 14 道自拟习题与参考解答。

## 下载与编译

[下载 LaTeX 源码压缩包](output/latex.zip?raw=true)

解压后选择 **XeLaTeX**，将 `main.tex` 设为主文件。也可以直接使用本仓库的 `latex/` 目录：

```sh
cd latex
latexmk -xelatex main.tex
```

完整 TeX Live 或 Overleaf 需提供 `ctex`、`xeCJK` 等中文支持。全部排版图已包含在包中，编译不需要运行 Python，也无需 BibTeX、Biber、MATLAB、网络或 shell-escape。

## 内容与文件

- `latex/chapters/`：问题分类、凸优化基础、资源分配、波束与估计、数值算法、非凸优化、离散决策、随机与在线优化、实验和习题解答。
- `latex/code/`、`latex/data/`、`latex/figures/`：实验代码、原始数据和图形。
- `latex/SOURCES.txt`：开源检索及复用说明。
- `latex/VALIDATION.txt`：数学、数值和编译验证记录。
- `latex/third_party/`：上游案例、固定版本、归属及完整许可。
- `output/latex.zip`：可独立编译的完整交付包。

## 来源

以 CVX 公有领域案例和 CVXPY Apache-2.0 案例为基础扩充；参考书和论文通过引用标明。数学书写遵循用户指定的 [writing_skills](https://github.com/hongjinrui/writing_skills/blob/main/SKILL.md)。上游文件适用各自许可，详见 `latex/third_party/NOTICE.txt`；本仓库未替用户决定新写正文的公开许可。
