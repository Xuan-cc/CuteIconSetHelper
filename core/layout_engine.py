"""
排布算法引擎
"""
from PIL import Image
import typing as tp
import math
from core.image_processor import ImageProcessor


class LayoutEngine:
    """排布算法引擎"""
    
    def __init__(self):
        self.processor = ImageProcessor()
    
    def horizontal_layout(self, images: tp.List[Image.Image]) -> Image.Image:
        """
        横排布局
        图片水平排列，高度相同，总宽度 = 单张宽度 * 数量
        
        Args:
            images: 图片列表
        
        Returns:
            拼接后的图片
        """
        if not images:
            return None
        
        if len(images) == 1:
            return images[0].copy()
        
        # 获取单张图片尺寸（假设所有图片尺寸相同）
        tile_width = images[0].width
        tile_height = images[0].height
        
        # 计算总尺寸
        total_width = tile_width * len(images)
        total_height = tile_height
        
        # 创建画布
        canvas = self.processor.create_transparent_canvas(total_width, total_height)
        
        # 水平排列
        for i, img in enumerate(images):
            x = i * tile_width
            y = 0
            self.processor.paste_image(canvas, img, x, y, anchor="tl")
        
        return canvas
    
    def vertical_layout(self, images: tp.List[Image.Image]) -> Image.Image:
        """
        竖排布局
        图片垂直排列，宽度相同，总高度 = 单张高度 * 数量
        
        Args:
            images: 图片列表
        
        Returns:
            拼接后的图片
        """
        if not images:
            return None
        
        if len(images) == 1:
            return images[0].copy()
        
        # 获取单张图片尺寸
        tile_width = images[0].width
        tile_height = images[0].height
        
        # 计算总尺寸
        total_width = tile_width
        total_height = tile_height * len(images)
        
        # 创建画布
        canvas = self.processor.create_transparent_canvas(total_width, total_height)
        
        # 垂直排列
        for i, img in enumerate(images):
            x = 0
            y = i * tile_height
            self.processor.paste_image(canvas, img, x, y, anchor="tl")
        
        return canvas
    
    def circular_layout(self, images: tp.List[Image.Image]) -> Image.Image:
        """
        圆形排布
        图片围绕中心点环形排列，自动缩放以避免重叠
        
        Args:
            images: 图片列表
        
        Returns:
            排布后的图片
        """
        if not images:
            return None
        
        if len(images) == 1:
            return images[0].copy()
        
        n = len(images)
        tile_width = images[0].width
        tile_height = images[0].height
        
        # 输出尺寸固定为256x256（与单张相同）
        output_size = tile_width
        center_x = output_size // 2
        center_y = output_size // 2
        
        # 计算缩放比例和排列半径
        if n == 2:
            # 两张图片：180度间隔
            angle_step = 180
            # 计算合适的缩放比例和半径
            scale, radius = self._calculate_circular_params(
                tile_width, tile_height, n, output_size
            )
        else:
            # 三张或更多：360/n度间隔
            angle_step = 360 / n
            scale, radius = self._calculate_circular_params(
                tile_width, tile_height, n, output_size
            )
        
        # 创建画布
        canvas = self.processor.create_transparent_canvas(output_size, output_size)
        
        # 排列图片
        for i, img in enumerate(images):
            # 计算角度（从0度开始，顺时针）
            angle = i * angle_step  # 0度使第一张在右侧（3点钟方向）
            
            # 计算位置
            rad = math.radians(angle)
            x = center_x + radius * math.cos(rad)
            y = center_y + radius * math.sin(rad)
            
            # 缩放图片
            if scale < 1.0:
                new_width = int(tile_width * scale)
                new_height = int(tile_height * scale)
                scaled_img = self.processor.resize_image(img, new_width, new_height)
            else:
                scaled_img = img.copy()
            
            # 粘贴到画布（中心对齐）
            self.processor.paste_image(canvas, scaled_img, int(x), int(y), anchor="c")
        
        return canvas
    
    def _calculate_circular_params(
        self,
        tile_width: int,
        tile_height: int,
        n: int,
        output_size: int
    ) -> tp.Tuple[float, float]:
        """
        计算圆形排布的参数
        
        目标：找到合适的缩放比例和半径，使得图片不重叠且尽可能大
        
        Args:
            tile_width: 单张图片宽度
            tile_height: 单张图片高度
            n: 图片数量
            output_size: 输出画布尺寸
        
        Returns:
            (缩放比例, 排列半径)
        """
        # 使用二分法寻找最大缩放比例
        min_scale = 0.1
        max_scale = 1.0
        best_scale = min_scale
        best_radius = 0
        
        # 迭代优化
        for _ in range(50):  # 迭代次数
            scale = (min_scale + max_scale) / 2
            
            # 计算缩放后的图片尺寸
            scaled_w = tile_width * scale
            scaled_h = tile_height * scale
            
            # 计算半对角线长度（从中心到角落）
            half_diagonal = math.sqrt(scaled_w**2 + scaled_h**2) / 2
            
            # 计算需要的角度间隔（考虑图片本身占用的角度）
            if n == 2:
                # 两张图片：需要至少180度的可视间隔
                # 简化计算：确保图片不接触
                required_angle = 180  # 度
            else:
                # 360/n度的间隔，但图片有宽度
                # 计算图片在圆环上占用的角度
                chord = math.sqrt(scaled_w**2 + scaled_h**2)  # 图片对角线作为弦长
                required_angle = 360 / n
            
            # 计算最小半径（确保图片在画布内且不重叠）
            # 图片中心到画布边缘需要留margin
            margin = half_diagonal
            max_radius = (output_size / 2) - margin
            
            # 根据角度间隔计算半径
            # 弦长 = 2 * r * sin(θ/2)
            # 其中弦长是图片对角线，θ是角度间隔
            angle_rad = math.radians(required_angle)
            
            # 确保图片不重叠的最小半径
            if n == 2:
                # 两张图片相对排列
                # 图片中心间距 = 2 * radius
                # 需要大于 2 * half_diagonal
                min_radius = half_diagonal
            else:
                # 多张图片环形排列
                # 相邻图片中心的最小距离
                min_distance = 2 * half_diagonal
                # 弦长 = min_distance
                if math.sin(angle_rad / 2) > 0:
                    min_radius = min_distance / (2 * math.sin(angle_rad / 2))
                else:
                    min_radius = 0
            
            # 检查可行性
            if min_radius <= max_radius:
                # 可行，尝试更大的缩放
                best_scale = scale
                best_radius = min(min_radius * 0.9, max_radius * 0.9)  # 留一些余量
                min_scale = scale
            else:
                # 不可行，需要缩小
                max_scale = scale
        
        return best_scale, best_radius
