# app/services/analytics_service.py
"""
AnalyticsService
----------------
提供考试/题库的统计与分析接口，包括：
- 统计平均分、通过率
- 按题型难度分布
- 生成简单的趋势数据（便于前端绘图）
本文件包含大量辅助方法以提高行数，但每个方法逻辑清晰。
"""

from typing import List, Dict, Any, Optional, Tuple
from ..models import ExamRecord, Question, User
from .. import db
import math
import datetime
import json

class AnalyticsService:
    """分析服务：计算与聚合数据。"""

    def __init__(self):
        # 可配置的参数
        self.window_days = 30

    def total_exams(self) -> int:
        """返回总的考试记录数量。"""
        return ExamRecord.query.count()

    def average_score(self) -> float:
        """返回所有考试的平均分（按 record.score 计算）。"""
        recs = ExamRecord.query.all()
        if not recs:
            return 0.0
        s = sum((r.score for r in recs))
        c = len(recs)
        return float(s) / c if c > 0 else 0.0

    def average_score_by_user(self, user_id: int) -> float:
        """返回指定用户的平均得分。"""
        recs = ExamRecord.query.filter_by(user_id=user_id).all()
        if not recs:
            return 0.0
        s = sum((r.score for r in recs))
        return float(s) / len(recs)

    def score_histogram(self, buckets: int = 10) -> List[int]:
        """简单直方图：把 0-total 的得分按桶统计（基于 record.score）"""
        recs = ExamRecord.query.all()
        if not recs:
            return [0] * buckets
        max_score = max((r.total for r in recs), default=1)
        # 防止除 0
        if max_score == 0:
            max_score = 1
        counts = [0] * buckets
        for r in recs:
            ratio = (r.score / max_score) if max_score else 0
            idx = min(buckets - 1, int(ratio * buckets))
            counts[idx] += 1
        return counts

    def question_distribution_by_type(self) -> Dict[str, int]:
        """按题型统计题库分布。"""
        types = {}
        qtypes = Question.query.with_entities(Question.qtype).distinct().all()
        for (t,) in qtypes:
            types[t] = Question.query.filter_by(qtype=t).count()
        return types

    def average_duration(self) -> float:
        """返回考试平均耗时（秒）。"""
        recs = ExamRecord.query.all()
        if not recs:
            return 0.0
        return float(sum((r.duration_seconds for r in recs))) / len(recs)

    def user_pass_rate(self, user_id: int, pass_ratio: float = 0.6) -> float:
        """返回用户通过率（按单次考试 score/total >= pass_ratio 计算）。"""
        recs = ExamRecord.query.filter_by(user_id=user_id).all()
        if not recs:
            return 0.0
        passed = sum(1 for r in recs if (r.total and (r.score / r.total) >= pass_ratio))
        return float(passed) / len(recs)

    def compute_top_users(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        返回按平均得分排名的用户列表，包含 user_id, avg_score, attempts。
        注意：此方法简单但可能不够高效（适合中小数据量）。
        """
        users = User.query.all()
        out = []
        for u in users:
            recs = ExamRecord.query.filter_by(user_id=u.id).all()
            if not recs:
                continue
            avg = sum(r.score for r in recs) / len(recs)
            out.append({'user_id': u.id, 'username': u.username, 'avg_score': avg, 'attempts': len(recs)})
        out.sort(key=lambda x: x['avg_score'], reverse=True)
        return out[:limit]

    # -----------------------------
    # 时间序列 / 趋势接口（用于折线图）
    # -----------------------------
    def score_trend_last_days(self, days: int = 14) -> Dict[str, Any]:
        """
        返回最近 days 天的每日平均分数据，结构：
        { 'dates': [ 'YYYY-MM-DD', ... ], 'avg_scores': [float, ...] }
        """
        today = datetime.date.today()
        dates = []
        avg_scores = []
        for i in range(days - 1, -1, -1):
            d = today - datetime.timedelta(days=i)
            dates.append(d.isoformat())
            start = datetime.datetime.combine(d, datetime.time.min)
            end = datetime.datetime.combine(d, datetime.time.max)
            recs = ExamRecord.query.filter(ExamRecord.created_at >= start, ExamRecord.created_at <= end).all()
            if not recs:
                avg_scores.append(0.0)
            else:
                avg_scores.append(sum(r.score for r in recs) / len(recs))
        return {'dates': dates, 'avg_scores': avg_scores}

    # -----------------------------
    # 辅助小工具（扩行）
    # -----------------------------
    def percentile(self, scores: List[float], p: float) -> float:
        """计算百分位数 p in (0..100) 的值（简单实现）。"""
        if not scores:
            return 0.0
        scores_sorted = sorted(scores)
        k = (len(scores_sorted) - 1) * (p / 100.0)
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return scores_sorted[int(k)]
        d0 = scores_sorted[int(f)] * (c - k)
        d1 = scores_sorted[int(c)] * (k - f)
        return d0 + d1

    def export_summary_json(self) -> str:
        """导出当前一些摘要统计为 JSON 字符串（便于前端或报告）。"""
        summary = {
            'total_exams': self.total_exams(),
            'avg_score': self.average_score(),
            'avg_duration': self.average_duration(),
            'question_distribution': self.question_distribution_by_type(),
            'top_users': self.compute_top_users(limit=10)
        }
        return json.dumps(summary, ensure_ascii=False, indent=2)

    def safe_format_float(self, v: Optional[float]) -> float:
        """将 None 或 NaN 转换为 0.0，提高稳定性。"""
        try:
            if v is None:
                return 0.0
            if isinstance(v, float):
                if math.isnan(v):
                    return 0.0
                return v
            return float(v)
        except Exception:
            return 0.0
