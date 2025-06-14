# IP查询MCP工具

简易的IP查询MCP工具，基于deepseek大模型，用于学习如何让大模型调用MCP工具

## 项目说明

- ip_query_mcp.py：ip查询MCP
- main.py：大模型调用该MCP工具的示例，可以使用大模型通过function_call功能，调用MCP的接口

# 如何运行

设置deepseek的apikey

```
uv run main.py
```

启动之后，在终端根据提示输入问题，比如查询公网IP或内网IP，大模型会自动调用相关工具查询，最后根据查询结果回答问题。

