通信中的优化问题——LaTeX 源码包

编译
1. 解压后将 main.tex 设为主文件，使用 XeLaTeX。
2. 本地推荐：latexmk -xelatex main.tex
   或运行两到三次：xelatex -interaction=nonstopmode -halt-on-error main.tex
3. Overleaf：上传整个压缩包，Menu / Settings 中选择 XeLaTeX，主文件 main.tex。
4. 需要现代 TeX Live 的中文支持（ctex、xeCJK、Fandol 字体）及常用宏包
   amsmath、TikZ、PGFPlots、booktabs、hyperref、listings 等。
5. 字体优先使用 Noto CJK；若系统没有 Noto，则自动改用 TeX Live 的 Fandol。
6. 参考文献直接包含在 references.tex，无需 BibTeX 或 Biber。
   图形 PDF 和数据均已随包保存，编译不依赖 Python、网络或外部程序。
   不需要 shell-escape。

内容
chapters/    10章正文、前言与2个附录
figures/     4组实算图形（PDF用于排版，PNG便于查看）
code/        数值实验脚本与依赖版本
data/       实验参数、数据与结果（详见 results.json）
third_party/ 精确版本的上游案例、许可证、NOTICE，以及用户指定写作规则
SOURCES.txt  开源检索与复用说明
VALIDATION.txt 编译与数值检查记录

复现实验（不影响 LaTeX 编译）
python -m venv .venv
.venv/bin/python -m pip install -r code/requirements.txt
.venv/bin/python code/run_experiments.py
Windows 下使用 .venv\Scripts\python.exe 代替 .venv/bin/python。
脚本按其自身文件位置定位输出目录，重新生成图和 data/results.json。

阅读顺序
先读第1章的模型分类和第2章基础，再以第3—4章掌握精确凸化；
第5章介绍数值迭代，第6—8章处理非凸、离散和随机问题。
第9章的实验能独立复现，第10章习题在附录A中有参考解答。

来源与使用
上游 CVX 案例属于公有领域；CVXPY 案例采用 Apache-2.0 许可；
写作规则采用其原 MIT 许可。详情见 third_party/NOTICE.txt 与各原许可证。
新写正文以引用方式介绍已有理论，未复制所参考商业教材的正文或插图。
本包未替用户决定新写正文的公开发布许可证。
