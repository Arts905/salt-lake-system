from typing import List, Dict

class AHPCalculator:
    """
    AHP (Analytic Hierarchy Process) 计算器
    用于计算评价指标的权重
    """
    
    @staticmethod
    def calculate_weights(comp_at: float, comp_tc: float, comp_ac: float) -> Dict[str, float]:
        """
        计算权重
        
        Args:
            comp_at: 可达性 vs 主题性 (Accessibility vs Thematic)
            comp_tc: 主题性 vs 色彩性 (Thematic vs Colorfulness)
            comp_ac: 可达性 vs 色彩性 (Accessibility vs Colorfulness)
            
            值说明: 
            1: 同等重要
            3: 稍微重要
            5: 明显重要
            7: 强烈重要
            9: 极端重要
            (分数 1/3, 1/5 等代表反向重要)
            
        Returns:
            Dict containing 'accessibility', 'thematic', 'colorfulness' weights
        """
        
        # 构建矩阵
        #      A      T      C
        # A    1      AT     AC
        # T    1/AT   1      TC
        # C    1/AC   1/TC   1
        
        # 为了处理一致性，我们通常尽量使用传递性，但在用户输入场景下，
        # 我们直接使用用户输入的三个值构建矩阵（即使可能不完全一致）
        
        matrix = [
            [1.0,      comp_at,    comp_ac],
            [1.0/comp_at, 1.0,     comp_tc],
            [1.0/comp_ac, 1.0/comp_tc, 1.0]
        ]
        
        # 使用几何平均法计算权重 (Geometric Mean Method)
        # 这种方法对于3x3矩阵计算简单且效果好
        
        gm = [0.0] * 3
        for i in range(3):
            product = 1.0
            for j in range(3):
                product *= matrix[i][j]
            gm[i] = product ** (1.0/3.0)
            
        # 归一化
        total = sum(gm)
        weights = [x / total for x in gm]
        
        return {
            "accessibility": weights[0],
            "thematic": weights[1],
            "colorfulness": weights[2]
        }

    @staticmethod
    def calculate_score(attraction, weights: Dict[str, float]) -> float:
        """
        计算景点的综合得分
        """
        # 确保属性存在，如果不存在则给默认值 0.5
        a_score = getattr(attraction, 'accessibility_score', 0.5) or 0.5
        t_score = getattr(attraction, 'thematic_score', 0.5) or 0.5
        c_score = getattr(attraction, 'colorfulness_score', 0.5) or 0.5
        
        score = (
            weights['accessibility'] * a_score +
            weights['thematic'] * t_score +
            weights['colorfulness'] * c_score
        )
        return score
