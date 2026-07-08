import httpx
import asyncio
from PIL import Image
import sqlite3
from datetime import datetime
import uuid
import os
from dotenv import load_dotenv
from io import BytesIO

load_dotenv()


url = 'https://api.unsplash.com/photos/random'
api_key = os.getenv("UNSPLASH_ACCESS_KEY")
headers = {"Authorization": "Client-ID {}".format(api_key)}
    

def save_img(image_response, img_url):

    img = Image.open(BytesIO(image_response.content))
    width, height = img.size
    imgformat = img.format
    single_pixel = img.resize((1, 1), resample=Image.Resampling.BOX)
    average_color = single_pixel.getpixel((0, 0))
    r, g, b = average_color[:3]
    hex_colour = f"#{r:02x}{g:02x}{b:02x}"
    fetched_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    os.makedirs("images", exist_ok=True)
    filename = os.path.join("images", f"{uuid.uuid4()}.jpeg")
    with open(filename, "wb") as f:
        f.write(image_response.content)

    with sqlite3.connect('sql.db') as con:
        cur = con.cursor()
        cur.execute("""INSERT INTO images(file_name, image_url, width, height, format, avg_colour, fetched_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (filename, img_url, width, height, imgformat, hex_colour, fetched_at))
        con.commit()

async def fetch(client):
    try:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()
        image_url = data["urls"]["regular"]
        image_response = await client.get(image_url)
        image_response.raise_for_status()
        save_img(image_response,image_url)
    except httpx.HTTPStatusError as e:
        print(f"HTTP error fetching image: {e}")
    except httpx.RequestError as e:
        print(f"Network error fetching image: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

        

async def fetch_images():
    async with httpx.AsyncClient(headers=headers) as client:
        tasks = [fetch(client) for _ in range(5)]
        await asyncio.gather(*tasks)

            # print("Status:", r.status_code)
            # print("Content-Type:", r.headers.get("content-type")

def query_images(format: str = None):
    with sqlite3.connect('sql.db') as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        if format:
            cur.execute("SELECT * FROM images WHERE format = ?", (format,))
        else:
            cur.execute("SELECT * FROM images")
        return [dict(row) for row in cur.fetchall()]
    
# asyncio.run(main())
# con = sqlite3.connect('sql.db')
# cur = con.cursor()
# cur.execute("Select * from images")
# print(cur.fetchall())