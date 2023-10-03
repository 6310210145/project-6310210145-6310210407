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
    return render_template('index.html', original_image='', removebg_image='', background_image='', output_image='', new_output_image='', new_output2_image='', new_removebg_image_base64='')

@app.route('/process', methods=['POST'])
def process_image():
    original_image_base64 = ''
    removebg_image_base64 = ''
    new_removebg_image_base64 = ''
    background_image_base64 = ''
    output_image_base64 = ''
    new_output_image_base64 = ''
    new_output2_image_base64 = ''

    # ตรวจสอบว่ามีไฟล์ภาพที่อัปโหลดหรือไม่
    if 'image' in request.files:
        image_file = request.files['image']

        # โหลดภาพต้นฉบับ
        input_image = Image.open(image_file)

        # ปรับขนาดรูปต้นฉบับให้มีขนาดใหญ่ขึ้น 2 เท่า
        new_size = (int(input_image.width * 2), int(input_image.height * 2))
        new_input_image = input_image.resize(new_size)

        # ลบพื้นหลังตั้งแต่เริ่มต้น
        mask = remove(input_image)
        new_mask = remove(new_input_image)

        # แปลงภาพเป็น base64
        original_image_base64 = image_to_base64(input_image)
        removebg_image_base64 = image_to_base64(mask)
        new_removebg_image_base64 = image_to_base64(new_mask)

        # ตรวจสอบว่ามีไฟล์พื้นหลังที่อัปโหลดหรือไม่
        if 'background' in request.files:
            background_file = request.files['background']
            background = Image.open(background_file)

            # ปรับขนาดรูปพื้นหลังให้ตรงกับขนาดของรูปภาพที่อัปโหลด
            #background_resize = background.resize(input_image.size)
            
            # สร้าง output image โดยวางภาพ mask บน background ตรงกลาง
            output = Image.new('RGBA', input_image.size)
            x_offset = (input_image.width - mask.width) // 2
            y_offset = (input_image.height - mask.height) // 2
            output.paste(background, (0, 0))
            output.paste(mask, (x_offset, y_offset), mask=mask)

            background_image_base64 = image_to_base64(background)
            output_image_base64 = image_to_base64(output)

            # สร้างภาพ new output
            new_size = (background.width * 2, background.height * 2)
            new_background = background.resize(new_size)
            new_output = Image.new('RGBA', new_size)
            x_offset = (new_size[0] - mask.width) // 2
            y_offset = (new_size[1] - mask.height) // 2
            new_output.paste(new_background, (0, 0))
            new_output.paste(mask, (x_offset, y_offset), mask=mask)
            new_output_image_base64 = image_to_base64(new_output)

            # สร้างภาพ new output2
            new_output2 = Image.new('RGBA', input_image.size)
            x_offset = (input_image.width - new_mask.width) // 2
            y_offset = (input_image.height - new_mask.height) // 2
            new_output2.paste(background, (0, 0))
            new_output2.paste(new_mask, (x_offset, y_offset), mask=new_mask)
            new_output2_image_base64 = image_to_base64(new_output2)

    # ส่งข้อมูลไปยังหน้าเว็บสำหรับแสดงผล
    return render_template('process.html', original_image=original_image_base64, removebg_image=removebg_image_base64, background_image=background_image_base64, output_image=output_image_base64, new_output_image=new_output_image_base64, new_output2_image=new_output2_image_base64, new_removebg_image=new_removebg_image_base64)
    

if __name__ == '__main__':
    app.run(debug=True)
