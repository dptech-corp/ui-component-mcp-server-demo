"""
基于 Opik 的大模型输出评估模块
用于检测幻觉、评估准确性和相关性
"""

import os
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from opik import track, Opik
from opik.evaluation.metrics import (
    HallucinationMetric, 
    AnswerRelevanceMetric, 
    ContextPrecisionMetric,
    ContextRecallMetric,
    ContainsMetric,
    RegexMatchMetric
)
from opik.evaluation import evaluate
from dotenv import load_dotenv

load_dotenv()

@dataclass
class EvaluationResult:
    """评估结果数据类"""
    hallucination_score: float
    answer_relevance_score: float
    context_precision_score: float
    context_recall_score: float
    contains_score: float
    overall_score: float
    evaluation_details: Dict[str, Any]

class ModelEvaluator:
    """大模型输出评估器"""
    
    def __init__(self):
        """初始化评估器"""
        self.opik_client = Opik()
        self.metrics = {
            'hallucination': HallucinationMetric(),
            'answer_relevance': AnswerRelevanceMetric(),
            'context_precision': ContextPrecisionMetric(),
            'context_recall': ContextRecallMetric(),
            'contains': ContainsMetric(),
        }
        
    @track
    async def evaluate_single_response(
        self,
        user_question: str,
        model_response: str,
        ground_truth: str,
        context: Optional[str] = None
    ) -> EvaluationResult:
        """
        评估单个模型响应
        
        Args:
            user_question: 用户问题
            model_response: 模型响应
            ground_truth: 标准答案
            context: 检索到的上下文（可选）
            
        Returns:
            EvaluationResult: 评估结果
        """
        print(f"开始评估模型响应...")
        print(f"问题: {user_question}")
        print(f"模型响应: {model_response[:100]}...")
        print(f"标准答案: {ground_truth[:100]}...")
        
        # 计算各项指标
        scores = {}
        
        # 1. 幻觉检测
        if context:
            hallucination_score = self.metrics['hallucination'].score(
                input=user_question,
                output=model_response,
                context=context
            )
        else:
            # 如果没有上下文，使用标准答案作为参考
            hallucination_score = self.metrics['hallucination'].score(
                input=user_question,
                output=model_response,
                context=ground_truth
            )
        scores['hallucination'] = hallucination_score
        
        # 2. 答案相关性
        answer_relevance_score = self.metrics['answer_relevance'].score(
            input=user_question,
            output=model_response,
            context=ground_truth
        )
        scores['answer_relevance'] = answer_relevance_score
        
        # 3. 上下文精确度（如果有上下文）
        if context:
            context_precision_score = self.metrics['context_precision'].score(
                input=user_question,
                output=model_response,
                context=context
            )
            scores['context_precision'] = context_precision_score
        else:
            context_precision_score = 0.0
            scores['context_precision'] = context_precision_score
            
        # 4. 上下文召回率（如果有上下文）
        if context:
            context_recall_score = self.metrics['context_recall'].score(
                input=user_question,
                output=model_response,
                context=context
            )
            scores['context_recall'] = context_recall_score
        else:
            context_recall_score = 0.0
            scores['context_recall'] = context_recall_score
            
        # 5. 内容包含度
        contains_score = self.metrics['contains'].score(
            input=user_question,
            output=model_response,
            context=ground_truth
        )
        scores['contains'] = contains_score
        
        # 计算综合得分
        overall_score = self._calculate_overall_score(scores)
        
        result = EvaluationResult(
            hallucination_score=hallucination_score,
            answer_relevance_score=answer_relevance_score,
            context_precision_score=context_precision_score,
            context_recall_score=context_recall_score,
            contains_score=contains_score,
            overall_score=overall_score,
            evaluation_details=scores
        )
        
        print(f"评估完成，综合得分: {overall_score:.3f}")
        return result
    
    def _calculate_overall_score(self, scores: Dict[str, float]) -> float:
        """
        计算综合得分
        
        Args:
            scores: 各项指标得分
            
        Returns:
            float: 综合得分
        """
        # 权重配置
        weights = {
            'hallucination': 0.3,      # 幻觉检测权重最高
            'answer_relevance': 0.25,  # 答案相关性
            'context_precision': 0.15, # 上下文精确度
            'context_recall': 0.15,    # 上下文召回率
            'contains': 0.15           # 内容包含度
        }
        
        overall_score = 0.0
        for metric, score in scores.items():
            if metric in weights:
                overall_score += score * weights[metric]
                
        return overall_score
    
    @track
    async def evaluate_batch_responses(
        self,
        test_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        批量评估模型响应
        
        Args:
            test_cases: 测试用例列表，每个包含:
                - user_question: 用户问题
                - model_response: 模型响应
                - ground_truth: 标准答案
                - context: 上下文（可选）
                
        Returns:
            Dict: 批量评估结果
        """
        print(f"开始批量评估 {len(test_cases)} 个测试用例...")
        
        results = []
        total_scores = {
            'hallucination': 0.0,
            'answer_relevance': 0.0,
            'context_precision': 0.0,
            'context_recall': 0.0,
            'contains': 0.0,
            'overall': 0.0
        }
        
        for i, test_case in enumerate(test_cases):
            print(f"评估测试用例 {i+1}/{len(test_cases)}...")
            
            result = await self.evaluate_single_response(
                user_question=test_case['user_question'],
                model_response=test_case['model_response'],
                ground_truth=test_case['ground_truth'],
                context=test_case.get('context')
            )
            
            results.append({
                'test_case_id': i,
                'user_question': test_case['user_question'],
                'model_response': test_case['model_response'],
                'ground_truth': test_case['ground_truth'],
                'context': test_case.get('context'),
                'evaluation_result': result
            })
            
            # 累加得分
            total_scores['hallucination'] += result.hallucination_score
            total_scores['answer_relevance'] += result.answer_relevance_score
            total_scores['context_precision'] += result.context_precision_score
            total_scores['context_recall'] += result.context_recall_score
            total_scores['contains'] += result.contains_score
            total_scores['overall'] += result.overall_score
        
        # 计算平均得分
        num_cases = len(test_cases)
        average_scores = {
            metric: score / num_cases 
            for metric, score in total_scores.items()
        }
        
        # 生成评估报告
        report = {
            'summary': {
                'total_test_cases': num_cases,
                'average_scores': average_scores,
                'performance_analysis': self._analyze_performance(average_scores)
            },
            'detailed_results': results
        }
        
        print(f"批量评估完成，平均综合得分: {average_scores['overall']:.3f}")
        return report
    
    def _analyze_performance(self, scores: Dict[str, float]) -> Dict[str, str]:
        """
        分析性能表现
        
        Args:
            scores: 平均得分
            
        Returns:
            Dict: 性能分析结果
        """
        analysis = {}
        
        # 幻觉检测分析
        if scores['hallucination'] >= 0.8:
            analysis['hallucination'] = "优秀 - 几乎没有幻觉"
        elif scores['hallucination'] >= 0.6:
            analysis['hallucination'] = "良好 - 幻觉较少"
        elif scores['hallucination'] >= 0.4:
            analysis['hallucination'] = "一般 - 存在一定幻觉"
        else:
            analysis['hallucination'] = "较差 - 幻觉较多"
            
        # 答案相关性分析
        if scores['answer_relevance'] >= 0.8:
            analysis['answer_relevance'] = "优秀 - 答案高度相关"
        elif scores['answer_relevance'] >= 0.6:
            analysis['answer_relevance'] = "良好 - 答案较为相关"
        elif scores['answer_relevance'] >= 0.4:
            analysis['answer_relevance'] = "一般 - 答案相关性一般"
        else:
            analysis['answer_relevance'] = "较差 - 答案相关性较低"
            
        # 综合表现分析
        if scores['overall'] >= 0.8:
            analysis['overall'] = "优秀 - 整体表现优异"
        elif scores['overall'] >= 0.6:
            analysis['overall'] = "良好 - 整体表现良好"
        elif scores['overall'] >= 0.4:
            analysis['overall'] = "一般 - 整体表现一般"
        else:
            analysis['overall'] = "较差 - 需要改进"
            
        return analysis
    
    def create_test_dataset(self, dataset_name: str, test_cases: List[Dict[str, Any]]) -> None:
        """
        在 Opik 中创建测试数据集
        
        Args:
            dataset_name: 数据集名称
            test_cases: 测试用例列表
        """
        try:
            # 创建数据集
            dataset = self.opik_client.create_dataset(
                name=dataset_name,
                description=f"理论专家代理评估数据集 - {dataset_name}"
            )
            
            # 添加测试用例
            for test_case in test_cases:
                dataset.add_item(
                    input={
                        'user_question': test_case['user_question'],
                        'ground_truth': test_case['ground_truth'],
                        'context': test_case.get('context', '')
                    },
                    output=test_case['model_response']
                )
                
            print(f"成功创建数据集: {dataset_name}")
            
        except Exception as e:
            print(f"创建数据集失败: {e}")

# 使用示例
async def main():
    """使用示例"""
    evaluator = ModelEvaluator()
    
    # 示例测试用例
    test_cases = [
        {
            'user_question': 'TESCAN 显微镜的安全操作规程是什么？',
            'model_response': 'TESCAN 显微镜的安全操作规程包括：操作前需检查电源连接，佩戴防护装备，确保工作环境通风良好。',
            'ground_truth': 'TESCAN 显微镜的安全操作规程包括：操作前需检查电源连接，佩戴防护装备，确保工作环境通风良好。',
            'context': 'TESCAN 显微镜操作手册第3章安全规程：1. 检查电源连接 2. 佩戴防护装备 3. 确保通风'
        },
        {
            'user_question': '什么是 SEM 成像原理？',
            'model_response': 'SEM 成像原理是通过电子束扫描样品表面，收集二次电子和背散射电子形成图像。',
            'ground_truth': 'SEM 成像原理是通过电子束扫描样品表面，收集二次电子和背散射电子形成图像。',
            'context': 'SEM 成像原理：电子束扫描样品表面，收集二次电子和背散射电子形成图像。'
        }
    ]
    
    # 批量评估
    report = await evaluator.evaluate_batch_responses(test_cases)
    
    # 打印结果
    print("\n=== 评估报告 ===")
    print(f"测试用例数量: {report['summary']['total_test_cases']}")
    print(f"平均综合得分: {report['summary']['average_scores']['overall']:.3f}")
    print(f"幻觉检测得分: {report['summary']['average_scores']['hallucination']:.3f}")
    print(f"答案相关性得分: {report['summary']['average_scores']['answer_relevance']:.3f}")
    
    print("\n=== 性能分析 ===")
    for metric, analysis in report['summary']['performance_analysis'].items():
        print(f"{metric}: {analysis}")

if __name__ == "__main__":
    asyncio.run(main()) 