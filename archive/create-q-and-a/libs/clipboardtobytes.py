import io
from PIL import ImageGrab



def getBytesFromClipboard():
    img = ImageGrab.grabclipboard()
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

def main():
    print('This is a Library. Call the functions from here in other clients')

if __name__ == '__main__':
    main()
