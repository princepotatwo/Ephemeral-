#!/usr/bin/env python3
import os
import json
import base64
import glob
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from PIL import Image, ImageOps

class CustomHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/save_frame':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            char = data.get('char', 'bubu')
            mode = data.get('mode', 'idle')
            dir_name = data.get('dir', 'front')
            frame_idx = data['index']
            img_data_url = data['image']
            
            # Decode base64 data
            header, encoded = img_data_url.split(",", 1)
            img_bytes = base64.b64decode(encoded)
            
            ASSETS_DIR = "/Users/jasminpingol/Codex/assets"
            META_PATH = os.path.join(ASSETS_DIR, "spritesheets_metadata.json")
            
            # 1. Save to high-res source frame
            if mode == "attack":
                # Raw attack frames are stored in raw_attack folder
                target_path = os.path.join(ASSETS_DIR, f"{char}_highres", "raw_attack", f"frame_{frame_idx}.png")
            else:
                target_path = os.path.join(ASSETS_DIR, f"{char}_highres", f"{mode}_{dir_name}_frame_{frame_idx}.png")
                
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, "wb") as f:
                f.write(img_bytes)
                
            # 2. If it is an attack frame, we need to run apply_changes-like logic
            # to mirror it to left/right and update all folders
            if mode == "attack":
                self.apply_attack_frame_changes(char, frame_idx, target_path)
            else:
                # For normal frames, resize and save to the specific folder paths
                self.apply_normal_frame_changes(char, mode, dir_name, frame_idx, target_path)
                
            # 3. Rebuild spritesheets in real time!
            self.rebuild_spritesheets(char)
                
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "path": target_path}).encode('utf-8'))
            
        elif self.path == '/apply_changes':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            char = data.get('char', 'bubu')
            
            # Rebuild spritesheets
            self.rebuild_spritesheets(char)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))

    def apply_attack_frame_changes(self, char, frame_idx, source_path):
        ASSETS_DIR = "/Users/jasminpingol/Codex/assets"
        raw_attack_dir = os.path.join(ASSETS_DIR, f"{char}_highres", "raw_attack")
        
        # Bubu has 36 frames, Dudu has 24
        total_raw = 36 if char == "bubu" else 24
        all_clean_canvases = []
        for f_i in range(total_raw):
            frame_path = os.path.join(raw_attack_dir, f"frame_{f_i}.png")
            if os.path.exists(frame_path):
                canvas = Image.open(frame_path)
            else:
                canvas = Image.new("RGBA", (250, 300), (0, 0, 0, 0))
            all_clean_canvases.append(canvas)
            
        key_indices = list(range(16, 26)) if char == "bubu" else [0, 1, 2, 3, 4, 5]
        extracted_key_frames = [all_clean_canvases[i] for i in key_indices]
        directions = ["right", "left", "front", "back"]
        
        # Save to high-res
        highres_dir = os.path.join(ASSETS_DIR, f"{char}_highres")
        for dir_name in directions:
            for idx, frame in enumerate(extracted_key_frames):
                img_to_save = ImageOps.mirror(frame) if dir_name == "left" else frame
                path = os.path.join(highres_dir, f"attack_{dir_name}_frame_{idx}.png")
                img_to_save.save(path)
                
        # Downscale to normal, outlined, pixelated
        for folder in [char, f"{char}_outlined", f"{char}_pixel"]:
            target_dir = os.path.join(ASSETS_DIR, folder)
            os.makedirs(target_dir, exist_ok=True)
            
            is_outlined = "outlined" in folder
            box_w = 250 if is_outlined else (46 if "dudu" in char else 41)
            box_h = 300 if is_outlined else 50
            box_sz = (box_w, box_h)
            
            resamp = Image.Resampling.NEAREST if "pixel" in folder else Image.Resampling.LANCZOS
            for dir_name in directions:
                for idx, frame in enumerate(extracted_key_frames):
                    img_to_save = ImageOps.mirror(frame) if dir_name == "left" else frame
                    resized = img_to_save.resize(box_sz, resamp)
                    path = os.path.join(target_dir, f"attack_{dir_name}_frame_{idx}.png")
                    resized.save(path)

    def apply_normal_frame_changes(self, char, mode, dir_name, frame_idx, source_path):
        ASSETS_DIR = "/Users/jasminpingol/Codex/assets"
        img = Image.open(source_path)
        
        folders = [char, f"{char}_outlined", f"{char}_pixel"]
        for folder in folders:
            target_dir = os.path.join(ASSETS_DIR, folder)
            os.makedirs(target_dir, exist_ok=True)
            
            is_outlined = "outlined" in folder
            box_w = 250 if is_outlined else (46 if "dudu" in char else 41)
            box_h = 300 if is_outlined else 50
            box_sz = (box_w, box_h)
            
            resamp = Image.Resampling.NEAREST if "pixel" in folder else Image.Resampling.LANCZOS
            resized = img.resize(box_sz, resamp)
            path = os.path.join(target_dir, f"{mode}_{dir_name}_frame_{frame_idx}.png")
            resized.save(path)

    def rebuild_spritesheets(self, char):
        ASSETS_DIR = "/Users/jasminpingol/Codex/assets"
        META_PATH = os.path.join(ASSETS_DIR, "spritesheets_metadata.json")
        
        with open(META_PATH, "r") as f:
            meta = json.load(f)
            
        variants = [char, f"{char}_pixel", f"{char}_highres", f"{char}_outlined"]
        for v in variants:
            if v not in meta:
                continue
            char_dir = os.path.join(ASSETS_DIR, v)
            if not os.path.isdir(char_dir):
                continue
                
            target_w = meta[v]["frameWidth"]
            target_h = meta[v]["frameHeight"]
            anims = meta[v]["animations"]
            if not anims:
                continue
                
            max_count = max(a["count"] for a in anims.values())
            num_rows = max(a["row"] for a in anims.values()) + 1
            
            sheet_w = max_count * target_w
            sheet_h = num_rows * target_h
            
            spritesheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))
            
            for anim_name, a_info in anims.items():
                row_idx = a_info["row"]
                parts = anim_name.split("-")
                if len(parts) == 2:
                    mode, direction = parts
                    for col_idx in range(a_info["count"]):
                        frame_path = os.path.join(char_dir, f"{mode}_{direction}_frame_{col_idx}.png")
                        if os.path.exists(frame_path):
                            try:
                                with Image.open(frame_path) as frame_img:
                                    dx = col_idx * target_w
                                    dy = row_idx * target_h
                                    
                                    canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
                                    px = max(0, (target_w - frame_img.width) // 2)
                                    py = max(0, target_h - frame_img.height)
                                    canvas.paste(frame_img, (px, py))
                                    spritesheet.paste(canvas, (dx, dy))
                            except Exception:
                                pass
                                
            sheet_path = os.path.join(char_dir, "spritesheet.png")
            spritesheet.save(sheet_path, "PNG")
            print(f"✓ Rebuilt spritesheet for {v} at {target_w}x{target_h}")
            
        else:
            super().do_POST()

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        if self.command == 'GET' and '/assets/' in self.path:
            self.send_header('Cache-Control', 'public, max-age=31536000, immutable')
        super().end_headers()

if __name__ == '__main__':
    server_address = ('', 8080)
    httpd = ThreadingHTTPServer(server_address, CustomHandler)
    print("Custom HTTP Server running on port 8080...")
    httpd.serve_forever()
