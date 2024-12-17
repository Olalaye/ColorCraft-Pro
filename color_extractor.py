import cv2
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import os

def rgb_to_hex(color, alpha=255):
    """将RGB颜色转换为HEX代码，支持透明度"""
    return "#{:02x}{:02x}{:02x}{:02x}".format(*color, alpha)

def hex_to_rgb(hex_color):
    """将HEX颜色代码转换为RGB"""
    hex_color = hex_color.lstrip('#')
    lv = len(hex_color)
    return tuple(int(hex_color[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def color_psychology(hsv_color):
    """提供色彩心理学推荐"""
    hue = hsv_color[0]
    if 0 <= hue < 30 or 330 <= hue <= 360:
        return "Warmth, Energy, Passion (Red tones)"
    elif 30 <= hue < 90:
        return "Optimism, Happiness, Creativity (Yellow tones)"
    elif 90 <= hue < 150:
        return "Nature, Growth, Calmness (Green tones)"
    elif 150 <= hue < 210:
        return "Trust, Serenity, Peace (Blue tones)"
    elif 210 <= hue < 270:
        return "Luxury, Mystery, Spirituality (Purple tones)"
    else:
        return "Neutral, Balance, Simplicity (Gray tones)"

def generate_css_content(sorted_colors):
    """生成CSS内容的辅助函数"""
    css_content = []
    css_content.append("/* 自动生成的调色板CSS变量 */")
    css_content.append(":root {")
    
    # 基础颜色变量
    for i, color in enumerate(sorted_colors):
        css_content.append(f"    --color-{i + 1}: {rgb_to_hex(color)};")
    
    # 语义化颜色变量
    css_content.extend([
        "\n    /* 语义化颜色变量 */",
        f"    --color-primary: {rgb_to_hex(sorted_colors[-1])};",
        f"    --color-secondary: {rgb_to_hex(sorted_colors[-2])};",
        f"    --color-accent: {rgb_to_hex(sorted_colors[0])};",
        f"    --color-background: {rgb_to_hex(sorted_colors[1])};",
        f"    --color-text: {rgb_to_hex(sorted_colors[-1])};",
    ])
    
    # 透明度变量
    css_content.append("\n    /* 透明度变量 */")
    for alpha in [90, 75, 50, 25, 10]:
        css_content.append(f"    --opacity-{alpha}: {alpha}%;")
    
    # 间距和圆角变量
    css_content.extend([
        "\n    /* 间距变量 */",
        "    --spacing-xs: 0.25rem;",
        "    --spacing-sm: 0.5rem;",
        "    --spacing-md: 1rem;",
        "    --spacing-lg: 1.5rem;",
        "    --spacing-xl: 2rem;",
        "\n    /* 圆角变量 */",
        "    --radius-sm: 0.25rem;",
        "    --radius-md: 0.5rem;",
        "    --radius-lg: 1rem;",
        "    --radius-full: 9999px;",
    ])
    
    css_content.append("}\n")
    
    # 实用类
    css_content.append("/* 颜色实用类 */")
    for i, color in enumerate(sorted_colors):
        class_name = f"color-{i + 1}"
        css_content.extend([
            f".bg-{class_name} {{ background-color: var(--color-{i + 1}); }}",
            f".text-{class_name} {{ color: var(--color-{i + 1}); }}",
            f".border-{class_name} {{ border-color: var(--color-{i + 1}); }}",
            f".hover\\:bg-{class_name}:hover {{ background-color: var(--color-{i + 1}); }}",
        ])
    
    # 语义化类
    css_content.append("\n/* 语义化类 */")
    semantic_classes = ["primary", "secondary", "accent", "background", "text"]
    for class_name in semantic_classes:
        css_content.extend([
            f".bg-{class_name} {{ background-color: var(--color-{class_name}); }}",
            f".text-{class_name} {{ color: var(--color-{class_name}); }}",
            f".border-{class_name} {{ border-color: var(--color-{class_name}); }}",
            f".hover\\:bg-{class_name}:hover {{ background-color: var(--color-{class_name}); }}",
        ])
    
    # 布局实用类
    css_content.extend([
        "\n/* 布局实用类 */",
        ".flex { display: flex; }",
        ".flex-col { flex-direction: column; }",
        ".items-center { align-items: center; }",
        ".justify-center { justify-content: center; }",
        ".gap-sm { gap: var(--spacing-sm); }",
        ".gap-md { gap: var(--spacing-md); }",
        ".p-sm { padding: var(--spacing-sm); }",
        ".p-md { padding: var(--spacing-md); }",
        ".rounded-sm { border-radius: var(--radius-sm); }",
        ".rounded-md { border-radius: var(--radius-md); }",
    ])
    
    return "\n".join(css_content)

def generate_html_content(sorted_colors):
    """生成HTML内容的辅助函数"""
    html_content = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "    <title>Color Palette</title>",
        "    <link rel='stylesheet' href='color_palette.css'>",
        "</head>",
        "<body class='flex flex-col gap-md p-md'>",
        "    <h1 class='text-primary'>提取的配色方案</h1>",
        "    <div class='flex flex-col gap-sm'>"
    ]
    
    for i, color in enumerate(sorted_colors):
        hex_code = rgb_to_hex(color)
        html_content.append(
            f'    <div class="flex items-center bg-color-{i + 1} rounded-md p-md">'
            f'        <span class="text-white">{hex_code}</span>'
            f'    </div>'
        )
    
    html_content.extend([
        "    </div>",
        "</body>",
        "</html>"
    ])
    
    return "\n".join(html_content)

def extract_and_sort_colors(image_path, num_colors=5, output_folder="output"):
    """提取颜色并按亮度排序，保存颜色卡和UI设计预览"""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 加载图像并转换为RGB
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_resized = image.reshape((-1, 3))

    # KMeans提取颜色
    kmeans = KMeans(n_clusters=num_colors, random_state=0)
    kmeans.fit(image_resized)
    colors = kmeans.cluster_centers_.astype(int)

    # 转换HSV颜色并排序（按亮度递增排序）
    hsv_colors = [cv2.cvtColor(np.uint8([[color]]), cv2.COLOR_RGB2HSV)[0][0] for color in colors]
    sorted_indices = sorted(range(len(hsv_colors)), key=lambda i: hsv_colors[i][2])
    sorted_colors = [colors[i] for i in sorted_indices]

    # 保存颜色卡图像
    color_card_path = os.path.join(output_folder, "color_card.png")
    plt.figure(figsize=(10, 2))
    for i, color in enumerate(sorted_colors):
        plt.gca().add_patch(Rectangle((i, 0), 1, 1, color=np.array(color) / 255))
        plt.text(i + 0.5, -0.5, rgb_to_hex(color), ha='center', fontsize=10)
    plt.xlim(0, len(sorted_colors))
    plt.ylim(0, 1)
    plt.axis('off')
    plt.title("Sorted Color Card")
    plt.savefig(color_card_path)
    plt.close()

    # 输出HEX代码和色彩心理学推荐
    hex_colors = [rgb_to_hex(color) for color in sorted_colors]
    print("提取的排序配色方案 (HEX代码):")
    for i, (color, hsv) in enumerate(zip(sorted_colors, [hsv_colors[i] for i in sorted_indices])):
        print(f"Color {i+1}: {rgb_to_hex(color)} - {color_psychology(hsv)}")

    # UI设计预览
    ui_preview_path = os.path.join(output_folder, "ui_preview.png")
    plt.figure(figsize=(6, 8))
    for i, color in enumerate(sorted_colors):
        plt.fill_betweenx([i, i+1], 0, 6, color=np.array(color) / 255)
        plt.text(3, i + 0.5, f"{rgb_to_hex(color)}", ha='center', va='center', fontsize=12, 
                 color='white' if np.mean(color) < 128 else 'black')
    plt.xlim(0, 6)
    plt.ylim(0, len(sorted_colors))
    plt.axis('off')
    plt.title("UI Preview with Sorted Colors")
    plt.savefig(ui_preview_path)
    plt.close()

    # 生成并保存CSS文件
    css_file_path = os.path.join(output_folder, "color_palette.css")
    with open(css_file_path, "w", encoding="utf-8") as f:
        f.write(generate_css_content(sorted_colors))
    
    # 生成并保存HTML文件
    html_file_path = os.path.join(output_folder, "color_palette.html")
    with open(html_file_path, "w", encoding="utf-8") as f:
        f.write(generate_html_content(sorted_colors))
    
    print(f"\nCSS样式表已保存至: {css_file_path}")
    print(f"HTML样式表已保存至: {html_file_path}")
    print(f"颜色卡已保存至: {color_card_path}")
    print(f"UI设计预览已保存至: {ui_preview_path}")
    
    return sorted_colors