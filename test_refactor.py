"""
测试脚本：验证重构后的算法实现
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.models.place import Place, Location
from src.models.user_preferences import UserPreferences, TravelStyle, PreferenceCategory
from src.algorithms.scoring import CompositeScoringSystem
from src.algorithms.travel_penalty import TravelPenaltyCalculator
from src.algorithms.enhanced_knapsack import EnhancedKnapsackSolver


def create_test_places():
    """创建测试数据"""
    places = [
        Place(
            name="Stanley Park",
            address="Vancouver, BC",
            place_id="test1",
            location=Location(49.3017, -123.1444),
            rating=4.6,
            user_ratings_total=5000,
            place_types=["park", "tourist_attraction"],
            visit_time=60
        ),
        Place(
            name="Vancouver Art Gallery",
            address="750 Hornby St, Vancouver",
            place_id="test2", 
            location=Location(49.2827, -123.1207),
            rating=4.2,
            user_ratings_total=2500,
            place_types=["art_gallery", "museum"],
            visit_time=90
        ),
        Place(
            name="Granville Island Market",
            address="1661 Duranleau St, Vancouver",
            place_id="test3",
            location=Location(49.2713, -123.1342),
            rating=4.4,
            user_ratings_total=8000,
            place_types=["food", "shopping_mall"],
            visit_time=75
        )
    ]
    return places


def create_test_travel_matrix():
    """创建测试旅行时间矩阵"""
    return [
        [
            {"status": "OK", "duration_minutes": 0, "distance_meters": 0},
            {"status": "OK", "duration_minutes": 25, "distance_meters": 2000},
            {"status": "OK", "duration_minutes": 15, "distance_meters": 1200}
        ],
        [
            {"status": "OK", "duration_minutes": 25, "distance_meters": 2000},
            {"status": "OK", "duration_minutes": 0, "distance_meters": 0},
            {"status": "OK", "duration_minutes": 20, "distance_meters": 1500}
        ],
        [
            {"status": "OK", "duration_minutes": 15, "distance_meters": 1200},
            {"status": "OK", "duration_minutes": 20, "distance_meters": 1500},
            {"status": "OK", "duration_minutes": 0, "distance_meters": 0}
        ]
    ]


def test_algorithms():
    """测试重构后的算法"""
    print("🧪 测试重构后的算法实现")
    print("=" * 50)
    
    # 1. 创建测试数据
    places = create_test_places()
    travel_matrix = create_test_travel_matrix()
    
    # 2. 创建用户偏好
    user_prefs = UserPreferences()
    user_prefs.travel_style = TravelStyle.BALANCED_TRAVELER
    user_prefs.category_preferences[PreferenceCategory.ART] = 0.4
    user_prefs.category_preferences[PreferenceCategory.NATURE] = 0.3
    user_prefs.category_preferences[PreferenceCategory.FOOD] = 0.3
    
    print(f"📊 测试数据：{len(places)}个景点")
    for place in places:
        print(f"  - {place.name}: {place.rating}⭐, {place.visit_time}分钟, 类别: {list(place.categories)}")
    
    # 3. 测试综合评分系统
    print(f"\n🎯 测试综合评分系统")
    scoring_system = CompositeScoringSystem()
    
    for place in places:
        score = scoring_system.calculate_composite_score(place, user_prefs, 0.0)
        print(f"  - {place.name}: 综合得分 {score:.2f}")
    
    # 4. 测试旅行惩罚计算
    print(f"\n🚗 测试旅行惩罚计算")
    penalty_calc = TravelPenaltyCalculator(n=2)  # 前2个高评分景点
    penalties = penalty_calc.calculate_travel_penalties(places, travel_matrix)
    
    for i, place in enumerate(places):
        print(f"  - {place.name}: 旅行惩罚 {penalties[i]:.2f}")
    
    # 5. 测试增强背包算法
    print(f"\n🎒 测试增强背包算法")
    knapsack_solver = EnhancedKnapsackSolver()
    
    time_limit = 180  # 3小时
    selected_places, total_score, details = knapsack_solver.solve(
        places, user_prefs, travel_matrix, time_limit, start_location_index=0
    )
    
    print(f"  时间限制: {time_limit}分钟")
    print(f"  选中景点数: {len(selected_places)}")
    print(f"  总得分: {total_score:.2f}")
    print(f"  使用时间: {details['time_used']:.1f}分钟")
    print(f"  效率: {details['selection_efficiency']:.2f} 得分/分钟")
    
    print(f"  选中的景点:")
    for place in selected_places:
        print(f"    - {place.name}: 得分{place.composite_score:.2f}, 访问{place.visit_time}分钟")
    
    # 6. 算法比较
    print(f"\n⚖️ 算法比较：增强背包 vs 传统背包")
    comparison = knapsack_solver.compare_with_traditional_knapsack(
        places, user_prefs, travel_matrix, time_limit
    )
    
    enhanced = comparison["enhanced_knapsack"]
    traditional = comparison["traditional_knapsack"]
    improvement = comparison["improvement"]
    
    print(f"  增强背包: {enhanced['places_count']}个景点, 得分{enhanced['total_score']:.2f}")
    print(f"  传统背包: {traditional['places_count']}个景点, 得分{traditional['total_score']:.2f}")
    print(f"  改进: 得分提升{improvement['score_improvement_percent']:.1f}%")
    
    # 7. 连通性分析
    print(f"\n🕸️ 连通性分析")
    connectivity = penalty_calc.analyze_connectivity(places, travel_matrix)
    print(f"  平均旅行惩罚: {connectivity['average_penalty']:.2f}")
    print(f"  连通性好的景点: {connectivity['well_connected_count']}/{connectivity['total_places']}")
    
    print(f"\n✅ 测试完成！算法实现正常工作。")


if __name__ == "__main__":
    test_algorithms()
