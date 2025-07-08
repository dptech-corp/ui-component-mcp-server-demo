# Theory Expert Agent Package 
# 创建全局实例
from .LightRAGTool import LightRAGTool

lightragTool = LightRAGTool()
lightragTool.initialize()
lightrag_tools = lightragTool.create_tools()

