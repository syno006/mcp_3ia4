from fastmcp import FastMCP
mcp=FastMCP(name="calculator")
@mcp.tool()

def add(a:float ,b:float)->float :
    """add two numbers """
    return a+b
@mcp.tool()
def subtract(a:float ,b:float)->float :
    """subtract two numbers """
    return a-b
@mcp.tool()
def multiply(a:float ,b:float)->float :
    """multiply two numbers """
    return a*b
@mcp.tool()
def divide(a:float ,b:float)->float :
    """divide two numbers """
    if b==0:
        return "Error: Division by zero"
    return a/b


if __name__ == "__main__":
    
    mcp.run(transport="http")
