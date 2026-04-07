import os
from PIL import Image, ImageStat, ImageFilter

_latest_context = {
    "is_room": True,
    "lighting": "dim",
    "style": "Modern",
    "furnished_status": "furnished",
    "edge_mean": 0.0
}

def analyze_room_image(image_path):
    global _latest_context
    try:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found at {image_path}")
            
        img = Image.open(image_path).convert('RGB')
        stat = ImageStat.Stat(img)
        
        # Calculate variance to check if it's completely dark or empty
        variance = sum(stat.var) / 3
        if variance < 5.0:
            _latest_context["is_room"] = False
            return {"is_room": False, "error": "Image is too dark or empty to be a room."}
            
        # Determine lighting from average RGB
        r_avg, g_avg, b_avg = stat.mean
        avg_brightness = (r_avg + g_avg + b_avg) / 3
        
        if avg_brightness < 85:
            lighting = "dim"
        elif avg_brightness > 200:
            lighting = "bright"
        elif r_avg > b_avg + 20 and r_avg > g_avg + 10:
            lighting = "warm"
        elif b_avg > r_avg + 20 and b_avg > g_avg + 10:
            lighting = "cool"
        else:
            lighting = "bright"  # fallback
            
        # Apply find edges for structure complexity
        edges = img.convert('L').filter(ImageFilter.FIND_EDGES)
        edge_stat = ImageStat.Stat(edges)
        edge_mean = edge_stat.mean[0]
        
        if edge_mean < 15:
            furnished_status = "empty"
            style = "Minimalist"
        elif edge_mean > 25:
            furnished_status = "furnished"
            style = "Eclectic"
        else:
            furnished_status = "furnished"
            style = "Modern"
            
        _latest_context = {
            "is_room": True,
            "lighting": lighting,
            "style": style,
            "furnished_status": furnished_status,
            "edge_mean": edge_mean
        }
        
        return {"is_room": True}
        
    except Exception as e:
        # Fallback in case of errors
        _latest_context = {
            "is_room": True,
            "lighting": "dim",
            "style": "Modern",
            "furnished_status": "furnished",
            "edge_mean": 0.0
        }
        return {"is_room": True}

def get_latest_context():
    return _latest_context
