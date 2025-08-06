"""
旅行惩罚计算 (Travel Penalty Calculation)
实现队友设计文档中的Top-N Travel Penalty
"""

from typing import List, Dict, Any
import statistics
from ..models.place import Place


class TravelPenaltyCalculator:
    """
    实现队友设计的Top-N旅行惩罚：
    "Calculate each attraction's average distance to the N highest-rated 
    attractions to encourage selection of well-connected, high-quality clusters"
    """
    
    def __init__(self, n: int = 5):
        """
        初始化旅行惩罚计算器
        
        Args:
            n: 考虑前N个高评分景点
        """
        self.n = n
    
    def calculate_travel_penalties(self, 
                                  places: List[Place], 
                                  travel_matrix: List[List[Dict[str, Any]]]) -> List[float]:
        """
        计算所有景点的旅行惩罚值
        
        Args:
            places: 景点列表
            travel_matrix: 旅行时间矩阵
            
        Returns:
            每个景点的旅行惩罚值列表
        """
        if len(places) <= self.n:
            # 如果景点数少于等于N，所有景点惩罚都为0
            return [0.0] * len(places)
        
        # 1. 获取前N个高评分景点的索引
        top_n_indices = self._get_top_n_rated_indices(places)
        
        # 2. 计算每个景点的旅行惩罚
        penalties = []
        for i, place in enumerate(places):
            penalty = self._calculate_single_place_penalty(i, top_n_indices, travel_matrix)
            penalties.append(penalty)
        
        # 3. 归一化惩罚值 (0-10 scale)
        normalized_penalties = self._normalize_penalties(penalties)
        
        # 4. 更新景点对象
        for i, place in enumerate(places):
            place.travel_penalty = normalized_penalties[i]
        
        return normalized_penalties
    
    def _get_top_n_rated_indices(self, places: List[Place]) -> List[int]:
        """
        获取前N个高评分景点的索引
        
        Args:
            places: 景点列表
            
        Returns:
            前N个高评分景点的索引列表
        """
        # 创建 (评分, 索引) 对并排序
        rated_places = [(place.rating, i) for i, place in enumerate(places)]
        rated_places.sort(reverse=True, key=lambda x: x[0])
        
        # 返回前N个的索引
        return [idx for _, idx in rated_places[:self.n]]
    
    def _calculate_single_place_penalty(self, 
                                       place_index: int, 
                                       top_n_indices: List[int], 
                                       travel_matrix: List[List[Dict[str, Any]]]) -> float:
        """
        计算单个景点的旅行惩罚值
        
        Args:
            place_index: 当前景点索引
            top_n_indices: 前N个高评分景点索引
            travel_matrix: 旅行时间矩阵
            
        Returns:
            该景点的旅行惩罚值
        """
        if place_index >= len(travel_matrix):
            return float('inf')
        
        travel_times = []
        
        for top_index in top_n_indices:
            if (place_index < len(travel_matrix) and 
                top_index < len(travel_matrix[place_index]) and
                travel_matrix[place_index][top_index]['status'] == 'OK'):
                
                travel_time = travel_matrix[place_index][top_index]['duration_minutes']
                
                # 排除自己到自己的距离
                if place_index != top_index and travel_time < float('inf'):
                    travel_times.append(travel_time)
        
        if not travel_times:
            return float('inf')  # 无法到达任何高评分景点
        
        # 返回平均旅行时间作为惩罚值
        return statistics.mean(travel_times)
    
    def _normalize_penalties(self, penalties: List[float]) -> List[float]:
        """
        归一化惩罚值到0-10范围
        
        Args:
            penalties: 原始惩罚值列表
            
        Returns:
            归一化后的惩罚值列表
        """
        # 过滤掉无限值
        finite_penalties = [p for p in penalties if p != float('inf')]
        
        if not finite_penalties:
            return [0.0] * len(penalties)
        
        min_penalty = min(finite_penalties)
        max_penalty = max(finite_penalties)
        
        if max_penalty == min_penalty:
            # 所有惩罚值相同，返回中等惩罚
            return [5.0] * len(penalties)
        
        # 线性归一化到0-10范围
        normalized = []
        for penalty in penalties:
            if penalty == float('inf'):
                normalized.append(10.0)  # 最大惩罚
            else:
                # 归一化公式：将最小值映射到0，最大值映射到10
                norm_value = ((penalty - min_penalty) / (max_penalty - min_penalty)) * 10
                normalized.append(norm_value)
        
        return normalized
    
    def get_well_connected_clusters(self, 
                                   places: List[Place], 
                                   travel_matrix: List[List[Dict[str, Any]]],
                                   penalty_threshold: float = 5.0) -> List[List[int]]:
        """
        识别连通性好的景点簇
        队友设计中提到的 "well-connected, high-quality clusters"
        
        Args:
            places: 景点列表
            travel_matrix: 旅行时间矩阵
            penalty_threshold: 惩罚值阈值
            
        Returns:
            景点簇列表，每个簇包含景点索引
        """
        penalties = self.calculate_travel_penalties(places, travel_matrix)
        
        # 找出低惩罚值的景点（连通性好）
        well_connected_indices = [
            i for i, penalty in enumerate(penalties) 
            if penalty <= penalty_threshold
        ]
        
        if not well_connected_indices:
            return []
        
        # 简单的聚类：基于旅行时间的邻近性
        clusters = []
        used_indices = set()
        
        for idx in well_connected_indices:
            if idx in used_indices:
                continue
            
            cluster = [idx]
            used_indices.add(idx)
            
            # 找出与当前景点旅行时间较短的其他景点
            for other_idx in well_connected_indices:
                if (other_idx not in used_indices and
                    idx < len(travel_matrix) and
                    other_idx < len(travel_matrix[idx]) and
                    travel_matrix[idx][other_idx]['status'] == 'OK'):
                    
                    travel_time = travel_matrix[idx][other_idx]['duration_minutes']
                    
                    # 如果旅行时间小于30分钟，认为是同一簇
                    if travel_time <= 30:
                        cluster.append(other_idx)
                        used_indices.add(other_idx)
            
            if len(cluster) > 1:  # 只保留包含多个景点的簇
                clusters.append(cluster)
        
        return clusters
    
    def analyze_connectivity(self, 
                           places: List[Place], 
                           travel_matrix: List[List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        分析景点连通性统计信息
        
        Args:
            places: 景点列表
            travel_matrix: 旅行时间矩阵
            
        Returns:
            连通性分析结果
        """
        penalties = self.calculate_travel_penalties(places, travel_matrix)
        clusters = self.get_well_connected_clusters(places, travel_matrix)
        
        return {
            "total_places": len(places),
            "average_penalty": statistics.mean(penalties) if penalties else 0,
            "min_penalty": min(penalties) if penalties else 0,
            "max_penalty": max(penalties) if penalties else 0,
            "well_connected_count": sum(1 for p in penalties if p <= 5.0),
            "poorly_connected_count": sum(1 for p in penalties if p > 7.0),
            "clusters_found": len(clusters),
            "largest_cluster_size": max((len(c) for c in clusters), default=0),
        }
