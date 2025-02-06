from PIL import Image, ImageDraw
import os

def create_icon(color='gray'):
    # 确保目录存在
    os.makedirs('src/icon', exist_ok=True)
    
    # 创建一个 32x32 的图像
    img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 设置颜色
    if color == 'gray':
        fill_color = (128, 128, 128, 255)  # 灰色
    else:
        fill_color = (0, 255, 0, 255)  # 绿色
    
    # 画一个圆形
    draw.ellipse([2, 2, 30, 30], fill=fill_color)
    
    # 保存为图标文件
    img.save('src/icon/app_icon.ico', format='ICO', sizes=[(16, 16), (32, 32)])

if __name__ == '__main__':
    create_icon() 