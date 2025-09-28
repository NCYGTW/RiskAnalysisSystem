"""
主程序
"""

import os
import json
import time
import logging
from typing import Dict, List
from datetime import datetime  
from RiskFormulaParserAgent.agent import RiskFormulaParserAgent
from DataValidationAgent.agent import DataValidationAgent
from ReportGenerationAgent.agent import ReportGenerationAgent
from ForumEngine.monitor import ForumEngine

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RiskAnalysisSystem:
    """主类"""
    
    def __init__(self):
        """系统初始化"""
        self.forum_engine = ForumEngine()
        self.formula_parser_agent = RiskFormulaParserAgent()
        self.data_validation_agent = DataValidationAgent()
        self.report_generation_agent = ReportGenerationAgent()
        
        print("初始化风险分析系统")
    
    def run_full_analysis(self, risk_data_file: str = "data/risk_warning.json"):
        """
        运行系统
        
        Args:
            risk_data_file: 风险数据文件路径
        """
        print("开始风险分析...")
        
        try:
            # Step 1: 加载风险数据
            risk_data = self._load_risk_data(risk_data_file)
            if not risk_data:
                print("未能加载风险数据")
                return
            
            #Step 2: 处理风险数据
            analysis_results = self._process_risks_one_by_one(risk_data)
            
            # Step 3: 生成报告
            report_content = self._generate_final_report(analysis_results)
            
            print("风险分析完成")
            return report_content
            
        except Exception as e:
            print(f"运行风险分析时发生错误: {str(e)}")
            return None

    def _process_risks_one_by_one(self, risk_data: Dict) -> List[Dict]:
        """逐个处理风险"""
        print("开始逐个处理风险...")
        
        results = []
        generated_codes = []
        total_processed = 0
        
        for company_name, company_risks in risk_data.items():
            print(f"\n处理公司: {company_name}")
            
            for risk_category, risk_list in company_risks.items():
                print(f"  处理风险类别: {risk_category}")
                
                for risk_item in risk_list:
                    risk_description = risk_item.get('具体风险和模型公式编号', '')
                    model_items = risk_item.get('模型涉及项目', [])
                    
                    if risk_description and model_items:
                        total_processed += 1
                        print(f"\n  [{total_processed}] 处理风险: {risk_description[:50]}...")
                        
                        validation_data = {
                            "company_name": company_name,
                            "model_items": model_items
                        }
                        
                        # 1. 解析风险公式
                        code = self.formula_parser_agent.parse_risk_formula(risk_description, model_items)
                        
                        if code:
                            # 将生成的代码添加到列表中
                            generated_codes.append({
                                'company_name': company_name,
                                'risk_category': risk_category,
                                'risk_description': risk_description,
                                'python_code': code
                            })
                            print(f"    ✅ 成功解析风险公式")
                            
                            # 打印生成的Python代码
                            print(f"\n    📝 生成的Python代码:")
                            print("    " + "="*70)
                            # 按行打印代码，并添加缩进
                            for line in code.split('\n'):
                                print(f"    {line}")
                            print("    " + "="*70)
                            
                            # 2. 验证风险 - 使用模型涉及项目数据
                            print(f"    🧪 开始验证风险...")
                            is_risk = self.data_validation_agent.validate_risk(code, validation_data)
                            
                            # 3. 如果第一次验证结果为False，即无风险，则重新调用LLM生成代码进行验证
                            if not is_risk:
                                print(f"    🔄 第一次验证结果为无风险，重新生成验证代码进行确认...")
                                # 再次调用LLM生成代码
                                retry_code = self.formula_parser_agent.parse_risk_formula(risk_description, model_items)
                                
                                if retry_code:
                                    # 将重试生成的代码也添加到列表中
                                    retry_entry = {
                                        'company_name': company_name,
                                        'risk_category': risk_category,
                                        'risk_description': risk_description,
                                        'python_code': retry_code,
                                        'is_retry': True
                                    }
                                    generated_codes.append(retry_entry)
                                    
                                    # 打印重试生成的Python代码
                                    print(f"\n    📝 重试生成的Python代码:")
                                    print("    " + "="*70)
                                    for line in retry_code.split('\n'):
                                        print(f"    {line}")
                                    print("    " + "="*70)
                                    
                                    # 再次验证
                                    print(f"    🧪 开始第二次验证...")
                                    retry_is_risk = self.data_validation_agent.validate_risk(retry_code, validation_data)
                                    
                                    # 如果第二次结果仍然为False，保留此风险项并标记为无风险
                                    if not retry_is_risk:
                                        print(f"    ✅ 两次验证结果均为无风险，确认结果为无风险")
                                        # 使用第二次验证的结果
                                        is_risk = False
                                        code = retry_code
                                    else:
                                        is_risk = retry_is_risk
                                        code = retry_code
                                else:
                                    print(f"    ❌ 重试生成代码失败，使用第一次的验证结果")
                            
                            # 3. 将结果添加到列表中
                            result = {
                                'company_name': company_name,
                                'risk_category': risk_category,
                                'risk_description': risk_description,
                                'python_code': code,
                                'is_risk': is_risk
                            }
                            results.append(result)
                            
                            # 4. 打印验证结果
                            print(f"\n📊 验证结果 - {company_name} - {risk_category}:")
                            print(f"   风险描述: {risk_description[:80]}{'...' if len(risk_description) > 80 else ''}")
                            print(f"   验证结论: {'🔴 存在风险' if is_risk else '🟢 无风险'}")
                            print("="*80)
                        else:
                            print(f"    ❌ 解析失败")
                            results.append({
                                'company_name': company_name,
                                'risk_category': risk_category,
                                'risk_description': risk_description,
                                'python_code': '',
                                'is_risk': False,
                                'error': '解析失败'
                            })
                        
                        # 在处理每个风险后添加延迟2秒，避免API速率限制
                        time.sleep(2)  
        
        # 保存生成的代码到文件
        self._save_generated_codes(generated_codes)
        
        print(f"\n风险处理完成，共处理 {total_processed} 个风险")
        return results
    
    def _load_risk_data(self, risk_data_file: str) -> Dict:
        """加载风险数据"""
        print("加载风险数据...")
        
        try:
            full_path = os.path.join(os.path.dirname(__file__), risk_data_file)
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                risk_data = data.get('data', {})
                print(f"成功加载风险数据，包含 {len(risk_data)} 个公司")
                return risk_data
        except Exception as e:
            print(f"加载风险数据时出错: {str(e)}")
            return {}
    
    def _save_generated_codes(self, generated_codes: List[Dict]):
        """保存生成的代码到文件"""
        try:
            output_dir = "outputs"
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_risk_codes_{timestamp}.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(generated_codes, f, ensure_ascii=False, indent=2)
            
            print(f"生成的风险公式代码已保存到: {filepath}")
        except Exception as e:
            print(f"保存生成的代码时出错: {str(e)}")
    
    def _generate_final_report(self, analysis_results: List[Dict]) -> str:
        """生成最终报告"""
        print("生成最终报告...")
        
        # 使用ReportGenerationAgent生成报告
        report_content = self.report_generation_agent.generate_report(analysis_results)
        
        print("最终报告生成完成")
        return report_content

def main():
    """主函数"""
    # 启动ForumEngine监控
    forum_engine = ForumEngine()
    forum_engine.start_monitoring()
    
    # 系统初始化
    system = RiskAnalysisSystem()
    
    # 系统运行
    report = system.run_full_analysis()
    
    # 停止ForumEngine监控
    forum_engine.stop_monitoring()
    
    if report:
        print("风险分析完成，报告已生成")
    else:
        print("风险分析失败")

if __name__ == "__main__":
    main()