"""
Google Maps Distance Matrix API 封装
实现队友设计中的实时数据集成和预测建模
"""

import requests
import os
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ..models.place import Place


class GoogleMapsAPI:
    """Google Maps Distance Matrix API 封装类"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_MAPS_API_KEY")
        if not self.api_key:
            raise ValueError("Google Maps API key is required")
        
        self.base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    
    def get_travel_time_matrix(self, 
                              places: List[Place], 
                              mode: str = "walking",
                              departure_time: Optional[datetime] = None,
                              traffic_model: str = "best_guess") -> List[List[Dict[str, Any]]]:
        """
        获取景点间的旅行时间矩阵
        实现队友设计中的实时数据集成
        
        Args:
            places: 景点列表
            mode: 交通方式 (walking, driving, bicycling, transit)
            departure_time: 出发时间（用于考虑交通状况）
            traffic_model: 交通模型 (best_guess, pessimistic, optimistic)
            
        Returns:
            旅行时间矩阵
        """
        if not places:
            return []
        
        # 构建位置字符串
        locations = [f"{place.location.lat},{place.location.lng}" for place in places]
        origins = "|".join(locations)
        destinations = origins  # 全对全矩阵
        
        params = {
            "origins": origins,
            "destinations": destinations,
            "mode": mode,
            "key": self.api_key,
            "units": "metric"
        }
        
        # 队友设计：考虑交通模式和时间变化
        if mode == "driving" and departure_time:
            params["departure_time"] = int(departure_time.timestamp())
            params["traffic_model"] = traffic_model
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "OK":
                error_msg = data.get("error_message", "Unknown error")
                print(f"Distance Matrix API Error: {data.get('status')} - {error_msg}")
                return []
            
            return self._parse_matrix_response(data, places)
            
        except requests.RequestException as e:
            print(f"Error fetching travel times: {e}")
            return []
        except Exception as e:
            print(f"Error parsing distance matrix response: {e}")
            return []
    
    def _parse_matrix_response(self, data: dict, places: List[Place]) -> List[List[Dict[str, Any]]]:
        """解析距离矩阵API响应"""
        matrix = []
        
        for i, row in enumerate(data.get("rows", [])):
            matrix_row = []
            
            for j, element in enumerate(row.get("elements", [])):
                if element["status"] == "OK":
                    travel_info = {
                        "duration_seconds": element["duration"]["value"],
                        "duration_minutes": element["duration"]["value"] / 60,
                        "distance_meters": element["distance"]["value"],
                        "from_place": places[i].name if i < len(places) else "Unknown",
                        "to_place": places[j].name if j < len(places) else "Unknown",
                        "status": "OK"
                    }
                    
                    # 如果有交通信息（driving mode）
                    if "duration_in_traffic" in element:
                        travel_info["duration_in_traffic_seconds"] = element["duration_in_traffic"]["value"]
                        travel_info["duration_in_traffic_minutes"] = element["duration_in_traffic"]["value"] / 60
                else:
                    travel_info = {
                        "duration_seconds": float('inf'),
                        "duration_minutes": float('inf'),
                        "distance_meters": float('inf'),
                        "from_place": places[i].name if i < len(places) else "Unknown",
                        "to_place": places[j].name if j < len(places) else "Unknown",
                        "status": element["status"]
                    }
                
                matrix_row.append(travel_info)
            
            matrix.append(matrix_row)
        
        return matrix
    
    def get_travel_time_with_prediction(self, 
                                       place1: Place, 
                                       place2: Place,
                                       departure_time: Optional[datetime] = None,
                                       safety_buffer: float = 1.15) -> float:
        """
        获取两个景点间的预测旅行时间
        实现队友设计中的预测建模和安全缓冲
        
        Args:
            place1: 起点
            place2: 终点
            departure_time: 出发时间
            safety_buffer: 安全缓冲系数（默认15%）
            
        Returns:
            预测旅行时间（分钟）
        """
        if departure_time is None:
            departure_time = datetime.now()
        
        # 获取单次查询的旅行时间
        matrix = self.get_travel_time_matrix([place1, place2], 
                                           departure_time=departure_time)
        
        if matrix and len(matrix) > 0 and len(matrix[0]) > 1:
            base_time = matrix[0][1]["duration_minutes"]
            
            # 应用安全缓冲
            predicted_time = base_time * safety_buffer
            
            return predicted_time
        
        return float('inf')
    
    def get_optimal_departure_times(self, 
                                   places: List[Place], 
                                   start_time: datetime,
                                   visit_duration: int = 60) -> Dict[str, datetime]:
        """
        计算各景点的最优出发时间
        考虑交通模式优化
        
        Args:
            places: 景点列表
            start_time: 开始时间
            visit_duration: 每个景点的访问时长
            
        Returns:
            各景点的建议出发时间
        """
        optimal_times = {}
        current_time = start_time
        
        for i, place in enumerate(places):
            optimal_times[place.name] = current_time
            current_time += timedelta(minutes=visit_duration)
        
        return optimal_times
