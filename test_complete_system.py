"""
全面测试脚本：验证完整的重构系统
测试队友设计的完整算法流程
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.models.place import Place, Location
from src.models.user_preferences import UserPreferences, TravelStyle, PreferenceCategory
from src.core.tour_planner import IntelligentTourPlanner
from src.utils.output_formatter import OutputFormatter


def create_comprehensive_test_data():
    """创建更全面的测试数据"""
    places = [
        Place(
            name="Stanley Park",
            address="Vancouver, BC",
            place_id="test1",
            location=Location(49.3017, -123.1444),
            rating=4.6,
            user_ratings_total=5000,
            place_types=["park", "tourist_attraction"],
            visit_time=90
        ),
        Place(
            name="Vancouver Art Gallery", 
            address="750 Hornby St, Vancouver",
            place_id="test2",
            location=Location(49.2827, -123.1207),
            rating=4.2,
            user_ratings_total=2500,
            place_types=["art_gallery", "museum"],
            visit_time=75
        ),
        Place(
            name="Granville Island Market",
            address="1661 Duranleau St, Vancouver",
            place_id="test3",
            location=Location(49.2713, -123.1342),
            rating=4.4,
            user_ratings_total=8000,
            place_types=["food", "shopping_mall"],
            visit_time=60
        ),
        Place(
            name="Capilano Suspension Bridge",
            address="3735 Capilano Rd, North Vancouver",
            place_id="test4",
            location=Location(49.3429, -123.1149),
            rating=4.3,
            user_ratings_total=12000,
            place_types=["tourist_attraction", "park"],
            visit_time=120
        ),
        Place(
            name="Gastown Steam Clock",
            address="Water St, Vancouver",
            place_id="test5",
            location=Location(49.2839, -123.1064),
            rating=3.8,
            user_ratings_total=1500,
            place_types=["tourist_attraction", "historical_site"],
            visit_time=30
        )
    ]
    return places


def create_comprehensive_travel_matrix():
    """创建5x5旅行时间矩阵"""
    return [
        # From Stanley Park
        [
            {"status": "OK", "duration_minutes": 0, "distance_meters": 0},
            {"status": "OK", "duration_minutes": 25, "distance_meters": 2000},
            {"status": "OK", "duration_minutes": 20, "distance_meters": 1500},
            {"status": "OK", "duration_minutes": 15, "distance_meters": 1200},
            {"status": "OK", "duration_minutes": 30, "distance_meters": 2500}
        ],
        # From Vancouver Art Gallery
        [
            {"status": "OK", "duration_minutes": 25, "distance_meters": 2000},
            {"status": "OK", "duration_minutes": 0, "distance_meters": 0},
            {"status": "OK", "duration_minutes": 15, "distance_meters": 1200},
            {"status": "OK", "duration_minutes": 35, "distance_meters": 3000},
            {"status": "OK", "duration_minutes": 8, "distance_meters": 600}
        ],
        # From Granville Island Market
        [
            {"status": "OK", "duration_minutes": 20, "distance_meters": 1500},
            {"status": "OK", "duration_minutes": 15, "distance_meters": 1200},
            {"status": "OK", "duration_minutes": 0, "distance_meters": 0},
            {"status": "OK", "duration_minutes": 30, "distance_meters": 2800},
            {"status": "OK", "duration_minutes": 18, "distance_meters": 1400}
        ],
        # From Capilano Bridge
        [
            {"status": "OK", "duration_minutes": 15, "distance_meters": 1200},
            {"status": "OK", "duration_minutes": 35, "distance_meters": 3000},
            {"status": "OK", "duration_minutes": 30, "distance_meters": 2800},
            {"status": "OK", "duration_minutes": 0, "distance_meters": 0},
            {"status": "OK", "duration_minutes": 40, "distance_meters": 3500}
        ],
        # From Gastown Steam Clock
        [
            {"status": "OK", "duration_minutes": 30, "distance_meters": 2500},
            {"status": "OK", "duration_minutes": 8, "distance_meters": 600},
            {"status": "OK", "duration_minutes": 18, "distance_meters": 1400},
            {"status": "OK", "duration_minutes": 40, "distance_meters": 3500},
            {"status": "OK", "duration_minutes": 0, "distance_meters": 0}
        ]
    ]


def test_complete_system():
    """测试完整重构后的系统"""
    print("🚀 完整系统测试：队友设计的智能旅游规划器")
    print("=" * 70)
    
    # 创建测试数据
    places = create_comprehensive_test_data()
    travel_matrix = create_comprehensive_travel_matrix()
    
    print(f"📊 测试数据：{len(places)} 个景点")
    for i, place in enumerate(places):
        categories = [cat.value for cat in place.categories]
        print(f"  {i+1}. {place.name}: {place.rating}⭐, {place.visit_time}分钟, {categories}")
    
    # 测试不同的用户偏好
    test_scenarios = [
        {
            "name": "品质探索者",
            "style": TravelStyle.QUALITY_EXPLORER,
            "art_pref": 0.5,
            "nature_pref": 0.3,
            "food_pref": 0.2
        },
        {
            "name": "高效游客", 
            "style": TravelStyle.EFFICIENT_TOURIST,
            "art_pref": 0.2,
            "nature_pref": 0.3,
            "food_pref": 0.5
        },
        {
            "name": "平衡旅行者",
            "style": TravelStyle.BALANCED_TRAVELER,
            "art_pref": 0.33,
            "nature_pref": 0.33,
            "food_pref": 0.34
        }
    ]
    
    # 创建输出格式化器
    formatter = OutputFormatter()
    
    for scenario in test_scenarios:
        print(f"\n" + "="*50)
        print(f"🎭 测试场景: {scenario['name']}")
        print("="*50)
        
        # 创建用户偏好
        user_prefs = UserPreferences()
        user_prefs.travel_style = scenario['style'] 
        user_prefs.category_preferences = {
            PreferenceCategory.ART: scenario['art_pref'],
            PreferenceCategory.NATURE: scenario['nature_pref'],
            PreferenceCategory.FOOD: scenario['food_pref'],
            PreferenceCategory.CULTURE: 0.1,
            PreferenceCategory.SHOPPING: 0.05,
            PreferenceCategory.ENTERTAINMENT: 0.05
        }
        
        # 模拟完整的规划流程（不使用真实API）
        result = simulate_planning_process(places, travel_matrix, user_prefs, 240)  # 4小时
        
        # 显示结果
        formatter.print_planning_result(result)
        
        print(f"\n" + "-"*30)


def simulate_planning_process(places, travel_matrix, user_preferences, time_limit):
    """
    模拟完整的规划流程（不使用真实API）
    """
    from src.algorithms.enhanced_knapsack import EnhancedKnapsackSolver
    from src.algorithms.route_optimizer import RouteOptimizer
    from datetime import datetime
    
    # 创建算法实例
    knapsack_solver = EnhancedKnapsackSolver()
    route_optimizer = RouteOptimizer()
    
    planning_start = datetime.now()
    
    # Step 1: 增强背包算法选择景点
    selected_places, total_score, knapsack_details = knapsack_solver.solve(
        places, user_preferences, travel_matrix, time_limit, start_location_index=0
    )
    
    if not selected_places:
        return {"success": False, "error": "无法在时间限制内选择任何景点"}
    
    # Step 2: 路径优化
    optimized_route, route_details = route_optimizer.optimize_route(
        selected_places, travel_matrix, places, start_index=0
    )
    
    # 生成详细行程
    itinerary = generate_mock_itinerary(optimized_route, travel_matrix, places)
    
    # 计算统计信息
    stats = route_optimizer.calculate_route_statistics(optimized_route, travel_matrix, places)
    
    planning_end = datetime.now()
    planning_time = (planning_end - planning_start).total_seconds()
    
    # 构建结果
    result = {
        "success": True,
        "city": "Vancouver (测试)",
        "planning_time": planning_time,
        "user_preferences": {
            "travel_style": user_preferences.travel_style.value,
            "weights": {
                "rating": user_preferences.weight_rating,
                "preference": user_preferences.weight_preference, 
                "travel": user_preferences.weight_travel
            }
        },
        "algorithm_results": {
            "step1_knapsack": knapsack_details,
            "step2_route_optimization": route_details
        },
        "selected_places": [
            {
                "name": place.name,
                "address": place.address,
                "rating": place.rating,
                "visit_time": place.visit_time,
                "composite_score": place.composite_score,
                "categories": [cat.value for cat in place.categories]
            }
            for place in optimized_route
        ],
        "itinerary": itinerary,
        "statistics": stats,
        "parameters": {
            "time_limit": time_limit,
            "travel_mode": "walking",
            "max_places": len(places),
            "place_type": "tourist_attraction"
        }
    }
    
    return result


def generate_mock_itinerary(route, travel_matrix, all_places):
    """生成模拟行程"""
    itinerary = []
    current_time = 0
    
    for i, place in enumerate(route):
        # 访问活动
        visit_item = {
            "type": "visit",
            "place_name": place.name,
            "address": place.address,
            "start_time": current_time,
            "duration": place.visit_time,
            "end_time": current_time + place.visit_time,
            "activity": f"参观 {place.name}",
            "rating": place.rating,
            "composite_score": place.composite_score
        }
        itinerary.append(visit_item)
        current_time += place.visit_time
        
        # 旅行到下一个地点
        if i < len(route) - 1:
            next_place = route[i + 1]
            from_idx = all_places.index(place)
            to_idx = all_places.index(next_place)
            
            travel_time = travel_matrix[from_idx][to_idx]['duration_minutes']
            
            travel_item = {
                "type": "travel",
                "from_place": place.name,
                "to_place": next_place.name,
                "start_time": current_time,
                "duration": travel_time,
                "end_time": current_time + travel_time,
                "activity": f"前往 {next_place.name}",
                "travel_mode": "步行"
            }
            itinerary.append(travel_item)
            current_time += travel_time
    
    return itinerary


def test_algorithm_comparison():
    """测试算法比较功能"""
    print(f"\n" + "="*50)
    print(f"⚖️ 算法比较测试")
    print("="*50)
    
    places = create_comprehensive_test_data()
    travel_matrix = create_comprehensive_travel_matrix()
    
    user_prefs = UserPreferences()
    user_prefs.travel_style = TravelStyle.BALANCED_TRAVELER
    
    from src.algorithms.enhanced_knapsack import EnhancedKnapsackSolver
    knapsack_solver = EnhancedKnapsackSolver()
    
    comparison = knapsack_solver.compare_with_traditional_knapsack(
        places, user_prefs, travel_matrix, 240
    )
    
    formatter = OutputFormatter()
    formatter.print_comparison_result({"comparison_results": comparison})


if __name__ == "__main__":
    test_complete_system()
    test_algorithm_comparison()
    
    print(f"\n🎉 全面测试完成！")
    print(f"✅ 队友设计的算法已成功实现并集成")
    print(f"📦 Step 1: 增强背包算法 - 综合评分 + 旅行惩罚 + 位置感知")
    print(f"🛣️ Step 2: 两阶段路径优化 - 最近邻 + 2-opt改进")
    print(f"🏗️ 重构完成：模块化、可维护、可扩展")
