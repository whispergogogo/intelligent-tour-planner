"""
用户输入处理器 (Input Handler)
处理命令行交互和用户偏好收集
"""

from typing import Dict, Any
from ..models.user_preferences import UserPreferences, TravelStyle, PreferenceCategory


class InputHandler:
    """
    用户输入处理器
    实现队友设计中的用户偏好收集
    """
    
    def __init__(self):
        pass
    
    def get_basic_parameters(self) -> Dict[str, Any]:
        """
        获取基本规划参数
        """
        print("🌟 欢迎使用智能旅游规划器！")
        print("基于队友设计的增强背包算法 + 两阶段路径优化")
        print("-" * 50)
        
        city = input("请输入城市名称 (默认: Vancouver): ").strip()
        if not city:
            city = "Vancouver"
        
        place_type = input("请输入景点类型 (默认: tourist_attraction): ").strip()
        if not place_type:
            place_type = "tourist_attraction"
        
        try:
            max_results = int(input("最大候选景点数量 (默认: 15): ") or "15")
        except ValueError:
            max_results = 15
        
        try:
            time_limit = int(input("时间限制（分钟） (默认: 300): ") or "300")
        except ValueError:
            time_limit = 300
        
        travel_mode = input("交通方式 (walking/driving/bicycling, 默认: walking): ").strip()
        if travel_mode not in ["walking", "driving", "bicycling"]:
            travel_mode = "walking"
        
        return {
            "city": city,
            "place_type": place_type,
            "max_results": max_results,
            "time_limit": time_limit,
            "travel_mode": travel_mode
        }
    
    def get_user_preferences(self) -> UserPreferences:
        """
        获取用户偏好
        实现队友设计的用户偏好方法
        """
        print(f"\n🎯 用户偏好设置")
        print("队友设计包含：旅行风格 + 类别偏好权重")
        print("-" * 50)
        
        # 1. 选择旅行风格
        travel_style = self._get_travel_style()
        
        # 2. 设置类别偏好
        category_preferences = self._get_category_preferences()
        
        # 3. 创建用户偏好对象
        user_prefs = UserPreferences()
        user_prefs.travel_style = travel_style
        user_prefs.category_preferences = category_preferences
        
        # 4. 可选：自定义权重
        if travel_style == TravelStyle.CUSTOM:
            user_prefs = self._get_custom_weights(user_prefs)
        
        return user_prefs
    
    def _get_travel_style(self) -> TravelStyle:
        """获取旅行风格"""
        print("请选择您的旅行风格：")
        print("1. 品质探索者 (Quality Explorer) - 重视景点质量")
        print("2. 高效游客 (Efficient Tourist) - 重视时间效率")
        print("3. 平衡旅行者 (Balanced Traveler) - 平衡各方面")
        print("4. 自定义 (Custom) - 自定义权重")
        
        while True:
            try:
                choice = int(input("请选择 (1-4): "))
                if choice == 1:
                    return TravelStyle.QUALITY_EXPLORER
                elif choice == 2:
                    return TravelStyle.EFFICIENT_TOURIST
                elif choice == 3:
                    return TravelStyle.BALANCED_TRAVELER
                elif choice == 4:
                    return TravelStyle.CUSTOM
                else:
                    print("请输入1-4之间的数字")
            except ValueError:
                print("请输入有效的数字")
    
    def _get_category_preferences(self) -> Dict[PreferenceCategory, float]:
        """获取类别偏好权重"""
        print(f"\n请设置各类景点的偏好程度 (0.0-1.0)：")
        
        categories = [
            (PreferenceCategory.ART, "艺术类 (博物馆、画廊)"),
            (PreferenceCategory.FOOD, "美食类 (餐厅、市场)"),
            (PreferenceCategory.NATURE, "自然类 (公园、海滩)"),
            (PreferenceCategory.CULTURE, "文化类 (历史遗迹、建筑)"),
            (PreferenceCategory.SHOPPING, "购物类 (商场、商店)"),
            (PreferenceCategory.ENTERTAINMENT, "娱乐类 (游乐园、剧院)")
        ]
        
        preferences = {}
        total_weight = 0.0
        
        for category, description in categories:
            while True:
                try:
                    weight = float(input(f"{description} 偏好权重 (默认: 0.2): ") or "0.2")
                    if 0.0 <= weight <= 1.0:
                        preferences[category] = weight
                        total_weight += weight
                        break
                    else:
                        print("权重必须在0.0-1.0之间")
                except ValueError:
                    print("请输入有效的数字")
        
        # 归一化权重
        if total_weight > 0:
            for category in preferences:
                preferences[category] /= total_weight
        
        print(f"权重归一化完成，总和: {sum(preferences.values()):.2f}")
        
        return preferences
    
    def _get_custom_weights(self, user_prefs: UserPreferences) -> UserPreferences:
        """获取自定义权重"""
        print(f"\n自定义算法权重设置：")
        print("队友设计的综合评分公式权重")
        
        try:
            rating_weight = float(input("景点评分权重 (0.0-1.0, 默认: 0.4): ") or "0.4")
            preference_weight = float(input("偏好匹配权重 (0.0-1.0, 默认: 0.4): ") or "0.4")
            travel_weight = float(input("旅行惩罚权重 (0.0-1.0, 默认: 0.2): ") or "0.2")
            
            # 归一化
            total = rating_weight + preference_weight + travel_weight
            if total > 0:
                user_prefs.weight_rating = rating_weight / total
                user_prefs.weight_preference = preference_weight / total
                user_prefs.weight_travel = travel_weight / total
            
            print(f"权重设置完成：评分{user_prefs.weight_rating:.2f}, " + 
                  f"偏好{user_prefs.weight_preference:.2f}, " +
                  f"旅行{user_prefs.weight_travel:.2f}")
                  
        except ValueError:
            print("使用默认权重设置")
        
        return user_prefs
    
    def confirm_settings(self, params: Dict[str, Any], user_prefs: UserPreferences) -> bool:
        """确认设置"""
        print(f"\n📋 设置确认：")
        print(f"城市: {params['city']}")
        print(f"时间限制: {params['time_limit']} 分钟")
        print(f"交通方式: {params['travel_mode']}")
        print(f"旅行风格: {user_prefs.travel_style.value}")
        print(f"算法权重: 评分{user_prefs.weight_rating:.1f}, " +
              f"偏好{user_prefs.weight_preference:.1f}, " + 
              f"旅行{user_prefs.weight_travel:.1f}")
        
        confirm = input(f"\n确认开始规划? (y/n, 默认: y): ").strip().lower()
        return confirm != 'n'
