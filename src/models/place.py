"""
Place Data Model
景点数据模型，包含队友设计中需要的所有属性
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set
from .user_preferences import PreferenceCategory


@dataclass
class Location:
    """地理位置"""
    lat: float
    lng: float


@dataclass 
class Place:
    """
    景点数据类
    包含队友算法设计所需的所有属性
    """
    
    # 基础信息
    name: str
    address: str
    place_id: str
    location: Location
    
    # Google Places API 数据
    rating: float = 0.0
    user_ratings_total: int = 0
    place_types: List[str] = None
    
    # 计算得出的属性
    visit_time: int = 30  # 建议访问时间（分钟）
    categories: Set[PreferenceCategory] = None  # 景点类别
    
    # 队友算法所需的属性
    interest_score: float = 0.0       # 基础兴趣分数
    composite_score: float = 0.0      # 综合得分
    travel_penalty: float = 0.0       # 旅行惩罚值
    
    def __post_init__(self):
        """初始化默认值"""
        if self.place_types is None:
            self.place_types = []
        
        if self.categories is None:
            self.categories = set()
            self._categorize_place()
        
        # 计算基础兴趣分数
        self._calculate_base_interest()
    
    def _categorize_place(self):
        """根据place_types自动分类景点"""
        type_mapping = {
            # 艺术文化类
            'art_gallery': PreferenceCategory.ART,
            'museum': PreferenceCategory.ART,
            'cultural_center': PreferenceCategory.CULTURE,
            'historical_site': PreferenceCategory.CULTURE,
            'church': PreferenceCategory.CULTURE,
            'synagogue': PreferenceCategory.CULTURE,
            'mosque': PreferenceCategory.CULTURE,
            
            # 美食类
            'restaurant': PreferenceCategory.FOOD,
            'food': PreferenceCategory.FOOD,
            'cafe': PreferenceCategory.FOOD,
            'bakery': PreferenceCategory.FOOD,
            'meal_takeaway': PreferenceCategory.FOOD,
            
            # 自然类
            'park': PreferenceCategory.NATURE,
            'natural_feature': PreferenceCategory.NATURE,
            'zoo': PreferenceCategory.NATURE,
            'aquarium': PreferenceCategory.NATURE,
            'beach': PreferenceCategory.NATURE,
            
            # 购物类
            'shopping_mall': PreferenceCategory.SHOPPING,
            'store': PreferenceCategory.SHOPPING,
            'clothing_store': PreferenceCategory.SHOPPING,
            
            # 娱乐类
            'amusement_park': PreferenceCategory.ENTERTAINMENT,
            'movie_theater': PreferenceCategory.ENTERTAINMENT,
            'night_club': PreferenceCategory.ENTERTAINMENT,
            'casino': PreferenceCategory.ENTERTAINMENT,
        }
        
        for place_type in self.place_types:
            if place_type in type_mapping:
                self.categories.add(type_mapping[place_type])
        
        # 如果没有匹配到类别，默认为文化类
        if not self.categories:
            self.categories.add(PreferenceCategory.CULTURE)
    
    def _calculate_base_interest(self):
        """计算基础兴趣分数"""
        # 基于评分和评价数量计算
        rating_score = self.rating * 2  # 0-10分制
        
        # 评价数量影响（对数缩放）
        import math
        if self.user_ratings_total > 0:
            popularity_score = min(2.0, math.log10(self.user_ratings_total))
        else:
            popularity_score = 0
        
        self.interest_score = rating_score + popularity_score
        
        # 根据访问时间调整（时间越长，可能越有趣）
        time_factor = min(1.2, self.visit_time / 30)
        self.interest_score *= time_factor
    
    def has_category(self, category: PreferenceCategory) -> bool:
        """检查是否属于特定类别"""
        return category in self.categories
    
    def get_primary_category(self) -> Optional[PreferenceCategory]:
        """获取主要类别"""
        if self.categories:
            return next(iter(self.categories))
        return None
    
    def update_visit_time(self, new_time: int):
        """更新访问时间并重新计算兴趣分数"""
        self.visit_time = max(15, min(180, new_time))  # 限制在15-180分钟
        self._calculate_base_interest()
