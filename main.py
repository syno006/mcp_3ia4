from mcp.server.fastmcp import FastMCP

mcp=FastMCP(name="say hello")
name="yassine"
@mcp.tool()
def say_hello( name):
    """"say hello """
    return(F"Hello from {name}")


if __name__ == "__main__":
    mcp.run(transport="stdio")
