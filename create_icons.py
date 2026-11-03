import math
import base64
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_app_icon():
    # Render at high resolution (1024x1024) with supersampling for ultra-crisp edges
    size = 1024
    img = Image.new('RGB', (size, size), color=(15, 23, 42)) # Slate 900
    draw = ImageDraw.Draw(img)

    # 1. Background Luxury Gradient (Deep Midnight Navy to Royal Indigo)
    top_color = (15, 23, 42)      # #0f172a
    bottom_color = (30, 27, 75)   # #1e1b4b
    for y in range(size):
        ratio = y / size
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        draw.line([(0, y), (size, y)], fill=(r, g, b))

    # 2. Golden ambient radial glow behind the ball
    glow_layer = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)
    cx, cy = size // 2, size // 2 - 20
    glow_radius = 420
    for r in range(glow_radius, 0, -8):
        alpha = int(45 * (1 - r / glow_radius)**1.8)
        glow_draw.ellipse(
            [(cx - r, cy - r), (cx + r, cy + r)],
            fill=(245, 158, 11, alpha) # Amber 500
        )
    img = Image.alpha_composite(img.convert('RGBA'), glow_layer).convert('RGB')
    draw = ImageDraw.Draw(img)

    # 3. 3D Golden Sphere (Lottery Ball)
    ball_radius = 330
    ball_cx, ball_cy = cx, cy

    # Render 3D shading with radial gradient offset toward top-left (specular highlight)
    ball_layer = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    ball_draw = ImageDraw.Draw(ball_layer)
    
    # Draw base dark gold rim
    ball_draw.ellipse(
        [(ball_cx - ball_radius, ball_cy - ball_radius), 
         (ball_cx + ball_radius, ball_cy + ball_radius)],
        fill=(180, 83, 9, 255) # Dark amber border
    )

    # Concentric gradient steps offset toward (ball_cx - 90, ball_cy - 90)
    light_x = ball_cx - 90
    light_y = ball_cy - 90
    max_d = ball_radius * 1.8
    for r in range(ball_radius - 6, 0, -3):
        frac = 1 - (r / (ball_radius - 6))
        # Color transition: Dark Amber (217, 119, 6) -> Rich Gold (245, 158, 11) -> Bright Yellow (254, 240, 138)
        if frac < 0.6:
            t = frac / 0.6
            cr = int(217 + (251 - 217) * t)
            cg = int(119 + (191 - 119) * t)
            cb = int(6 + (36 - 6) * t)
        else:
            t = (frac - 0.6) / 0.4
            cr = int(251 + (255 - 251) * t)
            cg = int(191 + (248 - 191) * t)
            cb = int(36 + (150 - 36) * t)
        
        # Center shifts toward light source
        curr_cx = int(ball_cx + (light_x - ball_cx) * frac * 0.5)
        curr_cy = int(ball_cy + (light_y - ball_cy) * frac * 0.5)
        ball_draw.ellipse(
            [(curr_cx - r, curr_cy - r), (curr_cx + r, curr_cy + r)],
            fill=(cr, cg, cb, 255)
        )

    # Specular white gloss on top-left
    spec_w, spec_h = 140, 90
    spec_x, spec_y = ball_cx - 140, ball_cy - 160
    spec_layer = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    spec_draw = ImageDraw.Draw(spec_layer)
    spec_draw.ellipse(
        [(spec_x - spec_w//2, spec_y - spec_h//2), (spec_x + spec_w//2, spec_y + spec_h//2)],
        fill=(255, 255, 255, 160)
    )
    spec_layer = spec_layer.filter(ImageFilter.GaussianBlur(radius=25))
    ball_layer = Image.alpha_composite(ball_layer, spec_layer)

    # 4. Center Inner White Circle (Standard official lotto ball badge)
    badge_radius = 160
    badge_layer = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    badge_draw = ImageDraw.Draw(badge_layer)
    
    # Shadow under inner circle
    badge_draw.ellipse(
        [(ball_cx - badge_radius - 4, ball_cy - badge_radius + 4),
         (ball_cx + badge_radius + 4, ball_cy + badge_radius + 12)],
        fill=(0, 0, 0, 60)
    )
    # White badge
    badge_draw.ellipse(
        [(ball_cx - badge_radius, ball_cy - badge_radius),
         (ball_cx + badge_radius, ball_cy + badge_radius)],
        fill=(255, 255, 255, 255),
        outline=(254, 215, 170, 255),
        width=6
    )
    ball_layer = Image.alpha_composite(ball_layer, badge_layer)

    # 5. Bold Typography: "7" (Lucky Lotto) and "AI" badge
    # Try Malgun Gothic or Arial
    font_path = r'C:\Windows\Fonts\arialbd.ttf'
    if not os.path.exists(font_path):
        font_path = r'C:\Windows\Fonts\malgunbd.ttf'
    
    font_large = ImageFont.truetype(font_path, 210)
    font_small = ImageFont.truetype(font_path, 54)
    font_bot = ImageFont.truetype(font_path, 62)

    text_layer = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_layer)

    # Draw Number "7" in center of white badge
    text = "7"
    bbox = font_large.getbbox(text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = ball_cx - tw // 2 - bbox[0]
    ty = ball_cy - th // 2 - bbox[1] - 10
    text_draw.text((tx, ty), text, font=font_large, fill=(180, 83, 9, 255)) # Dark Amber

    # 6. Sleek "AI" Badge Chip on Top-Right of ball
    ai_w, ai_h = 160, 74
    ai_x = ball_cx + 140
    ai_y = ball_cy - 240
    
    # AI badge shadow & background (Emerald / Gold gradient pill)
    badge_shape = [ai_x, ai_y, ai_x + ai_w, ai_y + ai_h]
    text_draw.rounded_rectangle(
        [ai_x + 3, ai_y + 5, ai_x + ai_w + 3, ai_y + ai_h + 5],
        radius=36,
        fill=(0, 0, 0, 90)
    )
    text_draw.rounded_rectangle(
        badge_shape,
        radius=36,
        fill=(16, 185, 129, 255), # Emerald 500
        outline=(255, 255, 255, 255),
        width=5
    )
    ai_text = "AI"
    ai_bbox = font_small.getbbox(ai_text)
    ai_tw = ai_bbox[2] - ai_bbox[0]
    ai_th = ai_bbox[3] - ai_bbox[1]
    text_draw.text(
        (ai_x + (ai_w - ai_tw)//2 - ai_bbox[0], ai_y + (ai_h - ai_th)//2 - ai_bbox[1]),
        ai_text,
        font=font_small,
        fill=(255, 255, 255, 255)
    )

    # 7. Bottom Elegant Title "LOTTO 6/45"
    bot_text = "LOTTO 6/45"
    bot_bbox = font_bot.getbbox(bot_text)
    bot_tw = bot_bbox[2] - bot_bbox[0]
    bot_tx = (size - bot_tw) // 2 - bot_bbox[0]
    bot_ty = size - 130

    # Glow under text
    text_draw.text((bot_tx, bot_ty + 2), bot_text, font=font_bot, fill=(0, 0, 0, 150))
    text_draw.text((bot_tx, bot_ty), bot_text, font=font_bot, fill=(254, 240, 138, 255)) # Warm Yellow

    # Combine all layers
    final_img = Image.alpha_composite(img.convert('RGBA'), ball_layer)
    final_img = Image.alpha_composite(final_img, text_layer).convert('RGB')

    # Save multi-size icons for iOS and Android
    out_dir = r'C:\Users\knigh\.gemini\antigravity\scratch\lotto-predictor'
    
    # 512x512 (PWA Splash & Manifest)
    icon_512 = final_img.resize((512, 512), Image.Resampling.LANCZOS)
    icon_512.save(os.path.join(out_dir, 'icon-512.png'), format='PNG', optimize=True)

    # 192x192 (PWA Android)
    icon_192 = final_img.resize((192, 192), Image.Resampling.LANCZOS)
    icon_192.save(os.path.join(out_dir, 'icon-192.png'), format='PNG', optimize=True)

    # 180x180 (iOS Apple Touch Icon - HIG Standard)
    icon_180 = final_img.resize((180, 180), Image.Resampling.LANCZOS)
    apple_path = os.path.join(out_dir, 'apple-touch-icon.png')
    icon_180.save(apple_path, format='PNG', optimize=True)

    # Copy to brain artifact directory as well
    artifact_dir = r'C:\Users\knigh\.gemini\antigravity\brain\4c7a2e94-b07d-41d6-b829-6737fffd4ae6'
    icon_180.save(os.path.join(artifact_dir, 'apple-touch-icon.png'), format='PNG', optimize=True)

    # Convert 180x180 to Base64 for inline fallback
    import io
    buf = io.BytesIO()
    icon_180.save(buf, format='PNG', optimize=True)
    b64_str = base64.b64encode(buf.getvalue()).decode('utf-8')

    print(f"Icons generated successfully!")
    print(f"Base64 length: {len(b64_str)}")
    with open(os.path.join(out_dir, 'icon_base64.txt'), 'w', encoding='utf-8') as f:
        f.write(b64_str)

if __name__ == '__main__':
    create_app_icon()
