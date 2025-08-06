"""
核心业务逻辑协调器 (Tour Planner Core)
整合队友设计的完整算法流程
"""

from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from ..models.place import Place
from ..models.user_preferences import UserPreferences
from ..api.google_places import GooglePlacesAPI
from ..api.google_maps import GoogleMapsAPI
from ..algorithms.enhanced_knapsack import EnhancedKnapsackSolver
from ..algorithms.route_optimizer import RouteOptimizer


class IntelligentTourPlanner:
    """
    智能旅游规划器
    实现队友设计文档的完整算法流程
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化旅游规划器
        
        Args:
            api_key: Google Maps API密钥
        """
        self.places_api = GooglePlacesAPI(api_key)
        self.maps_api = GoogleMapsAPI(api_key)
        self.knapsack_solver = EnhancedKnapsackSolver()
        self.route_optimizer = RouteOptimizer()
    
    def plan_tour(self, 
                  city: str,
                  user_preferences: UserPreferences,
                  time_limit: int,
                  place_type: str = "tourist_attraction",
                  max_places: int = 15,
                  travel_mode: str = "walking") -> Dict[str, Any]:
        """
        完整的旅游规划流程
        实现队友设计的两步算法
        
        Args:
            city: 城市名称
            user_preferences: 用户偏好
            time_limit: 时间限制（分钟）
            place_type: 景点类型
            max_places: 最大候选景点数
            travel_mode: 交通方式
            
        Returns:
            完整的旅游规划结果
        """
        planning_start_time = datetime.now()
        
        print(f"🌍 开始规划 {city} 的旅游行程...")
        print(f"📋 参数：时间限制 {time_limit}分钟，交通方式：{travel_mode}")
        
        # Step 1: 获取候选景点
        print(f"\n🔍 Step 1: 搜索候选景点...")
        candidate_places = self.places_api.search_places(
            city=city, 
            place_type=place_type, 
            max_results=max_places
        )
        
        if not candidate_places:
            return {"error": "未找到任何景点", "city": city}
        
        print(f"✅ 找到 {len(candidate_places)} 个候选景点")
        
        # Step 2: 获取旅行时间矩阵
        print(f"\n🗺️ Step 2: 计算景点间距离...")
        travel_matrix = self.maps_api.get_travel_time_matrix(
            candidate_places, 
            mode=travel_mode,
            departure_time=datetime.now()
        )
        
        if not travel_matrix:
            return {"error": "无法获取距离信息", "places": len(candidate_places)}
        
        print(f"✅ 获取 {len(travel_matrix)}x{len(travel_matrix[0])} 距离矩阵")
        
        # Step 3: 队友设计的Step 1 - Enhanced Knapsack
        print(f"\n🎒 Step 3: 执行增强背包算法（景点选择）...")
        selected_places, total_score, knapsack_details = self.knapsack_solver.solve(
            candidate_places,
            user_preferences, 
            travel_matrix,
            time_limit,
            start_location_index=0
        )
        
        print(f"✅ 选中 {len(selected_places)} 个景点，总得分 {total_score:.2f}")
        
        if not selected_places:
            return {
                "error": "在时间限制内无法访问任何景点",
                "time_limit": time_limit,
                "candidates": len(candidate_places)
            }
        
        # Step 4: 队友设计的Step 2 - Route Optimization  
        print(f"\n🛣️ Step 4: 执行路径优化算法...")
        optimized_route, route_details = self.route_optimizer.optimize_route(
            selected_places,
            travel_matrix,
            candidate_places,
            start_index=0
        )
        
        print(f"✅ 路径优化完成，改进 {route_details.get('improvement_percent', 0):.1f}%")
        
        # Step 5: 生成详细行程
        print(f"\n📅 Step 5: 生成详细行程...")
        detailed_itinerary = self._generate_detailed_itinerary(
            optimized_route, travel_matrix, candidate_places
        )
        
        # Step 6: 计算最终统计
        final_stats = self.route_optimizer.calculate_route_statistics(
            optimized_route, travel_matrix, candidate_places
        )
        
        planning_end_time = datetime.now()
        planning_duration = (planning_end_time - planning_start_time).total_seconds()
        
        print(f"✅ 规划完成！耗时 {planning_duration:.1f} 秒")
        
        # 组织完整结果
        result = {
            "success": True,
            "city": city,
            "planning_time": planning_duration,
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
            "itinerary": detailed_itinerary,
            "statistics": final_stats,
            "parameters": {
                "time_limit": time_limit,
                "travel_mode": travel_mode,
                "max_places": max_places,
                "place_type": place_type
            }
        }
        
        return result
    
    def _generate_detailed_itinerary(self, 
                                   route: List[Place],
                                   travel_matrix: List[List[Dict[str, Any]]],
                                   all_places: List[Place]) -> List[Dict[str, Any]]:
        """
        生成详细的行程安排
        """
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
            
            # 旅行到下一个地点（如果不是最后一个）
            if i < len(route) - 1:
                next_place = route[i + 1]
                
                from_index = all_places.index(place)
                to_index = all_places.index(next_place)
                
                travel_time = self._get_travel_time(from_index, to_index, travel_matrix)
                
                travel_item = {
                    "type": "travel",
                    "from_place": place.name,
                    "to_place": next_place.name,
                    "start_time": current_time,
                    "duration": travel_time,
                    "end_time": current_time + travel_time,
                    "activity": f"前往 {next_place.name}",
                    "travel_mode": "步行"  # 可以根据实际情况调整
                }
                itinerary.append(travel_item)
                current_time += travel_time
        
        return itinerary
    
    def _get_travel_time(self, from_index: int, to_index: int, travel_matrix: List[List[Dict[str, Any]]]) -> float:
        """获取旅行时间"""
        if (from_index >= len(travel_matrix) or 
            to_index >= len(travel_matrix[from_index])):
            return 30.0  # 默认30分钟
        
        element = travel_matrix[from_index][to_index]
        if element.get('status') == 'OK':
            return element.get('duration_minutes', 30.0)
        else:
            return 30.0

    def _recommend_best_style(self, results: Dict[str, Any]) -> str:
        """根据分析结果推荐最佳旅行风格"""
        if not results:
            return "无法分析"
        
        best_style = max(results.keys(), key=lambda style: results[style]["efficiency"])
        return f"推荐 {best_style}：效率最高 ({results[best_style]['efficiency']:.3f})"
