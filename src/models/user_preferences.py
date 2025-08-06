"""
User Preferences Data Model
实现队友设计中的用户偏好系统
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict


class TravelStyle(Enum):
    """预设旅行风格"""
    QUALITY_EXPLORER = "quality_explorer"
    EFFICIENT_TOURIST = "efficient_tourist"
    BALANCED_TRAVELER = "balanced_traveler"
    CUSTOM = "custom"


class PreferenceCategory(Enum):
    """偏好类别"""
    ART = "art"
    FOOD = "food"
    NATURE = "nature"
    SHOPPING = "shopping"
    CULTURE = "culture"
    ENTERTAINMENT = "entertainment"


@dataclass
class UserPreferences:
    """
    用户偏好数据类
    实现队友设计文档中的用户偏好方法
    """
    
    # 权重参数（队友设计的核心）
    weight_rating: float = 0.4      # 景点质量权重
    weight_preference: float = 0.4   # 用户偏好权重  
    weight_travel: float = 0.2       # 旅行惩罚权重
    
    # 旅行风格
    travel_style: TravelStyle = TravelStyle.BALANCED_TRAVELER
    
    # 偏好类别权重
    category_preferences: Dict[PreferenceCategory, float] = None
    
    def __post_init__(self):
        """初始化默认偏好"""
        if self.category_preferences is None:
            self.category_preferences = {
                PreferenceCategory.ART: 0.3,
                PreferenceCategory.FOOD: 0.2,
                PreferenceCategory.NATURE: 0.2,
                PreferenceCategory.CULTURE: 0.2,
                PreferenceCategory.SHOPPING: 0.05,
                PreferenceCategory.ENTERTAINMENT: 0.05,
            }
        
        # 根据旅行风格调整权重
        self._adjust_weights_by_style()
    
    def _adjust_weights_by_style(self):
        """根据旅行风格调整权重"""
        if self.travel_style == TravelStyle.QUALITY_EXPLORER:
            self.weight_rating = 0.6
            self.weight_preference = 0.3
            self.weight_travel = 0.1
        
        elif self.travel_style == TravelStyle.EFFICIENT_TOURIST:
            self.weight_rating = 0.2
            self.weight_preference = 0.3
            self.weight_travel = 0.5
            
        elif self.travel_style == TravelStyle.BALANCED_TRAVELER:
            self.weight_rating = 0.4
            self.weight_preference = 0.4
            self.weight_travel = 0.2
    
    def get_category_weight(self, category: PreferenceCategory) -> float:
        """获取特定类别的偏好权重"""
        return self.category_preferences.get(category, 0.0)
    
    def set_category_weight(self, category: PreferenceCategory, weight: float):
        """设置特定类别的偏好权重"""
        self.category_preferences[category] = max(0.0, min(1.0, weight))
        
    def normalize_category_weights(self):
        """归一化类别权重，确保总和为1"""
        total = sum(self.category_preferences.values())
        if total > 0:
            for category in self.category_preferences:
                self.category_preferences[category] /= total
    
    def validate_weights(self) -> bool:
        """验证权重设置是否合理"""
        total_main_weights = self.weight_rating + self.weight_preference + self.weight_travel
        return abs(total_main_weights - 1.0) < 0.01  # 允许小的浮点误差
