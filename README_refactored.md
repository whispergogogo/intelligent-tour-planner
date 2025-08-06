# 🌟 Intelligent Tour Planner (重构版)

基于队友算法设计的智能旅游规划器，实现了增强背包算法和两阶段路径优化。

## 🧠 核心算法

### Step 1: Variant Knapsack for Interdependent Travel Attraction Costs
- **综合评分系统**: `attraction_score = (review_rating × weight_rating) + (preference_match_score × weight_preference) - (travel_penalty × weight_travel)`
- **用户偏好方法**: 预设旅行风格 + 类别偏好权重
- **Top-N旅行惩罚**: 鼓励选择连通性好的景点簇
- **位置感知背包**: 迭代贪心，考虑从当前位置的效率得分

### Step 2: Two-Phase Heuristic Route Optimization
- **最近邻初始化**: 构建初始可行路径
- **2-Opt局部搜索**: 消除路径交叉，优化旅行时间
- **实时数据集成**: Google Maps API + 交通预测
- **预测建模**: 历史模型 + 安全缓冲

## 🏗️ 项目架构

```
src/
├── models/                 # 数据模型
│   ├── place.py           # 景点数据类
│   └── user_preferences.py # 用户偏好系统
├── api/                    # API封装层
│   ├── google_places.py   # Google Places API
│   └── google_maps.py     # Distance Matrix API
├── algorithms/             # 核心算法模块
│   ├── scoring.py         # 综合评分系统
│   ├── travel_penalty.py  # 旅行惩罚计算
│   ├── enhanced_knapsack.py # 增强背包算法
│   └── route_optimizer.py # 路径优化算法
├── core/                   # 业务逻辑层
│   └── tour_planner.py    # 主要协调器
└── utils/                  # 工具模块
    ├── input_handler.py   # 用户输入处理
    └── output_formatter.py # 结果格式化
```

## 🚀 快速开始

### 1. 环境设置
```bash
# 克隆项目
git clone <repository-url>
cd intelligent-tour-planner

# 安装依赖
pip install -r requirements.txt

# 设置API密钥
export GOOGLE_MAPS_API_KEY="your_api_key_here"
```

### 2. 运行方式

#### 交互式界面
```bash
python3 main_refactored.py
```

#### 编程接口
```python
from src.core.tour_planner import IntelligentTourPlanner
from src.models.user_preferences import UserPreferences, TravelStyle

# 创建规划器
planner = IntelligentTourPlanner(api_key="your_key")

# 设置用户偏好
user_prefs = UserPreferences()
user_prefs.travel_style = TravelStyle.BALANCED_TRAVELER

# 执行规划
result = planner.plan_tour(
    city="Vancouver",
    user_preferences=user_prefs,
    time_limit=300,  # 5小时
    travel_mode="walking"
)

# 处理结果
if result["success"]:
    print(f"选中 {len(result['selected_places'])} 个景点")
    print(f"总得分: {result['statistics']['total_composite_score']:.2f}")
```

### 3. 测试系统
```bash
# 基础算法测试
python3 test_refactor.py

# 完整系统测试
python3 test_complete_system.py
```

## 🎯 用户偏好系统

### 旅行风格
- **品质探索者**: 重视景点质量和评分
- **高效游客**: 优化时间效率和旅行路径
- **平衡旅行者**: 平衡质量、偏好和效率
- **自定义**: 手动设置算法权重

### 类别偏好
- 🎨 **艺术类**: 博物馆、画廊
- 🍽️ **美食类**: 餐厅、市场
- 🌳 **自然类**: 公园、海滩
- 🏛️ **文化类**: 历史遗迹、建筑
- 🛍️ **购物类**: 商场、商店
- 🎭 **娱乐类**: 游乐园、剧院

## 📊 算法性能

### 复杂度分析
- **时间复杂度**: O(n²) - 避免指数级状态空间
- **空间复杂度**: O(n) - 高效内存使用
- **扩展性**: 支持100+景点的实时规划

### 性能指标
- **选择效率**: 综合得分/时间消耗
- **路径优化**: 2-Opt改进程度
- **用户满意度**: 偏好匹配程度

## 🔬 测试结果示例

```
🎉 Vancouver (测试) 旅游规划完成！
============================================================
📊 规划算法: 队友设计的两阶段算法
⏱️ 规划耗时: 0.1 秒
🎯 旅行风格: balanced_traveler

🧠 算法性能分析
----------------------------------------
📦 Step 1 - 增强背包算法:
  候选景点: 5 个
  选中景点: 3 个
  综合得分: 12.64
  选择效率: 0.060 得分/分钟

🛣️ Step 2 - 路径优化:
  算法: Two-Phase Heuristic (Nearest Neighbor + 2-Opt)
  路径改进: 15.2%

🏛️ 选中的景点 (3 个)
----------------------------------------
1. Stanley Park - 4.6⭐ (90分钟)
2. Vancouver Art Gallery - 4.2⭐ (75分钟)  
3. Granville Island Market - 4.4⭐ (60分钟)
```

## 🛠️ 开发特性

### 代码质量
- ✅ 完全模块化设计
- ✅ 类型注解支持
- ✅ 全面错误处理
- ✅ 详细文档注释

### 测试覆盖
- ✅ 单元测试
- ✅ 集成测试  
- ✅ 算法比较测试
- ✅ 性能基准测试

### 扩展性
- ✅ 插件式算法架构
- ✅ 可配置评分权重
- ✅ 多交通方式支持
- ✅ 自定义景点类别

## 📈 相比原版的改进

| 特性 | 原版本 | 重构版本 |
|------|--------|----------|
| 代码行数 | 826行单文件 | 1000+行模块化 |
| 算法设计 | 简单背包+TSP | 增强背包+两阶段优化 |
| 用户偏好 | 无 | 完整偏好系统 |
| 评分算法 | rating×2 | 综合评分公式 |
| 路径优化 | 最近邻 | 最近邻+2-Opt |
| 可维护性 | 困难 | 高度模块化 |
| 测试覆盖 | 基础 | 全面测试套件 |

## 🔮 未来发展方向

1. **机器学习增强**: 用户行为学习和个性化推荐
2. **多目标优化**: 预算、天气、实时事件等约束
3. **可视化界面**: Web端和移动端应用
4. **社交功能**: 路线分享和社区评价
5. **实时调整**: GPS跟踪和动态重规划

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 联系

如有问题或建议，请联系项目维护者。

---
**基于队友算法设计，完全重构实现 🚀**
