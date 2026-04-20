from fastapi import FastAPI, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
import subprocess
import sys
import cv2
import numpy as np
import uvicorn

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


def read_static_html(filename: str) -> str:
    return (STATIC_DIR / filename).read_text(encoding="utf-8")

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
async def main():
    return HTMLResponse(content=read_static_html("index.html"), status_code=200)

@app.post("/submit")
async def get_info(image: UploadFile = File(...), message: str = Form(...)):
    try:
        msg_str = message
        contents = await image.read()

        image_array = np.frombuffer(contents, dtype=np.uint8)
        decoded_image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        if decoded_image is None:
            raise ValueError("Uploaded file is not a valid image.")

        img_path = STATIC_DIR / "uploaded_input.png"
        cv2.imwrite(str(img_path), decoded_image)

        subprocess.check_call([
            sys.executable,
            str(BASE_DIR / 'generate.py'),
            '--image',
            str(img_path),
            '--message',
            msg_str,
        ], bufsize=0)
       
        
        return HTMLResponse(content=read_static_html("output.html"), status_code=200)
        
         
        
    except Exception as e:
        return HTMLResponse(content=read_static_html("error.html"), status_code=500)
    
@app.get("/download")
async def download_output(filename: str):
    file_path = BASE_DIR / filename
    if file_path.exists():
        return FileResponse(file_path, headers={"Content-Disposition": f"attachment; filename={file_path.name}"})
    else:
        return HTMLResponse(content=read_static_html("error.html"), status_code=404)
    
if __name__ == "__main__":
    
    uvicorn.run(app, host="0.0.0.0", port=8000)


