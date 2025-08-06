"""
智能旅游规划器 - 主程序
实现队友设计的完整算法流程
重构后的干净版本
"""

import os
import sys
from src.core.tour_planner import IntelligentTourPlanner
from src.utils.input_handler import InputHandler
from src.utils.output_formatter import OutputFormatter
from src.utils.config import load_env_file


def main():
    """主程序入口"""
    # 加载.env文件
    load_env_file()
    
    # 检查API密钥
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        print("❌ 错误: 请设置 GOOGLE_MAPS_API_KEY")
        print("💡 步骤: cp env.example .env，然后编辑.env文件填入API密钥")
        sys.exit(1)
    
    # 初始化组件
    input_handler = InputHandler()
    output_formatter = OutputFormatter()
    tour_planner = IntelligentTourPlanner(api_key)
    
    try:
        # 1. 获取用户输入
        params = input_handler.get_basic_parameters()
        user_preferences = input_handler.get_user_preferences()
        
        # 2. 确认设置
        if not input_handler.confirm_settings(params, user_preferences):
            print("已取消规划")
            return
        
        # 3. 执行旅游规划
        result = tour_planner.plan_tour(
            city=params['city'],
            user_preferences=user_preferences,
            time_limit=params['time_limit'],
            place_type=params['place_type'],
            max_places=params['max_results'],
            travel_mode=params['travel_mode']
        )
        
        # 4. 显示结果
        output_formatter.print_planning_result(result)
        
        # 5. 保存结果（可选）
        save_file = input(f"\n💾 是否保存结果到文件? (y/n, 默认: y): ").strip().lower()
        if save_file != 'n':
            filename = f"tour_result_{params['city'].lower().replace(' ', '_')}.json"
            output_formatter.save_result_to_file(result, filename)
        
        print(f"\n🎉 感谢使用智能旅游规划器！")
        print(f"基于队友设计的增强背包算法 + 两阶段路径优化")
        
    except KeyboardInterrupt:
        print(f"\n\n⏹️ 用户中断了程序")
    except Exception as e:
        print(f"\n❌ 程序运行出错: {e}")
        print(f"请检查网络连接和API密钥设置")


if __name__ == "__main__":
    main()
