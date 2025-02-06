from PIL import Image, ImageDraw, ImageFont
import os

class IconGenerator:
    @staticmethod
    def create_icon(color='gray', size=64):
        """
        生成系统托盘图标
        :param color: 图标颜色 (gray, green)
        :param size: 图标尺寸
        :return: PIL Image对象
        """
        icon = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(icon)
        
        # 根据颜色绘制不同状态的图标
        if color == 'green':
            draw.ellipse([10, 10, size-10, size-10], fill=(0, 255, 0, 200))
        else:
            draw.ellipse([10, 10, size-10, size-10], fill=(128, 128, 128, 200))
        
        # 添加小盾牌图案
        draw.polygon(
            [(size//2, size//4), (size//4, size*3//4), (size*3//4, size*3//4)], 
            fill=(255, 255, 255, 180)
        )
        
        return icon

    @staticmethod
    def save_icon(icon, filename='icon.png'):
        """
        保存图标到文件
        :param icon: PIL Image对象
        :param filename: 保存的文件名
        """
        icon_dir = os.path.join(os.path.dirname(__file__), '..', 'icons')
        os.makedirs(icon_dir, exist_ok=True)
        icon.save(os.path.join(icon_dir, filename))

# 示例使用
if __name__ == '__main__':
    gray_icon = IconGenerator.create_icon('gray')
    green_icon = IconGenerator.create_icon('green')
    
    IconGenerator.save_icon(gray_icon, 'gray_icon.png')
    IconGenerator.save_icon(green_icon, 'green_icon.png')
