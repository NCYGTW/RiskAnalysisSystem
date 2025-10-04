"""
数据验证工具
将 DataValidationAgent 的非LLM节点逻辑重构为工具函数：数据提取、代码执行、结果验证与一体化流水线。
"""

from typing import Any, Dict


def extract_data(data_dict: Dict[str, Any]) -> Dict[str, Any]:
    """从完整数据字典中提取验证所需数据（等价于 DataExtractionNode.run）。"""
    company_name = data_dict.get("company_name", "")
    model_items = data_dict.get("model_items", [])

    extracted_data: Dict[str, Any] = {
        "company_name": company_name,
        "model_items": model_items,
        "model_data_by_name_type": {},
    }

    # 构建索引：name_type -> item
    for item in model_items:
        name = item.get("项目名称", "")
        item_type = item.get("类型", "")
        key = f"{name}_{item_type}"
        extracted_data["model_data_by_name_type"][key] = item

    return extracted_data


def execute_code(python_code: str, extracted_data: Dict[str, Any]) -> Any:
    """执行生成的 Python 代码并返回结果（等价于 CodeExecutionNode.run）。

    要求代码中定义 `check_risk(extracted_data)` 函数。
    """
    try:
        safe_globals: Dict[str, Any] = {
            "__builtins__": {
                "abs": abs,
                "min": min,
                "max": max,
                "round": round,
                "len": len,
                "sum": sum,
                "any": any,
                "all": all,
                "bool": bool,
                "int": int,
                "float": float,
                "str": str,
                "ValueError": ValueError,
                "KeyError": KeyError,
                "TypeError": TypeError,
                "IndexError": IndexError,
                "ZeroDivisionError": ZeroDivisionError,
                "AttributeError": AttributeError,
                "Exception": Exception,
                "__import__": __import__,
            }
        }

        # 执行代码
        exec(python_code, safe_globals)

        if "check_risk" in safe_globals:
            return safe_globals["check_risk"](extracted_data)
        raise Exception("代码中未找到check_risk函数")

    except Exception as e:
        print(f"执行代码时出错: {str(e)}")
        return None


def validate_result(execution_result: Any) -> Dict[str, Any]:
    """验证执行结果（等价于 ResultValidationNode.run）。"""
    is_risk = isinstance(execution_result, bool) and execution_result
    return {"is_risk": is_risk, "execution_result": execution_result}


def run_validation_pipeline(python_code: str, data_dict: Dict[str, Any]) -> Dict[str, Any]:
    """一体化：提取数据 -> 执行代码 -> 验证结果。"""
    extracted = extract_data(data_dict)
    exec_result = execute_code(python_code, extracted)
    return validate_result(exec_result)