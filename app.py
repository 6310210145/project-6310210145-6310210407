from flask import Flask, render_template, request
from rembg import remove
from PIL import Image
import io
import base64

app = Flask(__name__)

# ฟังก์ชันสำหรับแปลงภาพเป็นรูปแบบ base64
def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_base64

@app.route('/')
def index():
    return render_template('index.html', original_image='', removebg_image='', background_image='', output_image='')

@app.route('/process', methods=['POST'])
def process_image():
    original_image_base64 = ''
    removebg_image_base64 = ''
    background_image_base64 = ''
    output_image_base64 = ''

    # ตรวจสอบว่ามีไฟล์ภาพที่อัปโหลดหรือไม่
    if 'image' in request.files:
        image_file = request.files['image']

        # โหลดภาพต้นฉบับ
        input_image = Image.open(image_file)
        
        # ลบพื้นหลัง
        mask = remove(input_image)
        new_size = (input_image.width * 2, input_image.height * 2)
        mask_new = input_image.resize(new_size)
        # แปลงภาพเป็น base64
        original_image_base64 = image_to_base64(input_image)
        removebg_image_base64 = image_to_base64(mask)

        # ตรวจสอบว่ามีไฟล์พื้นหลังที่อัปโหลดหรือไม่
        if 'background' in request.files:
            background_file = request.files['background']
            background = Image.open(background_file)
            background = background.resize(input_image.size)
            output = Image.composite(input_image, background, mask_new)
            background_image_base64 = image_to_base64(background)
            output_image_base64 = image_to_base64(output)

    # ส่งข้อมูลไปยังหน้าเว็บสำหรับแสดงผล
    return render_template('index.html', original_image=original_image_base64, removebg_image=removebg_image_base64, background_image=background_image_base64, output_image=output_image_base64)

if __name__ == '__main__':
    app.run(debug=True)
