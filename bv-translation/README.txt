《凸优化》中文 LaTeX 译稿

Stephen Boyd、Lieven Vandenberghe 原著。
底本为用户上传的714页 bv_cvxbook.pdf；中文编译稿677页。
正文11章、附录3章，公式、例题、算法、图和习题沿用原书编号。

编译：在本目录运行 latexmk -xelatex main.tex。
Overleaf：上传整个源码包，选择XeLaTeX，将main.tex设为主文件。
需完整TeX Live的ctex/xeCJK和常用数学、图表宏包。
中文字体优先Noto CJK，无Noto时自动使用Fandol。
图形PDF已附，无需Python、网络、BibTeX、Biber或shell-escape。

chapters/         可编辑正文、公式、参考文献和记号表
figures/          原书图形矢量文件，轴名和图注已中文化
TRANSLATION.txt   底本标识、翻译约定及主要术语
SOURCE-ISSUES.txt 原PDF公式/引用的对照记录
VALIDATION.txt    本次核对与编译记录
