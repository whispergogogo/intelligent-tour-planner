"""
增强背包算法 (Enhanced Knapsack)
实现队友设计的"Iterative Knapsack with Travel Time Estimation"
和"Position-aware greedy decisions"
"""

from typing import List, Dict, Any, Optional, Tuple
from ..models.place import Place
from ..models.user_preferences import UserPreferences
from .scoring import CompositeScoringSystem
from .travel_penalty import TravelPenaltyCalculator


class EnhancedKnapsackSolver:
    """
    实现队友设计的增强背包算法：
    "Apply position-aware greedy decisions by evaluating each attraction's 
    efficiency score (composite_score / total_time_needed) from the current location"
    """
    
    def __init__(self):
        self.scoring_system = CompositeScoringSystem()
        self.penalty_calculator = TravelPenaltyCalculator()
    
    def solve(self, 
              places: List[Place], 
              user_preferences: UserPreferences,
              travel_matrix: List[List[Dict[str, Any]]],
              time_limit: int,
              start_location_index: int = 0) -> Tuple[List[Place], float, Dict[str, Any]]:
        """
        解决增强背包问题
        
        Args:
            places: 候选景点列表
            user_preferences: 用户偏好
            travel_matrix: 旅行时间矩阵
            time_limit: 时间限制（分钟）
            start_location_index: 起始位置索引
            
        Returns:
            (选中的景点列表, 总得分, 详细信息)
        """
        if not places or time_limit <= 0:
            return [], 0.0, {}
        
        # Step 1: 计算旅行惩罚
        travel_penalties = self.penalty_calculator.calculate_travel_penalties(places, travel_matrix)
        
        # Step 2: 计算综合得分
        self.scoring_system.batch_calculate_scores(places, user_preferences, travel_penalties)
        
        # Step 3: 迭代贪心选择（位置感知）
        selected_places, total_score, selection_details = self._iterative_position_aware_selection(
            places, travel_matrix, time_limit, start_location_index
        )
        
        # Step 4: 准备详细信息
        details = {
            "algorithm": "Enhanced Knapsack with Travel Time Estimation",
            "total_places_considered": len(places),
            "places_selected": len(selected_places),
            "total_composite_score": total_score,
            "time_limit": time_limit,
            "time_used": selection_details.get("time_used", 0),
            "selection_efficiency": total_score / max(1, selection_details.get("time_used", 1)),
            "selection_details": selection_details
        }
        
        return selected_places, total_score, details
    
    def _iterative_position_aware_selection(self, 
                                           places: List[Place], 
                                           travel_matrix: List[List[Dict[str, Any]]],
                                           time_limit: int,
                                           start_index: int) -> Tuple[List[Place], float, Dict[str, Any]]:
        """
        迭代的位置感知选择算法
        队友设计的核心算法
        """
        selected_places = []
        available_places = places.copy()
        current_location_index = start_index
        remaining_time = time_limit
        total_score = 0.0
        
        selection_log = []  # 记录选择过程
        
        iteration = 0
        while available_places and remaining_time > 0:
            iteration += 1
            
            # 计算每个可用景点的效率得分
            best_efficiency = -1
            best_place = None
            best_place_index = -1
            best_total_time = 0
            
            for i, place in enumerate(available_places):
                # 找到该景点在原列表中的索引
                original_index = places.index(place)
                
                # 计算从当前位置到该景点的旅行时间
                travel_time = self._get_travel_time(current_location_index, original_index, travel_matrix)
                
                # 计算总时间需求（旅行时间 + 访问时间）
                total_time_needed = travel_time + place.visit_time
                
                # 检查时间约束
                if total_time_needed <= remaining_time:
                    # 计算效率得分（队友设计的核心公式）
                    efficiency_score = place.composite_score / total_time_needed
                    
                    if efficiency_score > best_efficiency:
                        best_efficiency = efficiency_score
                        best_place = place
                        best_place_index = original_index
                        best_total_time = total_time_needed
            
            # 如果找到了最佳选择
            if best_place is not None:
                selected_places.append(best_place)
                available_places.remove(best_place)
                total_score += best_place.composite_score
                remaining_time -= best_total_time
                
                # 更新当前位置
                current_location_index = best_place_index
                
                # 记录选择过程
                selection_log.append({
                    "iteration": iteration,
                    "selected_place": best_place.name,
                    "composite_score": best_place.composite_score,
                    "efficiency_score": best_efficiency,
                    "time_needed": best_total_time,
                    "remaining_time": remaining_time
                })
            else:
                # 没有找到符合时间约束的景点，结束选择
                break
        
        selection_details = {
            "iterations": iteration,
            "time_used": time_limit - remaining_time,
            "remaining_time": remaining_time,
            "selection_log": selection_log,
            "final_location_index": current_location_index
        }
        
        return selected_places, total_score, selection_details
    
    def _get_travel_time(self, 
                        from_index: int, 
                        to_index: int, 
                        travel_matrix: List[List[Dict[str, Any]]]) -> float:
        """
        从旅行矩阵中获取旅行时间
        
        Args:
            from_index: 起点索引
            to_index: 终点索引
            travel_matrix: 旅行时间矩阵
            
        Returns:
            旅行时间（分钟）
        """
        if (from_index >= len(travel_matrix) or 
            to_index >= len(travel_matrix[from_index])):
            return float('inf')
        
        element = travel_matrix[from_index][to_index]
        
        if element.get('status') == 'OK':
            return element.get('duration_minutes', float('inf'))
        else:
            return float('inf')
    