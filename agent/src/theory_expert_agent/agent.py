import os
from typing import Dict, Any, List
from google.adk.agents import Agent, LlmAgent
from google.adk.tools import FunctionTool
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv
from lightrag import LightRAG, QueryParam
from lightrag.utils import EmbeddingFunc
import numpy as np
import logging
from openai import AzureOpenAI
from .prompts import return_instructions_root

load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)

class LightRAGAgent:
    """LightRAG 代理类，管理所有 RAG 工具和初始化"""
    
    def __init__(self):
        self._initialized = False
        self._rag_list = [None, None]
        
        # 工作目录配置
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.working_dir_tescan = os.path.join(self.base_dir, 'work_dickens', 'tescan_dickens')
        self.working_dir_guoyi = os.path.join(self.base_dir, 'work_dickens', 'guoyi_dickens')
        self.working_dir_bopuxue = os.path.join(self.base_dir, 'work_dickens', 'bopuxue_dickens')  
        self.working_dir_xianweixue = os.path.join(self.base_dir, 'work_dickens', 'xianweixue_dickens')  
        self.working_dir_yanshexue = os.path.join(self.base_dir, 'work_dickens', 'yanshe_dickens')  
        
        self.working_dir_list = [
            self.working_dir_tescan, 
            self.working_dir_guoyi, 
            self.working_dir_xianweixue, 
            self.working_dir_bopuxue, 
            self.working_dir_yanshexue
        ]
        
        # 初始化工具和代理
        self._tools = None
        self._theory_expert = None
        self._microscopy_expert = None
        
    async def _llm_model_func(self, prompt, system_prompt=None, history_messages=[], keyword_extraction=False, **kwargs) -> str:
        """LLM 模型函数"""
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        )

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if history_messages:
            messages.extend(history_messages)
        messages.append({"role": "user", "content": prompt})

        chat_completion = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=messages,
            temperature=kwargs.get("temperature", 0),
            top_p=kwargs.get("top_p", 1),
            n=kwargs.get("n", 1),
        )
        return chat_completion.choices[0].message.content

    async def _embedding_func(self, texts: list[str]) -> np.ndarray:
        """嵌入函数"""
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_EMBEDDING_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        )
        embedding = client.embeddings.create(model=os.getenv("AZURE_EMBEDDING_DEPLOYMENT"), input=texts)

        embeddings = [item.embedding for item in embedding.data]
        return np.array(embeddings)
        
    def initialize(self):
        """初始化 RAG 工具"""
        if not self._initialized:
            # 从环境变量读取超参数，提供默认值
            embedding_dimension = int(os.getenv("LIGHTRAG_EMBEDDING_DIMENSION", "1536"))
            max_token_size = int(os.getenv("LIGHTRAG_MAX_TOKEN_SIZE", "8192"))
            
            for i in range(len(self._rag_list)):
                if self._rag_list[i] is None:
                    self._rag_list[i] = LightRAG(
                        working_dir=self.working_dir_list[i],
                        llm_model_func=self._llm_model_func,
                        embedding_func=EmbeddingFunc(
                            embedding_dim=embedding_dimension,
                            max_token_size=max_token_size,
                            func=self._embedding_func,
                        ),
                    )
                    # await self._rag_list[i].initialize_storages()
                    # await initialize_pipeline_status()

            self._initialized = True
            print("LightRAG 代理初始化完成")
    
    def _ensure_initialized(self):
        """确保已初始化"""
        if not self._initialized:
            raise RuntimeError("LightRAG 代理尚未初始化，请先调用 await initialize()")
    
    # 实际的 RAG 查询逻辑
    async def knowledge_retrieval_tescan(self, query: str):
        """
        '此工具从 tescan 知识库中检索与问题相关的文档及参考材料。'
        Args:
            query: 用户提出的问题或查询。
        Returns:
            一个包含检索到的文档片段列表的字典，
            例如: {"status": "success", "context": ""}
                {"status": "not_found", "message": "未找到相关文档。"}
        """
        print(f"--- 工具：knowledge_retrieval_tool_by_lightrag_tescan 被调用，查询：{query} ---")
        try:
            self.initialize()
            
            llm_response = await self._rag_list[0].aquery(query, param=QueryParam(mode="hybrid"))
            return {
                "status": "success",
                "llm_response": llm_response,
            }
        except Exception as e:
            print(f"知识检索工具出错: {e}")
            return {
                "status": "error",
                "error_message": f"检索文档时发生错误: {str(e)}"
            }
    
    async def knowledge_retrieval_guoyi(self, query: str):
        """
        此工具从TEM样品制备流程与国仪软件使用相关的文档及参考材料。'
        Args:
            query: 用户提出的问题或查询。
        Returns:
            一个包含检索到的文档片段列表的字典，
            例如: {"status": "success", "context": ""}
                {"status": "not_found", "message": "未找到相关文档。"}
        """
        print(f"--- 工具：knowledge_retrieval_tool_by_lightrag_guoyi 被调用，查询：{query} ---")
        try:
            self.initialize()
            llm_response = await self._rag_list[1].aquery(query, param=QueryParam(mode="hybrid"))
            return {
                "status": "success",
                "llm_response": llm_response,
            }
        except Exception as e:
            print(f"知识检索工具出错: {e}")
            return {
                "status": "error",
                "error_message": f"检索文档时发生错误: {str(e)}"
            }
    
    def knowledge_retrieval_xianweixue(self, query: str):
        """
        此工具从显微成像，而且涉及到各类粒子的显微学相关的文档及参考材料。'
        Args:
            query: 用户提出的问题或查询。
        Returns:
            一个包含检索到的文档片段列表的字典，
            例如: {"status": "success", "context": ""}
                {"status": "not_found", "message": "未找到相关文档。"}
        """
        print(f"--- knowledge_retrieval_tool_by_lightrag_xianweixue 被调用，查询：{query} ---")
        try:
            self.initialize()
            llm_response = self._rag_list[2].query(query, param=QueryParam(mode="hybrid"))
            return {
                "status": "success",
                "llm_response": llm_response,
            }
        except Exception as e:
            print(f"知识检索工具出错: {e}")
            return {
                "status": "error",
                "error_message": f"检索文档时发生错误: {str(e)}"
            }
    
    def knowledge_retrieval_bopuxue(self, query: str):
        """
        此工具从谱学，而且涉及到各类粒子的谱学知识相关的文档及参考材料。'
        Args:
            query: 用户提出的问题或查询。
        Returns:
            一个包含检索到的文档片段列表的字典，
            例如: {"status": "success", "context": ""}
                {"status": "not_found", "message": "未找到相关文档。"}
        """
        print(f"--- knowledge_retrieval_tool_by_lightrag_bopuxue 被调用，查询：{query} ---")
        try:
            self.initialize()
            llm_response = self._rag_list[3].query(query, param=QueryParam(mode="hybrid"))
            return {
                "status": "success",
                "llm_response": llm_response,
            }
        except Exception as e:
            print(f"知识检索工具出错: {e}")
            return {
                "status": "error",
                "error_message": f"检索文档时发生错误: {str(e)}"
            }
    
    def knowledge_retrieval_yanshexue(self, query: str):
        """
        此工具从衍射，而且涉及到各类粒子的衍射知识相关的文档及参考材料。'
        Args:
            query: 用户提出的问题或查询。
        Returns:
            一个包含检索到的文档片段列表的字典，
            例如: {"status": "success", "context": ""}
                {"status": "not_found", "message": "未找到相关文档。"}
        """
        print(f"--- knowledge_retrieval_tool_by_lightrag_yanshexue 被调用，查询：{query} ---")
        try:
            self.initialize()
            llm_response = self._rag_list[4].query(query, param=QueryParam(mode="hybrid"))
            return {
                "status": "success",
                "llm_response": llm_response,
            }
        except Exception as e:
            print(f"知识检索工具出错: {e}")
            return {
                "status": "error",
                "error_message": f"检索文档时发生错误: {str(e)}"
            }

    def _create_tools(self) -> List[FunctionTool]:
        """创建 ADK 工具列表"""
        if self._tools is None:
            self._tools = [
                FunctionTool(self.knowledge_retrieval_tescan),
                FunctionTool(self.knowledge_retrieval_guoyi),
                # FunctionTool(self.knowledge_retrieval_xianweixue),
                # FunctionTool(self.knowledge_retrieval_bopuxue),
                # FunctionTool(self.knowledge_retrieval_yanshexue),
            ]
        return self._tools

    def create_theory_expert(self) -> LlmAgent:
        if self._theory_expert is None:
            # tools = self._create_tools()
            # theory_tools = [tools[2], tools[3], tools[4]]  # 显微学、波谱学、衍射学工具
            self._theory_expert = LlmAgent(
                model=LiteLlm(
                    model=os.getenv("LLM_MODEL", "gemini/gemini-1.5-flash"),
                    api_key=os.getenv("OPENAI_API_KEY"),
                    api_base=os.getenv("OPENAI_API_BASE_URL")),
                name="theory_expert",
                tools=[],
                description="领域理论专家子代理，专门处理显微学、衍射与成像技术、波谱学与能谱学等领域的理论问题和概念解释。",
                instruction="""你是领域理论专家子代理。你的专业领域包括：
1. 处理显微学理论相关问题和概念解释
2. 解答衍射与成像技术的基础原理和应用
3. 提供波谱学与能谱学的理论知识和解释
4. 解答材料表征领域的前沿理论问题

请根据用户的理论问题，提供严谨、准确的科学解释和理论知识。""",
            )
        return self._theory_expert

    def create_microscopy_expert(self) -> LlmAgent:
        """创建电镜操作专家代理"""
        if self._microscopy_expert is None:
            tools = self._create_tools()
            microscopy_tools = [tools[0], tools[1]]  # TESCAN、国仪工具
            self._microscopy_expert = LlmAgent(
                model=LiteLlm(
                    model=os.getenv("LLM_MODEL", "gemini/gemini-1.5-flash"),
                    api_key=os.getenv("OPENAI_API_KEY"),
                    api_base=os.getenv("OPENAI_API_BASE_URL")),
                tools=microscopy_tools,
                name="microscopy_expert",
                description="电镜操作专家子代理，专门处理各种型号电镜的具体操作指导、设备维护、样品制备和成像参数优化等问题。",
                instruction=return_instructions_root("microscopy_expert")
            )
        return self._microscopy_expert









 