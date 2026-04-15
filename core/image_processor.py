"""
图像处理核心模块
"""
from PIL import Image
import typing as tp


class ImageProcessor:
    """图像处理器"""
    
    @staticmethod
    def resize_image(
        image: Image.Image,
        target_width: int,
        target_height: int,
        resample: int = Image.Resampling.LANCZOS
    ) -> Image.Image:
        """
        缩放图片到目标尺寸
        
        Args:
            image: 原始图片
            target_width: 目标宽度
            target_height: 目标高度
            resample: 重采样算法，默认LANCZOS（高质量）
        
        Returns:
            缩放后的图片
        """
        # 转换为RGBA模式以保留透明通道
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # 使用LANCZOS重采样（类似线性插值但质量更高）
        resized = image.resize((target_width, target_height), resample)
        return resized
    
    @staticmethod
    def crop_to_square(image: Image.Image, x: int, y: int, size: int) -> Image.Image:
        """
        从图片中裁剪出正方形区域
        
        Args:
            image: 原始图片
            x: 左上角x坐标
            y: 左上角y坐标
            size: 裁剪区域边长
        
        Returns:
            裁剪后的正方形图片
        """
        return image.crop((x, y, x + size, y + size))
    
    @staticmethod
    def auto_crop_to_square(image: Image.Image) -> Image.Image:
        """
        自动居中裁剪为1:1正方形
        
        Args:
            image: 原始图片
        
        Returns:
            裁剪后的正方形图片
        """
        width, height = image.size
        size = min(width, height)
        x = (width - size) // 2
        y = (height - size) // 2
        return image.crop((x, y, x + size, y + size))
    
    @staticmethod
    def create_transparent_canvas(width: int, height: int) -> Image.Image:
        """
        创建透明画布
        
        Args:
            width: 画布宽度
            height: 画布高度
        
        Returns:
            RGBA透明画布
        """
        return Image.new('RGBA', (width, height), (0, 0, 0, 0))
    
    @staticmethod
    def paste_image(
        canvas: Image.Image,
        image: Image.Image,
        x: int,
        y: int,
        anchor: str = "tl"
    ) -> Image.Image:
        """
        将图片粘贴到画布上
        
        Args:
            canvas: 目标画布
            image: 要粘贴的图片
            x: 粘贴位置x坐标
            y: 粘贴位置y坐标
            anchor: 锚点位置，'tl'=左上, 'c'=中心
        
        Returns:
            粘贴后的画布
        """
        if anchor == "c":
            x = x - image.width // 2
            y = y - image.height // 2
        
        # 使用alpha通道进行粘贴
        canvas.paste(image, (x, y), image)
        return canvas
    
    @staticmethod
    def rotate_image(image: Image.Image, angle: float, expand: bool = False) -> Image.Image:
        """
        旋转图片
        
        Args:
            image: 原始图片
            angle: 旋转角度（度）
            expand: 是否扩展画布以适应旋转后的图片
        
        Returns:
            旋转后的图片
        """
        # 使用LANCZOS重采样进行旋转
        return image.rotate(
            angle,
            resample=Image.Resampling.LANCZOS,
            expand=expand,
            fillcolor=(0, 0, 0, 0)  # 透明背景
        )
