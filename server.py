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
            frame_idx = data['index']
            img_data_url = data['image']
            
            # Decode base64 data
            header, encoded = img_data_url.split(",", 1)
            img_bytes = base64.b64decode(encoded)
            
            # Save directly to assets/{char}_highres/raw_attack/frame_X.png
            target_path = f"/Users/jasminpingol/Codex/assets/{char}_highres/raw_attack/frame_{frame_idx}.png"
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, "wb") as f:
                f.write(img_bytes)
                
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
            print(f"Applying saved frames to game assets for {char}...")
            
            ASSETS_DIR = "/Users/jasminpingol/Codex/assets"
            raw_attack_dir = os.path.join(ASSETS_DIR, f"{char}_highres", "raw_attack")
            
            # Determine total frame count and raw files available
            # Bubu: 36 raw frames. Dudu: 24 raw frames.
            total_raw = 36 if char == "bubu" else 24
            
            all_clean_canvases = []
            for f_i in range(total_raw):
                frame_path = os.path.join(raw_attack_dir, f"frame_{f_i}.png")
                if os.path.exists(frame_path):
                    canvas = Image.open(frame_path)
                else:
                    canvas = Image.new("RGBA", (250, 300), (0, 0, 0, 0))
                all_clean_canvases.append(canvas)
                
            # Key indices choice
            if char == "bubu":
                # Frames 16-25 as requested
                key_indices = list(range(16, 26))
            else:
                # Dudu: default to [0, 1, 2, 3, 4, 5] (first 6 frames)
                key_indices = [0, 1, 2, 3, 4, 5]
                
            extracted_key_frames = [all_clean_canvases[i] for i in key_indices]
            directions = ["right", "left", "front", "back"]
            
            # Save to highres
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
                box_sz = (250, 300) if "outlined" in folder else (41, 50)
                resamp = Image.Resampling.NEAREST if "pixel" in folder else Image.Resampling.LANCZOS
                for dir_name in directions:
                    for idx, frame in enumerate(extracted_key_frames):
                        img_to_save = ImageOps.mirror(frame) if dir_name == "left" else frame
                        resized = img_to_save.resize(box_sz, resamp)
                        path = os.path.join(target_dir, f"attack_{dir_name}_frame_{idx}.png")
                        resized.save(path)
                        
            print(f"Successfully updated game assets for {char} with edited frames!")
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))
            
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
