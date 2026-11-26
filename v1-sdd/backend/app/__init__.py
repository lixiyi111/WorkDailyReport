"""智能日报生成器 v1（SDD）后端应用包。"""

import sys

if sys.version_info < (3, 12):  # noqa: UP036
    raise RuntimeError(
        "本项目需要 Python 3.12+。请先执行 `conda activate work_daily` 再启动服务；"
        f"当前解释器为 {sys.version.split()[0]}。"
    )
