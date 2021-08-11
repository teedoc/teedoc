

import mistune
mistune_version = mistune.__version__.split(".") # 0.8.4, 2.0.0rc1
mistune_version = int(mistune_version[0]) * 10 + int(mistune_version[1]) # 8, 20
if mistune_version >= 20:
    from .renderer_new import create_markdown_parser
else:
    from .renderer_old import create_markdown_parser

