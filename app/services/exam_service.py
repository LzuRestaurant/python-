# app/services/exam_service.py
"""
ExamService
-----------
负责考试流程的高级封装：生成试卷、评分、记录、导出成绩、模拟考试等。
实现较多占行但逻辑简单的函数，便于作业需要。
"""

from typing import List, Dict, Any, Optional
from ..models import ExamRecord, Question, User
from .. import db
from .question_service import QuestionService
from .analytics_service import AnalyticsService
import datetime
import json
import random

class ExamService:
    """考试服务：处理考试流程与考试记录。"""

    def __init__(self):
        self.qs = QuestionService()
        self.analytics = AnalyticsService()
        # 默认每次试卷题量
        self.default_paper_size = 10

    def create_paper(self, size: int = None, qtypes: Optional[List[str]] = None) -> List[Question]:
        """生成一张试卷（Question 对象列表）。"""
        if size is None:
            size = self.default_paper_size
        return self.qs.random_questions(size, qtypes)

    def grade_submission(self, answers: Dict[int, Any]) -> Dict[str, Any]:
        """
        对前端提交的数据进行评分。
        answers: dict mapping question_id -> { 'type': 'choice'/'fill'/'code', 'answer': 'A' or code... }
        返回评分结果字典，包含 score、total、detail 列表等。
        """
        total = 0.0
        score = 0.0
        details = []
        for qid_str, payload in answers.items():
            # qid 可能是字符串，处理
            try:
                qid = int(qid_str)
            except Exception:
                continue
            q = Question.query.get(qid)
            if not q:
                details.append({'qid': qid, 'ok': False, 'reason': '题目不存在'})
                continue
            qtype = q.qtype
            total += 1.0
            got = payload.get('answer')
            if qtype == 'choice':
                if (str(got).strip().upper() == (q.answer or '').strip().upper()):
                    score += 1.0
                    details.append({'qid': qid, 'ok': True, 'type': 'choice'})
                else:
                    details.append({'qid': qid, 'ok': False, 'type': 'choice', 'expected': q.answer, 'got': got})
            elif qtype == 'fill':
                if str(got).strip().lower() == (q.answer or '').strip().lower():
                    score += 1.0
                    details.append({'qid': qid, 'ok': True, 'type': 'fill'})
                else:
                    details.append({'qid': qid, 'ok': False, 'type': 'fill', 'expected': q.answer, 'got': got})
            elif qtype == 'code':
                # 简单执行判题模板与学生代码拼接（注意安全）
                # 这里我们用一个非常简化的 sandbox（与 utils.safe_exec 类似）：
                user_code = got or ''
                judge = q.judge_template or ''
                ok, msg = self._exec_code(user_code, judge)
                if ok:
                    score += 1.0
                details.append({'qid': qid, 'ok': ok, 'type': 'code', 'msg': msg})
            else:
                details.append({'qid': qid, 'ok': False, 'reason': '未知题型'})
        return {'score': score, 'total': total, 'details': details}

    def _exec_code(self, user_code: str, judge_code: str):
        """内部非常简单的运行器，返回 (ok: bool, msg: str)。"""
        # 限制内置函数（非常弱的沙箱）
        safe_builtins = {'range': range, 'len': len, 'int': int, 'float': float, 'str': str, 'print': print, 'enumerate': enumerate}
        g = {'__builtins__': safe_builtins}
        l = {}
        combined = user_code + "\n\n" + judge_code
        try:
            exec(combined, g, l)
            return True, "通过"
        except AssertionError as ae:
            return False, f"断言失败: {ae}"
        except Exception as e:
            return False, f"运行错误: {e}"

    def record_exam(self, user_id: int, score: float, total: float, duration_seconds: int, details: Any) -> ExamRecord:
        """保存考试记录到数据库并返回记录对象。"""
        rec = ExamRecord(
            user_id=user_id,
            score=score,
            total=total,
            duration_seconds=duration_seconds,
            details=json.dumps(details, ensure_ascii=False)
        )
        db.session.add(rec)
        db.session.commit()
        return rec

    def get_user_records(self, user_id: int, limit: int = 50) -> List[ExamRecord]:
        """获取用户的考试记录（按时间倒序）。"""
        return ExamRecord.query.filter_by(user_id=user_id).order_by(ExamRecord.created_at.desc()).limit(limit).all()

    def export_records_csv(self, records: Optional[List[ExamRecord]] = None) -> str:
        """导出考试记录为 CSV 字符串。"""
        import io, csv
        if records is None:
            records = ExamRecord.query.order_by(ExamRecord.created_at.desc()).all()
        out = io.StringIO()
        writer = csv.writer(out)
        writer.writerow(['id', 'user_id', 'score', 'total', 'duration_seconds', 'created_at', 'details'])
        for r in records:
            writer.writerow([r.id, r.user_id, r.score, r.total, r.duration_seconds, r.created_at.isoformat(), r.details])
        return out.getvalue()

    def simulate_exam_for_user(self, user_id: int, n: int = 5):
        """
        模拟 n 次考试（用于测试/演示），每次随机生成试卷并打分，保存记录。
        返回生成的记录列表。
        """
        created = []
        for i in range(n):
            paper = self.create_paper()
            # 随机做题：随机正确或错误
            answers = {}
            for q in paper:
                if q.qtype == 'choice':
                    # 随机选择 A-D
                    answers[str(q.id)] = {'answer': random.choice(['A','B','C','D'])}
                elif q.qtype == 'fill':
                    answers[str(q.id)] = {'answer': '示例答案'}
                elif q.qtype == 'code':
                    answers[str(q.id)] = {'answer': q.answer or ''}
            res = self.grade_submission(answers)
            rec = self.record_exam(user_id, res['score'], res['total'], duration_seconds=random.randint(30, 600), details=res['details'])
            created.append(rec)
        return created

    # -----------------------------
    # 统计/分析辅助（交给 Analytics）
    # -----------------------------
    def top_users_by_score(self, limit: int = 10) -> List[Dict[str, Any]]:
        """返回按平均得分排序的用户列表（交给 AnalyticsService 计算）。"""
        return self.analytics.compute_top_users(limit=limit)

    # -----------------------------
    # 其它冗余小方法
    # -----------------------------
    def safe_trim(self, s: Optional[str]) -> str:
        if s is None:
            return ''
        return str(s).strip()

# module-level instance
exam_service = ExamService()
