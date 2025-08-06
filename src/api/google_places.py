"""
Google Places API 封装
从原main.py中提取并改进
"""

import requests
import os
from typing import List, Optional
from ..models.place import Place, Location


class GooglePlacesAPI:
    """Google Places API 封装类"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_MAPS_API_KEY")
        if not self.api_key:
            raise ValueError("Google Maps API key is required")
        
        self.base_url = "https://maps.googleapis.com/maps/api/place"
    
    def search_places(self, 
                     city: str = "Vancouver", 
                     place_type: str = "tourist_attraction", 
                     max_results: int = 10) -> List[Place]:
        """
        搜索景点
        
        Args:
            city: 城市名称
            place_type: 景点类型
            max_results: 最大结果数
            
        Returns:
            景点列表
        """
        url = f"{self.base_url}/textsearch/json"
        params = {
            "query": f"{place_type} in {city}",
            "key": self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "OK":
                error_msg = data.get("error_message", "Unknown error")
                print(f"API Error: {data.get('status')} - {error_msg}")
                return []
            
            places = []
            for result in data.get("results", [])[:max_results]:
                place = self._parse_place_result(result)
                if place:
                    places.append(place)
            
            return places
            
        except requests.RequestException as e:
            print(f"Error fetching places: {e}")
            return []
        except Exception as e:
            print(f"Error parsing API response: {e}")
            return []
    
    def _parse_place_result(self, result: dict) -> Optional[Place]:
        """解析API返回的景点数据"""
        try:
            location_data = result["geometry"]["location"]
            location = Location(
                lat=location_data["lat"],
                lng=location_data["lng"]
            )
            
            place = Place(
                name=result["name"],
                address=result["formatted_address"],
                place_id=result["place_id"],
                location=location,
                rating=result.get("rating", 0.0),
                user_ratings_total=result.get("user_ratings_total", 0),
                place_types=result.get("types", [])
            )
            
            # 估算访问时间
            place.visit_time = self._estimate_visit_time(place)
            
            return place
            
        except KeyError as e:
            print(f"Missing required field in API response: {e}")
            return None
    
    def _estimate_visit_time(self, place: Place) -> int:
        """
        估算景点访问时间
        改进原来的简单计算
        """
        base_time = 30
        
        # 根据景点类型调整
        if any(t in place.place_types for t in ['museum', 'art_gallery']):
            base_time = 60
        elif any(t in place.place_types for t in ['park', 'zoo', 'amusement_park']):
            base_time = 90
        elif any(t in place.place_types for t in ['restaurant', 'cafe']):
            base_time = 45
        elif any(t in place.place_types for t in ['shopping_mall', 'store']):
            base_time = 60
        
        # 根据评分调整（评分高的地方可能值得花更多时间）
        if place.rating >= 4.5:
            base_time = int(base_time * 1.2)
        elif place.rating >= 4.0:
            base_time = int(base_time * 1.1)
        elif place.rating < 3.0:
            base_time = int(base_time * 0.8)
        
        return max(15, min(180, base_time))  # 限制在15-180分钟
