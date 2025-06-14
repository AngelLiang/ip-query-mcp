import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ip-query")


@mcp.tool(
    description='查询本机公网IP地址信息',
)
def ip_query() -> str:
    response = requests.get(
        "https://qifu-api.baidubce.com/ip/local/geo/v1/district")
    return response.text


@mcp.tool(
    description='查询本机内网IP地址信息'
)
def inner_ip_query() -> str:
    import socket
    try:
        # 获取主机名
        hostname = socket.gethostname()
        # 获取本机内网IP
        ip_address = socket.gethostbyname(hostname)
        # 返回格式化的结果
        result = {
            "status": "success",
            "hostname": hostname,
            "inner_ip": ip_address,
            "message": f"本机内网IP地址为: {ip_address}"
        }
        return str(result)
    except Exception as e:
        return str({"status": "error", "message": f"获取内网IP失败: {str(e)}"})


if __name__ == "__main__":
    mcp.run(transport="stdio")
