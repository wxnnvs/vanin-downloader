import os
import uuid
from pathlib import Path
from fastapi import FastAPI, UploadFile, BackgroundTasks
from fastapi.params import File
from fastapi.responses import FileResponse
import ocrmypdf

app = FastAPI()
jobs = {}
UPLOAD_DIR = "uploads"  # Create this directory

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/ocr")
def perform_ocr(file: UploadFile = File(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    job_id = str(uuid.uuid4())
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        return {"error": "File must be a PDF"}
    
    filename = Path(file.filename).name
    input_pdf = os.path.join(UPLOAD_DIR, f"{job_id}_{filename}")
    output_pdf = os.path.join(UPLOAD_DIR, f"{job_id}_ocr_{filename}")
    
    try:
        # Save uploaded file
        with open(input_pdf, "wb") as f:
            f.write(file.file.read())
    except Exception as e:
        return {"error": f"Failed to save file: {str(e)}"}
    
    # Store job status
    jobs[job_id] = {"status": "processing", "output_file": output_pdf}
    
    # Start OCR in background
    background_tasks.add_task(ocr_the_pdf, input_pdf, output_pdf, job_id)
    
    return {"job_id": job_id, "status": "processing"}




@app.get("/status/{job_id}")
def get_status(job_id: str):
    if job_id not in jobs:
        return {"error": "Job not found"}
    return jobs[job_id]


@app.get("/download/{job_id}")
def download_file(job_id: str):
    if job_id not in jobs:
        return {"error": "Job not found"}
    
    job = jobs[job_id]
    if job["status"] != "completed":
        return {"error": f"Job status: {job['status']}"}
    
    file_path = job["output_file"]
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='application/pdf', filename=file_path)
    else:
        return {"error": "File not found"}


def ocr_the_pdf(input_pdf, output_pdf, job_id):
    try:
        ocrmypdf.ocr(
            input_pdf,
            output_pdf,
            deskew=True,
            optimize=0,
            clean=False,
            clean_final=False,
            force_ocr=True,
            language='nld'
        )
        jobs[job_id]["status"] = "completed"
        print(f"Job {job_id}: Done. Searchable PDF created: {output_pdf}")
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        print(f"Job {job_id}: Error - {e}")
    finally:
        # Always clean up input file
        if os.path.exists(input_pdf):
            os.remove(input_pdf)