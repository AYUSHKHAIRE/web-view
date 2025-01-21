import base64
from PIL import Image
from io import BytesIO
from memory_manager import memoryManager

MM = memoryManager()

# Assuming you are reading from shared memory with correct user_id
user_id = 1111
data = MM.read_memory(user_id)

if data:
    image_data = base64.b64decode(data)
    image = Image.open(BytesIO(image_data))
    image.save("img.png")
    image.show()
else:
    print(f"No data found for user_id {user_id}")
