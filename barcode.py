import cv2
from pyzbar import pyzbar
import requests
from bs4 import BeautifulSoup
import urllib.parse
import os

# Replace with your Telegram Bot API token and chat ID
TELEGRAM_API_TOKEN = 'Your_Bot-Token'
# you can get user id in https://t.me/getmyid_bot
CHAT_ID = 'Your_User_Id'
SEARCH_ENGINE_URL = 'https://www.google.com/search?hl=en&tbm=isch&q='

def send_message_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Error sending message to Telegram: {e}")

def send_photo_to_telegram(photo_path):
    url = f"https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/sendPhoto"
    with open(photo_path, 'rb') as photo:
        payload = {
            'chat_id': CHAT_ID,
        }
        files = {
            'photo': photo
        }
        try:
            requests.post(url, data=payload, files=files)
        except Exception as e:
            print(f"Error sending photo to Telegram: {e}")

def search_and_download_image(query):
    search_url = SEARCH_ENGINE_URL + urllib.parse.quote(query)
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    img_tags = soup.find_all('img')
    
    if img_tags:
        # Use the first image URL
        img_url = img_tags[1]['src']
        img_response = requests.get(img_url, stream=True)
        img_name = 'barcode_image.jpg'
        with open(img_name, 'wb') as img_file:
            img_file.write(img_response.content)
        return img_name
    return None

def read_barcodes(frame):
    barcodes = pyzbar.decode(frame)
    for barcode in barcodes:
        x, y, w, h = barcode.rect
        barcode_info = barcode.data.decode('utf-8')
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, barcode_info, (x + 6, y - 6), font, 2.0, (255, 255, 255), 1)
        
        print("Barcode:", barcode_info)
        
        # Send barcode information to Telegram
        send_message_to_telegram(f"Barcode: {barcode_info}")
        
        # Search for image related to barcode information
        img_path = search_and_download_image(barcode_info)
        if img_path:
            send_photo_to_telegram(img_path)
            os.remove(img_path)  # Clean up image file after sending

    return frame

def main():
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("Error: Could not open camera.")
        return

    while True:
        ret, frame = camera.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        frame = read_barcodes(frame)
        cv2.imshow('Barcode/QR code reader', frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    camera.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
    
    
    
    








