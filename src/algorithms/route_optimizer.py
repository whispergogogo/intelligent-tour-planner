"""
路径优化器 (Route Optimizer)
实现队友设计的Step 2: Two-Phase Heuristic Route Optimization
"""

from typing import List, Dict, Any, Tuple, Optional
import random
from ..models.place import Place


class RouteOptimizer:
    """
    实现队友设计的两阶段启发式路径优化：
    1. Nearest Neighbor Initialization
    2. 2-Opt Local Search Improvement
    """
    
    def __init__(self):
        pass
    
    def optimize_route(self, 
                      selected_places: List[Place],
                      travel_matrix: List[List[Dict[str, Any]]],
                      all_places: List[Place],
                      start_index: int = 0) -> Tuple[List[Place], Dict[str, Any]]:
        """
        两阶段路径优化
        
        Args:
            selected_places: 已选中的景点列表
            travel_matrix: 旅行时间矩阵
            all_places: 全部景点列表（用于索引映射）
            start_index: 起始位置索引
            
        Returns:
            (优化后的路径, 优化详情)
        """
        if len(selected_places) <= 1:
            return selected_places, {"algorithm": "No optimization needed"}
        
        # Phase 1: Nearest Neighbor Initialization
        initial_route = self._nearest_neighbor_initialization(
            selected_places, travel_matrix, all_places, start_index
        )
        initial_distance = self._calculate_total_travel_time(initial_route, travel_matrix, all_places)
        
        # Phase 2: 2-Opt Local Search Improvement
        optimized_route = self._two_opt_improvement(initial_route, travel_matrix, all_places)
        final_distance = self._calculate_total_travel_time(optimized_route, travel_matrix, all_places)
        
        # 计算改进情况
        improvement = ((initial_distance - final_distance) / max(1, initial_distance)) * 100
        
        optimization_details = {
            "algorithm": "Two-Phase Heuristic (Nearest Neighbor + 2-Opt)",
            "initial_travel_time": initial_distance,
            "optimized_travel_time": final_distance,
            "improvement_percent": improvement,
            "places_count": len(optimized_route),
            "phases": {
                "phase1": "Nearest Neighbor Initialization",
                "phase2": "2-Opt Local Search"
            }
        }
        
        return optimized_route, optimization_details
    
    def _nearest_neighbor_initialization(self, 
                                        places: List[Place],
                                        travel_matrix: List[List[Dict[str, Any]]],
                                        all_places: List[Place],
                                        start_index: int) -> List[Place]:
        """
        最近邻算法初始化路径
        队友设计的Phase 1
        """
        if not places:
            return []
        
        # 找到起始点（如果在selected_places中）
        route = []
        unvisited = places.copy()
        
        # 尝试从指定起始点开始
        current_place = None
        if start_index < len(all_places):
            start_place = all_places[start_index]
            if start_place in unvisited:
                current_place = start_place
                unvisited.remove(start_place)
        
        # 如果起始点不在选中景点中，从第一个景点开始
        if current_place is None:
            current_place = unvisited.pop(0)
        
        route.append(current_place)
        
        # 贪心选择最近的下一个景点
        while unvisited:
            nearest_place = None
            min_distance = float('inf')
            
            current_index = all_places.index(current_place)
            
            for candidate in unvisited:
                candidate_index = all_places.index(candidate)
                distance = self._get_travel_time(current_index, candidate_index, travel_matrix)
                
                if distance < min_distance:
                    min_distance = distance
                    nearest_place = candidate
            
            if nearest_place:
                route.append(nearest_place)
                unvisited.remove(nearest_place)
                current_place = nearest_place
            else:
                # 如果无法到达任何景点，添加剩余景点
                route.extend(unvisited)
                break
        
        return route
    
    def _two_opt_improvement(self, 
                           route: List[Place],
                           travel_matrix: List[List[Dict[str, Any]]],
                           all_places: List[Place],
                           max_iterations: int = 100) -> List[Place]:
        """
        2-opt局部搜索改进
        队友设计的Phase 2
        """
        if len(route) < 4:  # 2-opt需要至少4个点
            return route
        
        best_route = route.copy()
        best_distance = self._calculate_total_travel_time(best_route, travel_matrix, all_places)
        
        improved = True
        iteration = 0
        
        while improved and iteration < max_iterations:
            improved = False
            iteration += 1
            
            # 尝试所有可能的2-opt交换
            for i in range(1, len(route) - 2):
                for j in range(i + 1, len(route)):
                    if j - i == 1:  # 跳过相邻的边
                        continue
                    
                    # 创建新路径：反转i到j之间的段
                    new_route = route.copy()
                    new_route[i:j] = reversed(new_route[i:j])
                    
                    # 计算新路径的距离
                    new_distance = self._calculate_total_travel_time(new_route, travel_matrix, all_places)
                    
                    # 如果找到更好的路径
                    if new_distance < best_distance:
                        best_route = new_route
                        best_distance = new_distance
                        improved = True
                        break
                
                if improved:
                    break
            
            route = best_route.copy()
        
        return best_route
    
    def _calculate_total_travel_time(self, 
                                   route: List[Place],
                                   travel_matrix: List[List[Dict[str, Any]]],
                                   all_places: List[Place]) -> float:
        """
        計算路径的总旅行时间
        """
        if len(route) <= 1:
            return 0.0
        
        total_time = 0.0
        
        for i in range(len(route) - 1):
            from_index = all_places.index(route[i])
            to_index = all_places.index(route[i + 1])
            travel_time = self._get_travel_time(from_index, to_index, travel_matrix)
            total_time += travel_time
        
        return total_time
    
    def _get_travel_time(self, 
                        from_index: int, 
                        to_index: int, 
                        travel_matrix: List[List[Dict[str, Any]]]) -> float:
        """
        获取两点间的旅行时间
        """
        if (from_index >= len(travel_matrix) or 
            to_index >= len(travel_matrix[from_index])):
            return float('inf')
        
        element = travel_matrix[from_index][to_index]
        
        if element.get('status') == 'OK':
            return element.get('duration_minutes', float('inf'))
        else:
            return float('inf')
    
    def calculate_route_statistics(self, 
                                 route: List[Place],
                                 travel_matrix: List[List[Dict[str, Any]]],
                                 all_places: List[Place]) -> Dict[str, Any]:
        """
        计算路径统计信息
        """
        if not route:
            return {"error": "Empty route"}
        
        total_visit_time = sum(place.visit_time for place in route)
        total_travel_time = self._calculate_total_travel_time(route, travel_matrix, all_places)
        total_time = total_visit_time + total_travel_time
        
        # 计算平均旅行时间
        avg_travel_time = total_travel_time / max(1, len(route) - 1) if len(route) > 1 else 0
        
        # 计算效率指标
        total_score = sum(place.composite_score for place in route)
        time_efficiency = total_score / max(1, total_time)
        
        return {
            "places_count": len(route),
            "total_visit_time": total_visit_time,
            "total_travel_time": total_travel_time,
            "total_time": total_time,
            "average_travel_time": avg_travel_time,
            "total_composite_score": total_score,
            "time_efficiency": time_efficiency,
            "route_names": [place.name for place in route]
        }
    
    def generate_multiple_routes(self, 
                               selected_places: List[Place],
                               travel_matrix: List[List[Dict[str, Any]]],
                               all_places: List[Place],
                               num_routes: int = 3) -> List[Tuple[List[Place], Dict[str, Any]]]:
        """
        生成多个候选路径并选择最佳的
        """
        routes_with_stats = []
        
        for i in range(num_routes):
            # 随机起始点
            start_index = random.randint(0, len(all_places) - 1)
            
            # 优化路径
            optimized_route, details = self.optimize_route(
                selected_places, travel_matrix, all_places, start_index
            )
            
            # 计算统计信息
            stats = self.calculate_route_statistics(optimized_route, travel_matrix, all_places)
            combined_details = {**details, **stats}
            
            routes_with_stats.append((optimized_route, combined_details))
        
        # 按时间效率排序
        routes_with_stats.sort(key=lambda x: x[1]['time_efficiency'], reverse=True)
        
        return routes_with_stats
