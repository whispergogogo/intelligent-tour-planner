"""
综合评分系统 (Composite Scoring System)
实现队友设计文档中的核心评分算法
"""

from typing import List
from ..models.place import Place
from ..models.user_preferences import UserPreferences, PreferenceCategory


class CompositeScoringSystem:
    """
    实现队友设计的综合评分公式：
    attraction_score = (review_rating * weight_rating) + 
                      (preference_match_score * weight_preference) - 
                      (travel_penalty * weight_travel)
    """
    
    def __init__(self):
        pass
    
    def calculate_composite_score(self, 
                                 place: Place, 
                                 user_preferences: UserPreferences,
                                 travel_penalty: float = 0.0) -> float:
        """
        计算景点的综合得分
        
        Args:
            place: 景点对象
            user_preferences: 用户偏好
            travel_penalty: 旅行惩罚值
            
        Returns:
            综合得分
        """
        # 1. Review Rating Component (0-10 scale)
        review_rating = place.rating * 2  # Convert from 5-star to 10-point scale
        
        # 2. Preference Match Score
        preference_match_score = self._calculate_preference_match(place, user_preferences)
        
        # 3. Apply the composite scoring formula
        composite_score = (
            review_rating * user_preferences.weight_rating +
            preference_match_score * user_preferences.weight_preference -
            travel_penalty * user_preferences.weight_travel
        )
        
        # Update place object
        place.composite_score = max(0, composite_score)  # Ensure non-negative
        place.travel_penalty = travel_penalty
        
        return place.composite_score
    
    def _calculate_preference_match(self, 
                                   place: Place, 
                                   user_preferences: UserPreferences) -> float:
        """
        计算偏好匹配得分
        量化景点类别与用户偏好的匹配程度
        
        Args:
            place: 景点对象
            user_preferences: 用户偏好
            
        Returns:
            偏好匹配得分 (0-10)
        """
        if not place.categories:
            return 5.0  # 默认中等匹配度
        
        # 计算加权匹配得分
        total_match_score = 0.0
        total_weight = 0.0
        
        for category in place.categories:
            if category in user_preferences.category_preferences:
                category_weight = user_preferences.get_category_weight(category)
                
                # 基础匹配得分 (基于用户对该类别的偏好强度)
                base_match = category_weight * 10  # Convert to 0-10 scale
                
                # 考虑景点在该类别中的质量
                quality_multiplier = self._get_category_quality_multiplier(place, category)
                
                match_score = base_match * quality_multiplier
                
                total_match_score += match_score * category_weight
                total_weight += category_weight
        
        if total_weight > 0:
            return min(10.0, total_match_score / total_weight)
        else:
            return 5.0  # 默认中等匹配度
    
    def _get_category_quality_multiplier(self, 
                                        place: Place, 
                                        category: PreferenceCategory) -> float:
        """
        根据景点类别获取质量乘数
        
        Args:
            place: 景点对象
            category: 偏好类别
            
        Returns:
            质量乘数 (0.5-1.5)
        """
        # 基于评分和评价数量的质量评估
        rating_factor = place.rating / 5.0  # 0-1
        
        # 评价数量因子（更多评价意味着更可靠）
        import math
        if place.user_ratings_total > 0:
            popularity_factor = min(1.0, math.log10(place.user_ratings_total) / 3.0)
        else:
            popularity_factor = 0.5
        
        # 类别特定的调整
        category_adjustments = {
            PreferenceCategory.ART: 1.0,
            PreferenceCategory.FOOD: 1.1,      # 美食评价通常更直观
            PreferenceCategory.NATURE: 0.9,    # 自然景观评价相对主观
            PreferenceCategory.CULTURE: 1.0,
            PreferenceCategory.SHOPPING: 0.8,  # 购物场所评价差异较大
            PreferenceCategory.ENTERTAINMENT: 1.2,  # 娱乐场所评价通常更明确
        }
        
        category_adj = category_adjustments.get(category, 1.0)
        
        # 综合质量乘数
        quality_multiplier = (rating_factor * 0.7 + popularity_factor * 0.3) * category_adj
        
        return max(0.5, min(1.5, quality_multiplier))
    
    def batch_calculate_scores(self, 
                              places: List[Place], 
                              user_preferences: UserPreferences,
                              travel_penalties: List[float] = None) -> List[Place]:
        """
        批量计算景点综合得分
        
        Args:
            places: 景点列表
            user_preferences: 用户偏好
            travel_penalties: 旅行惩罚列表（可选）
            
        Returns:
            更新得分后的景点列表
        """
        if travel_penalties is None:
            travel_penalties = [0.0] * len(places)
        
        for i, place in enumerate(places):
            penalty = travel_penalties[i] if i < len(travel_penalties) else 0.0
            self.calculate_composite_score(place, user_preferences, penalty)
        
        return places
    
    def get_top_scored_places(self, 
                             places: List[Place], 
                             n: int = 10) -> List[Place]:
        """
        获取得分最高的N个景点
        
        Args:
            places: 景点列表
            n: 返回的景点数量
            
        Returns:
            按得分排序的前N个景点
        """
        return sorted(places, key=lambda p: p.composite_score, reverse=True)[:n]
