"""
输出格式化器 (Output Formatter)
美化显示旅游规划结果
"""

from typing import Dict, Any, List
import json


class OutputFormatter:
    """
    结果输出格式化器
    """
    
    def __init__(self):
        pass
    
    def print_planning_result(self, result: Dict[str, Any]):
        """
        打印完整的规划结果
        """
        if not result.get("success"):
            self._print_error(result)
            return
        
        self._print_header(result)
        self._print_algorithm_performance(result)
        self._print_selected_places(result)
        self._print_detailed_itinerary(result)
        self._print_statistics(result)
    
    def _print_error(self, result: Dict[str, Any]):
        """打印错误信息"""
        print(f"\n❌ 规划失败")
        print(f"错误: {result.get('error', '未知错误')}")
        
        if "city" in result:
            print(f"城市: {result['city']}")
        if "time_limit" in result:
            print(f"时间限制: {result['time_limit']} 分钟")
    
    def _print_header(self, result: Dict[str, Any]):
        """打印结果头部"""
        print(f"\n🎉 {result['city']} 旅游规划完成！")
        print("=" * 60)
        print(f"📊 规划算法: 队友设计的两阶段算法")
        print(f"⏱️ 规划耗时: {result['planning_time']:.1f} 秒")
        print(f"🎯 旅行风格: {result['user_preferences']['travel_style']}")
        
        weights = result['user_preferences']['weights']
        print(f"⚖️ 算法权重: 评分{weights['rating']:.1f} + " +
              f"偏好{weights['preference']:.1f} + " +
              f"旅行{weights['travel']:.1f}")
    
    def _print_algorithm_performance(self, result: Dict[str, Any]):
        """打印算法性能信息"""
        print(f"\n🧠 算法性能分析")
        print("-" * 40)
        
        step1 = result['algorithm_results']['step1_knapsack']
        step2 = result['algorithm_results']['step2_route_optimization']
        
        print(f"📦 Step 1 - 增强背包算法:")
        print(f"  候选景点: {step1['total_places_considered']} 个")
        print(f"  选中景点: {step1['places_selected']} 个")
        print(f"  综合得分: {step1['total_composite_score']:.2f}")
        print(f"  选择效率: {step1['selection_efficiency']:.3f} 得分/分钟")
        
        print(f"\n🛣️ Step 2 - 路径优化:")
        print(f"  算法: {step2['algorithm']}")
        print(f"  初始旅行时间: {step2.get('initial_travel_time', 0):.1f} 分钟")
        print(f"  优化后时间: {step2.get('optimized_travel_time', 0):.1f} 分钟")
        print(f"  改进程度: {step2.get('improvement_percent', 0):.1f}%")
    
    def _print_selected_places(self, result: Dict[str, Any]):
        """打印选中的景点"""
        print(f"\n🏛️ 选中的景点 ({len(result['selected_places'])} 个)")
        print("-" * 40)
        
        for i, place in enumerate(result['selected_places'], 1):
            categories = ", ".join(place['categories'])
            print(f"{i}. {place['name']}")
            print(f"   📍 {place['address']}")
            print(f"   ⭐ 评分: {place['rating']}/5.0")
            print(f"   🎯 综合得分: {place['composite_score']:.2f}")
            print(f"   ⏰ 建议游览: {place['visit_time']} 分钟")
            print(f"   🏷️ 类别: {categories}")
            print()
    
    def _print_detailed_itinerary(self, result: Dict[str, Any]):
        """打印详细行程"""
        print(f"📅 详细行程安排")
        print("-" * 40)
        print(f"{'时间':<12} {'时长':<10} {'活动':<30}")
        print("-" * 60)
        
        for item in result['itinerary']:
            start_time = self._format_time(item['start_time'])
            end_time = self._format_time(item['end_time'])
            time_range = f"{start_time}-{end_time}"
            duration = f"{item['duration']:.0f}分钟"
            
            if item['type'] == 'visit':
                activity = f"🎯 {item['activity']}"
                print(f"{time_range:<12} {duration:<10} {activity:<30}")
                rating_info = f"评分: {item['rating']}/5.0, 得分: {item['composite_score']:.1f}"
                print(f"{'':>12} {'':>10} {'   ' + rating_info:<30}")
            else:  # travel
                activity = f"🚶‍♂️ {item['activity']}"
                print(f"{time_range:<12} {duration:<10} {activity:<30}")
            
            print()
    
    def _print_statistics(self, result: Dict[str, Any]):
        """打印统计信息"""
        stats = result['statistics']
        
        print(f"📈 行程统计")
        print("-" * 40)
        print(f"🏛️ 景点数量: {stats['places_count']} 个")
        print(f"⏰ 总游览时间: {stats['total_visit_time']} 分钟")
        print(f"🚶‍♂️ 总旅行时间: {stats['total_travel_time']:.1f} 分钟")
        print(f"📊 总耗时: {stats['total_time']:.1f} 分钟")
        print(f"🎯 总综合得分: {stats['total_composite_score']:.2f}")
        print(f"⚡ 效率指标: {stats['time_efficiency']:.3f} 得分/分钟")
        
        # 参数信息
        params = result['parameters']
        print(f"\n⚙️ 规划参数")
        print("-" * 40)
        print(f"⏱️ 时间限制: {params['time_limit']} 分钟")
        print(f"🚶‍♂️ 交通方式: {params['travel_mode']}")
        print(f"🔢 最大候选数: {params['max_places']}")
        print(f"🏷️ 景点类型: {params['place_type']}")
    
    def _format_time(self, minutes: float) -> str:
        """格式化时间显示"""
        hours = int(minutes // 60)
        mins = int(minutes % 60)
        return f"{hours:02d}:{mins:02d}"
    
    def save_result_to_file(self, result: Dict[str, Any], filename: str = "tour_result.json"):
        """保存结果到文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2, default=str)
            print(f"\n💾 结果已保存到 {filename}")
        except Exception as e:
            print(f"\n❌ 保存文件失败: {e}")
    