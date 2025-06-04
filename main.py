import os
import aiohttp
import shutil
from fastapi import FastAPI
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client
from tempfile import TemporaryDirectory

load_dotenv()

app = FastAPI()

# Load environment variables and configure Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.post("/generate-invoice-zip/")
async def generate_invoice_zip(data: dict):
    date_str = str(datetime.now())
    zip_name = f"receipt_attachment_{date_str}"
    
    with TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir) / zip_name
        base_path.mkdir(parents=True, exist_ok=True)

        # Download each file and organize them into category subfolders
        async with aiohttp.ClientSession() as session:
            for category, vendors in data.items():
                category_dir = base_path / category
                category_dir.mkdir(parents=True, exist_ok=True)

                for vendor, url in vendors.items():
                    filename = vendor.replace(" ", "_").replace("/", "_") + Path(url).suffix
                    file_path = category_dir / filename

                    async with session.get(url) as resp:
                        if resp.status == 200:
                            content = await resp.read()
                            with open(file_path, "wb") as f:
                                f.write(content)

        # Create a zip archive
        zip_path = Path(tmpdir) / f"{zip_name}.zip"
        shutil.make_archive(str(zip_path).replace(".zip", ""), 'zip', base_path)

        # Upload the zip file to Supabase
        with open(zip_path, "rb") as f:
            upload_path = f"{zip_name}.zip"
            supabase.storage.from_(SUPABASE_BUCKET).upload(upload_path, f, {"content-type": "application/zip"})

    # Return the download link
    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{upload_path}"
    return {
        "message": "✅ Pack and upload successful",
        "download_url": public_url
    }







