import math
import json
from datetime import datetime, timedelta
from collections import defaultdict


class OptimizedDropRateManager:
    def __init__(self):
        self.auto_rates = {}
        self.manual_rates = {}
        self.history_records = []
        self.auto_file = 'drop_rates_auto.json'
        self.manual_file = 'drop_rates_manual.json'
        self.history_file = 'draw_history.json'
        self.load_all_data()

    def load_all_data(self):
        """加载所有数据"""
        # 加载自动爆率
        try:
            if os.path.exists(self.auto_file):
                with open(self.auto_file, 'r', encoding='utf-8') as f:
                    self.auto_rates = json.load(f)
        except:
            self.auto_rates = {}

        # 加载手动爆率
        try:
            if os.path.exists(self.manual_file):
                with open(self.manual_file, 'r', encoding='utf-8') as f:
                    self.manual_rates = json.load(f)
        except:
            self.manual_rates = {}

        # 加载历史记录
        self.load_history()

        # 基于历史记录重新计算自动爆率
        self.recalculate_auto_rates()
        self.save_auto_rates()

    def load_history(self):
        """加载历史记录"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.history_records = data
                    else:
                        self.history_records = []
        except:
            self.history_records = []

    def save_history(self):
        """保存历史记录"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(
                    self.history_records, f, ensure_ascii=False, indent=2
                )
            return True
        except:
            return False

    def recalculate_auto_rates(self):
        """基于历史记录重新计算自动爆率 - 优化版算法"""
        if not self.history_records:
            return

        # 分析历史记录
        name_stats = defaultdict(
            lambda: {
                'total_count': 0,
                'recent_7_days': 0,
                'recent_30_days': 0,
                'last_draw_days': float('inf'),  # 距离上次被点的天数
                'first_draw_days': float('inf'),  # 距离第一次被点的天数
            }
        )

        total_draws = len(self.history_records)
        now = datetime.now()

        # 第一次遍历：统计基础数据
        name_first_draw = {}
        name_last_draw = {}

        for record in self.history_records:
            name = record.get('name', '')
            if not name:
                continue

            record_time = record.get('timestamp', '')
            try:
                if record_time:
                    record_date = datetime.fromisoformat(record_time)
                else:
                    record_date = now
            except:
                record_date = now

            # 更新统计
            name_stats[name]['total_count'] += 1

            # 更新首次和最后被点时间
            if (
                name not in name_first_draw
                or record_date < name_first_draw[name]
            ):
                name_first_draw[name] = record_date
            if (
                name not in name_last_draw
                or record_date > name_last_draw[name]
            ):
                name_last_draw[name] = record_date

        # 第二次遍历：计算时间相关统计
        seven_days_ago = now - timedelta(days=7)
        thirty_days_ago = now - timedelta(days=30)

        for record in self.history_records:
            name = record.get('name', '')
            record_time = record.get('timestamp', '')

            try:
                if record_time:
                    record_date = datetime.fromisoformat(record_time)
                else:
                    record_date = now
            except:
                record_date = now

            # 近期统计
            if record_date >= seven_days_ago:
                name_stats[name]['recent_7_days'] += 1
            if record_date >= thirty_days_ago:
                name_stats[name]['recent_30_days'] += 1

        # 计算时间距离
        for name in name_stats:
            if name in name_last_draw:
                name_stats[name]['last_draw_days'] = (
                    now - name_last_draw[name]
                ).days
            if name in name_first_draw:
                name_stats[name]['first_draw_days'] = (
                    now - name_first_draw[name]
                ).days

        # 智能爆率计算
        for name, stats in name_stats.items():
            if name in self.manual_rates:
                continue  # 跳过手动配置的

            total_count = stats['total_count']
            recent_7_days = stats['recent_7_days']
            recent_30_days = stats['recent_30_days']
            last_draw_days = stats['last_draw_days']
            first_draw_days = stats['first_draw_days']

            # === 优化版算法 ===

            # 1. 基础惩罚 - 使用对数函数平滑处理
            # 被点次数越多，惩罚越大，但增长逐渐放缓
            base_penalty = min(0.4, math.log(total_count + 1) * 0.15)

            # 2. 近期活跃惩罚 - 重点关注最近7天
            recent_penalty = min(0.3, math.log(recent_7_days + 1) * 0.2)

            # 3. 冷却时间奖励 - 长时间没被点会有奖励
            cool_down_bonus = 0.0
            if last_draw_days > 7:  # 超过7天没被点
                cool_down_bonus = min(0.3, math.log(last_draw_days - 6) * 0.1)

            # 4. 新人保护 - 第一次被点不久的人有保护
            newcomer_bonus = 0.0
            if first_draw_days <= 3:  # 3天内第一次被点
                newcomer_bonus = 0.2 * (1 - first_draw_days / 3)

            # 5. 长期未点奖励 - 结合总次数和最后被点时间
            long_time_no_see_bonus = 0.0
            if total_count > 0 and last_draw_days > 14:  # 被点过但很久没点了
                long_time_no_see_bonus = min(
                    0.4,
                    (math.log(last_draw_days) * 0.15)
                    + (math.log(total_count) * 0.05),
                )

            # 6. 平衡因子 - 确保整体平衡
            avg_draws = total_draws / max(1, len(name_stats))
            balance_factor = 0.0
            if total_count > avg_draws * 1.5:  # 被点次数远高于平均
                balance_factor = -0.1
            elif total_count < avg_draws * 0.5:  # 被点次数远低于平均
                balance_factor = 0.1

            # 最终爆率计算
            base_rate = 1.0  # 基础爆率
            calculated_rate = (
                base_rate
                - base_penalty
                - recent_penalty
                + cool_down_bonus
                + newcomer_bonus
                + long_time_no_see_bonus
                + balance_factor
            )

            # 边界控制
            final_rate = max(0.05, min(1.0, calculated_rate))  # 最低5%，最高100%

            self.auto_rates[name] = round(final_rate, 3)

    def save_auto_rates(self):
        """保存自动爆率"""
        try:
            with open(self.auto_file, 'w', encoding='utf-8') as f:
                json.dump(self.auto_rates, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False

    def save_manual_rates(self):
        """保存手动爆率"""
        try:
            with open(self.manual_file, 'w', encoding='utf-8') as f:
                json.dump(self.manual_rates, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False

    def get_drop_rate(self, name, use_manual_override=True):
        """获取爆率（优先使用手动配置）"""
        if use_manual_override and name in self.manual_rates:
            return self.manual_rates[name]
        return self.auto_rates.get(name, 1.0)

    def set_drop_rate(self, name, rate, is_manual=True):
        """设置爆率"""
        try:
            rate = float(rate)
            if rate < 0:
                rate = 0.0
            elif rate > 1:
                rate = 1.0

            if is_manual:
                self.manual_rates[name] = round(rate, 3)
                return self.save_manual_rates()
            else:
                # 只有在没有手动配置时才更新自动配置
                if name not in self.manual_rates:
                    self.auto_rates[name] = round(rate, 3)
                    return self.save_auto_rates()
                return True
        except:
            return False

    def reset_drop_rate(self, name):
        """重置单个爆率（删除手动配置）"""
        if name in self.manual_rates:
            del self.manual_rates[name]
            # 重新计算自动爆率
            self.recalculate_auto_rates()
            self.save_auto_rates()
            return self.save_manual_rates()
        return False

    def reset_all_manual_rates(self):
        """重置所有手动爆率"""
        self.manual_rates = {}
        # 重新计算自动爆率
        self.recalculate_auto_rates()
        self.save_auto_rates()
        return self.save_manual_rates()

    def reset_all_auto_rates(self):
        """重置所有自动爆率"""
        self.auto_rates = {}
        return self.save_auto_rates()

    def reset_today_history(self):
        """重置当天历史记录"""
        today = datetime.now().date()
        self.history_records = [
            record
            for record in self.history_records
            if datetime.fromisoformat(
                record.get('timestamp', '2000-01-01')
            ).date()
            != today
        ]
        success = self.save_history()
        if success:
            self.recalculate_auto_rates()
            self.save_auto_rates()
        return success

    def reset_all_history(self):
        """重置所有历史记录"""
        self.history_records = []
        success = self.save_history()
        if success:
            self.recalculate_auto_rates()
            self.save_auto_rates()
        return success

    def get_all_drop_rates(self):
        """获取所有爆率配置（合并手动和自动）"""
        all_rates = self.auto_rates.copy()
        all_rates.update(self.manual_rates)
        return all_rates

    def get_manual_rates(self):
        """获取所有手动爆率"""
        return self.manual_rates.copy()

    def get_auto_rates(self):
        """获取所有自动爆率"""
        return self.auto_rates.copy()

    def get_history_records(self):
        """获取历史记录"""
        return self.history_records.copy()

    def add_history_record(self, name, timestamp=None):
        """添加历史记录"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        record = {'name': name, 'timestamp': timestamp}
        self.history_records.append(record)
        self.save_history()

        # 重新计算自动爆率
        self.recalculate_auto_rates()
        self.save_auto_rates()

    def update_from_list(self, name_list):
        """根据名单更新自动爆率配置（不覆盖手动修改）"""
        updated = False
        new_names = []
        for name in name_list:
            # 只有在没有手动配置时才更新自动配置
            if name not in self.manual_rates and name not in self.auto_rates:
                self.auto_rates[name] = 1.0
                new_names.append(name)
                updated = True

        if updated:
            self.save_auto_rates()
            return True, new_names
        return False, []

    def get_detailed_stats(self, name):
        """获取详细的统计信息"""
        if not self.history_records:
            return None

        stats = {
            'total_count': 0,
            'recent_7_days': 0,
            'recent_30_days': 0,
            'last_draw_days': None,
            'first_draw_days': None,
            'current_rate': self.get_drop_rate(name),
            'rate_type': 'manual' if name in self.manual_rates else 'auto',
        }

        now = datetime.now()
        seven_days_ago = now - timedelta(days=7)
        thirty_days_ago = now - timedelta(days=30)

        first_draw = None
        last_draw = None

        for record in self.history_records:
            if record.get('name') == name:
                record_time = record.get('timestamp', '')
                try:
                    if record_time:
                        record_date = datetime.fromisoformat(record_time)
                    else:
                        continue
                except:
                    continue

                stats['total_count'] += 1

                if record_date >= seven_days_ago:
                    stats['recent_7_days'] += 1
                if record_date >= thirty_days_ago:
                    stats['recent_30_days'] += 1

                if first_draw is None or record_date < first_draw:
                    first_draw = record_date
                if last_draw is None or record_date > last_draw:
                    last_draw = record_date

        if last_draw:
            stats['last_draw_days'] = (now - last_draw).days
        if first_draw:
            stats['first_draw_days'] = (now - first_draw).days

        return stats


# 全局实例
drop_rate_manager = OptimizedDropRateManager()
