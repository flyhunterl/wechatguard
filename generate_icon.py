from PIL import Image, ImageDraw

def create_icon():
    # 创建一个 256x256 的图像（常用的图标尺寸）
    size = 256
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # 绘制一个简单的图标
    # 这里可以根据您的需求修改图标的样式
    margin = size // 8
    draw.rectangle(
        [margin, margin, size - margin, size - margin],
        fill='#1E90FF',  # 使用深蓝色
        outline='#4169E1',
        width=2
    )
    
    # 确保目录存在
    import os
    os.makedirs('src/icon', exist_ok=True)
    
    # 保存为 ICO 文件
    image.save('src/icon/app_icon.ico', format='ICO')

if __name__ == '__main__':
    create_icon() 