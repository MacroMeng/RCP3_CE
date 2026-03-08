
#135行附近debug！

def randomchoice(flush=True, record_history=True):
    global name, _name_, k, window_width, window_height, choose_mode, enable_drop_rate, use_manual_override
    
    if not name:
        return "名单为空"
    
    # 确保管理器存在
    global choose_manager, drop_rate_manager
    if 'choose_manager' not in globals():
        from choose_manager import choose_manager
    if 'drop_rate_manager' not in globals():
        from drop_rate_manager import drop_rate_manager
    
    # 根据模式选择名字
    if choose_mode == "repeat":
        temp = weighted_random_choice(name)
    elif choose_mode == "single_no_repeat":
        temp = weighted_random_choice(name)
        if temp in name:
            name.remove(temp)
    elif choose_mode == "history_no_repeat":
        available_names = [n for n in name if choose_manager.get_choice_count(n, "history_balance") == 0]
        if available_names:
            temp = weighted_random_choice(available_names)
        else:
            choose_manager.clear_history()
            temp = weighted_random_choice(name)
    else:
        temp = balanced_choice(name, choose_mode)
    
    temp = check_choose(temp)
    
    # 只有在record_history=True时才记录历史
    if record_history and choose_mode != "single_no_repeat":
        choose_manager.record_choice(temp)
        # 新增：记录到爆率管理器的历史中
        drop_rate_manager.add_history_record(temp)
    
    # 显示结果
    text = pygame.font.SysFont("MicrosoftYaHei UI", size=int(150*k)).render(temp, True, (255,255,255))
    screen.blit(namesurface, ((window_width-4.5*150*k)/2+8*k, (window_height-150*k)/2-30*k))
    screen.blit(text, ((4.5*150*k+30*k-text.get_width())/2-2*k+(window_width-4.5*150*k)/2+8*k, 
                      (150*k+60*k-text.get_height())/2-10*k+(window_height-150*k)/2-30*k))
    if flush:
        pygame.display.update(((window_width-4.5*150*k)/2+8*k, (window_height-150*k)/2-30*k, 
                             4.5*150*k+30*k, 150*k+60*k))
    return temp

def weighted_random_choice(name_list):
    """带权重的随机选择（考虑爆率）"""
    if not name_list:
        return ""
    
    global enable_drop_rate, use_manual_override
    
    if not enable_drop_rate:
        return random.choice(name_list)
    
    # 计算每个名字的权重（基于爆率）
    weights = []
    for name in name_list:
        drop_rate = drop_rate_manager.get_drop_rate(name, use_manual_override=use_manual_override)
        weights.append(drop_rate)
    
    # 如果所有权重都为0，使用均匀分布
    if sum(weights) == 0:
        return random.choice(name_list)
    
    return random.choices(name_list, weights=weights, k=1)[0]

def balanced_choice(name_list, mode):
    """修复后的平衡选择算法（更稳定可靠）"""
    if not name_list:
        return ""
    
    # 确保管理器存在
    global choose_manager, drop_rate_manager
    if 'choose_manager' not in globals():
        from choose_manager import choose_manager
    if 'drop_rate_manager' not in globals():
        from drop_rate_manager import drop_rate_manager
    
    # 获取权重配置
    balance_weight = float(globals().get('balance_weight', 0.7))
    smart_sensitivity = float(globals().get('smart_sensitivity', 0.5))
    enable_drop_rate = bool(globals().get('enable_drop_rate', False))
    use_manual_override = bool(globals().get('use_manual_override', True))
    
    # 计算每个名字的权重
    weights = []
    
    for name in name_list:
        if mode == "today_balance":
            count = choose_manager.get_choice_count(name, "today_balance")
            # 改进的权重计算：使用指数衰减，更平滑
            base_weight = 1.0 / (1.0 + count * balance_weight * 2)
            
        elif mode == "history_balance":
            count = choose_manager.get_choice_count(name, "history_balance")
            # 历史平衡：使用对数衰减，避免过度惩罚
            base_weight = 1.0 / (1.0 + count * balance_weight * 0.5)
            
        elif mode == "smart_balance":
            today_count = choose_manager.get_choice_count(name, "today_balance")
            history_count = choose_manager.get_choice_count(name, "history_balance")
            
            # 智能平衡：综合考虑今日和历史，使用更合理的权重分配
            today_weight = today_count * smart_sensitivity
            history_weight = history_count * (1 - smart_sensitivity) * 0.3  # 历史影响减弱
            
            # 使用平滑的衰减函数
            total_weight = today_weight + history_weight
            base_weight = 1.0 / (1.0 + total_weight * balance_weight)
        else:
            base_weight = 1.0
        
        # 应用爆率调整
        if enable_drop_rate:
            drop_rate = drop_rate_manager.get_drop_rate(name, use_manual_override=use_manual_override)
            final_weight = base_weight * drop_rate
        else:
            final_weight = base_weight
        
        # 确保权重不为负
        final_weight = max(0.001, final_weight)
        weights.append(final_weight)
    
    # 调试信息（可选）
#     debug_info = f"模式: {mode}, 权重: {[f'{w:.3f}' for w in weights]}"
#     print(f"平衡选择调试: {debug_info}")
    
    # 如果所有权重都为0，使用均匀分布
    if sum(weights) <= 0.001:
        return random.choice(name_list)
    
    return random.choices(name_list, weights=weights, k=1)[0]

def check_except_names(tempname):
    global except_name
    if tempname in except_name:
        return True
    else:
        return False

def check_choose(tempname):
    global name
    if check_except_names(tempname):
        name.remove(tempname)
        if name:
            tempname = random.choice(name)
            return check_choose(tempname)
        else:
            return "名单为空"
    else:
        return tempname

def reset_choose_history():
    """重置点名历史"""
    choose_manager.reset_all()
    return "点名历史已重置"

def get_choose_stats(mode="today"):
    """获取点名统计"""
    if mode == "today":
        data = choose_manager.today_data
        title = "今日点名统计"
    else:
        data = choose_manager.history_data
        title = "历史点名统计"
    
    if not data:
        return f"{title}：暂无数据"
    
    stats = [f"{title}："]
    for name, count in sorted(data.items(), key=lambda x: x[1], reverse=True):
        stats.append(f"{name}：{count}次")
    
    return "\n".join(stats)

def test_balance_mechanism(test_rounds=1000):
    """测试平衡机制（用于验证稳定性）"""
    global name, choose_mode, enable_drop_rate
    
    print("🧪 开始平衡机制测试...")
    
    # 备份当前设置
    original_mode = choose_mode
    original_drop_rate = enable_drop_rate
    original_names = name.copy()
    
    # 禁用爆率以确保测试纯净
    enable_drop_rate = False
    
    test_results = {}
    
    # 测试每种平衡模式
    test_modes = ["today_balance", "history_balance", "smart_balance"]
    
    for mode in test_modes:
        print(f"\n🔍 测试模式: {mode}")
        choose_mode = mode
        
        # 重置历史
        choose_manager.reset_all()
        
        # 模拟多次点名
        results = {}
        for i in range(test_rounds):
            chosen = balanced_choice(original_names, mode)
            if chosen in results:
                results[chosen] += 1
            else:
                results[chosen] = 1
        
        # 分析结果
        total_picks = sum(results.values())
        avg_picks = total_picks / len(original_names)
        
        # 计算公平性指标（标准差越小越公平）
        pick_counts = list(results.values())
        std_dev = (sum((x - avg_picks) ** 2 for x in pick_counts) / len(pick_counts)) ** 0.5
        
        test_results[mode] = {
            'total_picks': total_picks,
            'avg_picks': avg_picks,
            'std_dev': std_dev,
            'min_picks': min(pick_counts),
            'max_picks': max(pick_counts),
            'fairness_ratio': avg_picks / (std_dev + 0.001)  # 避免除零
        }
        
        print(f"  总点名: {total_picks}")
        print(f"  平均每人: {avg_picks:.2f}次")
        print(f"  标准差: {std_dev:.2f}")
        print(f"  最少点名: {min(pick_counts)}次")
        print(f"  最多点名: {max(pick_counts)}次")
        print(f"  公平性比率: {test_results[mode]['fairness_ratio']:.2f}")
    
    # 恢复原始设置
    choose_mode = original_mode
    enable_drop_rate = original_drop_rate
    name = original_names.copy()
    
    print("\n✅ 平衡机制测试完成!")
    return test_results

def get_balance_debug_info():
    """获取平衡机制调试信息"""
    global choose_mode, balance_weight, smart_sensitivity, enable_drop_rate
    
    debug_info = [
        "🔧 平衡机制调试信息:",
        f"当前模式: {choose_mode}",
        f"平衡权重: {balance_weight}",
        f"智能敏感度: {smart_sensitivity}",
        f"爆率调整: {'启用' if enable_drop_rate else '禁用'}"
    ]
    
    if choose_mode in ["today_balance", "history_balance", "smart_balance"]:
        # 显示当前权重分布
        global name, choose_manager
        weights = []
        for student in name[:5]:  # 只显示前5个作为样本
            if choose_mode == "today_balance":
                count = choose_manager.get_choice_count(student, "today_balance")
                weight = 1.0 / (1.0 + count * balance_weight * 2)
            elif choose_mode == "history_balance":
                count = choose_manager.get_choice_count(student, "history_balance")
                weight = 1.0 / (1.0 + count * balance_weight * 0.5)
            else:  # smart_balance
                today_count = choose_manager.get_choice_count(student, "today_balance")
                history_count = choose_manager.get_choice_count(student, "history_balance")
                today_weight = today_count * smart_sensitivity
                history_weight = history_count * (1 - smart_sensitivity) * 0.3
                total_weight = today_weight + history_weight
                weight = 1.0 / (1.0 + total_weight * balance_weight)
            
            weights.append(f"{student}: {weight:.3f}")
        
        debug_info.append("样本权重:")
        debug_info.extend(weights)
    
    return "\n".join(debug_info)

# 爆率管理函数 - 双文件系统
def set_drop_rate(name, rate):
    """设置爆率（自动保存到手动文件）"""
    success = drop_rate_manager.set_drop_rate(name, rate, is_manual=True)
    if success:
        return f"✅ 已设置 {name} 的爆率为 {rate*100}% (手动)"
    else:
        return f"❌ 设置 {name} 的爆率失败"

def get_drop_rate(name):
    """获取爆率信息（显示来源）"""
    rate = drop_rate_manager.get_drop_rate(name)
    source = "手动" if name in drop_rate_manager.get_manual_rates() else "自动"
    return f"{name} 的爆率：{rate*100}% ({source})"

def get_all_drop_rates():
    """获取所有爆率配置（显示来源）"""
    all_rates = drop_rate_manager.get_all_drop_rates()
    manual_rates = drop_rate_manager.get_manual_rates()
    
    if not all_rates:
        return "暂无爆率配置"
    
    result = ["爆率配置："]
    for name, rate in sorted(all_rates.items()):
        source = "手动" if name in manual_rates else "自动"
        result.append(f"{name}：{rate*100}% ({source})")
    
    return "\n".join(result)

def get_manual_drop_rates():
    """获取所有手动修改的爆率"""
    manual_rates = drop_rate_manager.get_manual_rates()
    
    if not manual_rates:
        return "暂无手动修改的爆率"
    
    result = ["手动修改的爆率："]
    for name, rate in sorted(manual_rates.items()):
        result.append(f"{name}：{rate*100}%")
    
    return "\n".join(result)

def get_auto_drop_rates():
    """获取所有自动爆率"""
    auto_rates = drop_rate_manager.get_auto_rates()
    
    if not auto_rates:
        return "暂无自动爆率配置"
    
    result = ["自动爆率配置："]
    for name, rate in sorted(auto_rates.items()):
        result.append(f"{name}：{rate*100}%")
    
    return "\n".join(result)

def reset_drop_rate(name):
    """重置爆率（从手动文件中删除）"""
    success = drop_rate_manager.reset_drop_rate(name)
    if success:
        return f"✅ 已重置 {name} 的爆率（恢复自动设置）"
    else:
        return f"❌ 重置 {name} 的爆率失败（可能不存在于手动文件）"

def reset_all_drop_rates():
    """重置所有爆率（清空手动文件）"""
    success = drop_rate_manager.reset_all_drop_rates()
    if success:
        return "✅ 已重置所有手动爆率配置"
    else:
        return "❌ 重置爆率配置失败"

def update_drop_rates_from_names():
    """更新爆率配置（不覆盖手动修改）"""
    global _name_
    updated, new_names = drop_rate_manager.update_from_list(_name_)
    if updated:
        if new_names:
            return f"✅ 已根据名单更新爆率配置\n新增 {len(new_names)} 个名字：{', '.join(new_names[:3])}{'...' if len(new_names) > 3 else ''}"
        else:
            return "✅ 爆率配置已更新"
    else:
        return "📝 爆率配置已是最新，无需更新"

def get_drop_rate_stats():
    """获取爆率统计信息"""
    all_rates = drop_rate_manager.get_all_drop_rates()
    manual_rates = drop_rate_manager.get_manual_rates()
    auto_rates = drop_rate_manager.get_auto_rates()
    
    stats = ["📊 爆率统计："]
    stats.append(f"总配置人数：{len(all_rates)}")
    stats.append(f"手动修改：{len(manual_rates)} 人")
    stats.append(f"自动设置：{len(auto_rates)} 人")
    
    # 统计爆率分布
    low_rate = len([r for r in all_rates.values() if r < 0.5])
    medium_rate = len([r for r in all_rates.values() if 0.5 <= r < 1.0])
    high_rate = len([r for r in all_rates.values() if r == 1.0])
    
    stats.append(f"低爆率(<50%)：{low_rate} 人")
    stats.append(f"中爆率(50-99%)：{medium_rate} 人")
    stats.append(f"高爆率(100%)：{high_rate} 人")
    
    return "\n".join(stats)

# 初始化管理器
def init_managers():
    """初始化选择管理器和爆率管理器"""
    global choose_manager, drop_rate_manager
    try:
        from choose_manager import choose_manager
        from drop_rate_manager import drop_rate_manager
        print("✅ 选择管理器和爆率管理器初始化成功")
        return True
    except Exception as e:
        print(f"❌ 管理器初始化失败：{e}")
        return False

# 在模块加载时自动初始化
init_managers()