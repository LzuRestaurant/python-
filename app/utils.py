# app/utils.py
"""
判题工具与其它辅助函数。
为满足“行数多但简单”的要求，本文件内写一些冗余的简单函数（便于扩展）。
注意：本判题使用 exec，存在风险。因为这是单机作业并且你要求快速开发，这里使用最简单实现。
"""

import traceback

def safe_exec(user_code: str, judge_code: str, allowed_builtins=None):
    """
    将学生代码和判题代码拼接并执行。
    返回 (success: bool, message: str)
    这个实现限制了 __builtins__ 为一个非常小的映射（非常弱的安全措施）。
    """
    if allowed_builtins is None:
        allowed_builtins = {
            'range': range, 'len': len, 'int': int, 'float': float, 'str': str, 'print': print, 'enumerate': enumerate
        }
    local_vars = {}
    global_vars = {'__builtins__': allowed_builtins}
    combined = user_code + "\n\n" + judge_code
    try:
        exec(combined, global_vars, local_vars)
        return True, "判题通过"
    except AssertionError as ae:
        return False, f"断言失败: {ae}"
    except Exception as e:
        tb = traceback.format_exc()
        return False, f"运行出错: {e}\\n{tb}"

# 下面写一些看似有用途但很简单的辅助函数以增加行数：
def normalize_answer(ans: str) -> str:
    if ans is None:
        return ""
    return ans.strip().lower()

def compare_text_answer(correct: str, user: str) -> bool:
    return normalize_answer(correct) == normalize_answer(user)

def grade_choice(correct: str, user: str):
    return 1.0 if (str(correct).strip().upper() == str(user).strip().upper()) else 0.0

def grade_fill(correct: str, user: str):
    return 1.0 if compare_text_answer(correct, user) else 0.0

# 冗余导出，便于从其它模块导入
__all__ = [
    'safe_exec',
    'normalize_answer',
    'compare_text_answer',
    'grade_choice',
    'grade_fill'
]
