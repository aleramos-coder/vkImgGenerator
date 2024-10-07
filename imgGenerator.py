import concurrent
import os.path
import time
from threading import Thread, Event
import requests
from lxml.html.diff import href_token
from selenium.webdriver.common.by import By
import pandas as pd
from forumInteractions import fetchNotifications, filterByRepliedNotifications
from utils import initiateDriver, login
from dotenv import load_dotenv

load_dotenv()

HF_AUTH_TOKEN = os.getenv("API_KEY")
API_URLS = [
    "https://api-inference.huggingface.co/models/XLabs-AI/flux-RealismLora",
    "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev",
    "https://api-inference.huggingface.co/models/Shakker-Labs/FLUX.1-dev-LoRA-AntiBlur",
    "https://api-inference.huggingface.co/models/ostris/OpenFLUX.1",

]
headers = {"Authorization": f"Bearer {HF_AUTH_TOKEN}"}


def load_fetched_ids(filename='./ids.xlsx'):
    try:
        df = pd.read_excel(filename)
        return set(df['ids'].tolist())
    except FileNotFoundError:
        return set()


def save_fetched_id(img_id, filename='./ids.xlsx'):
    try:
        df = pd.read_excel(filename)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['ids'])

    new_entry = pd.DataFrame({'ids': [img_id]})
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_excel(filename, index=False)



def fetch_image(url, payload):
    try:
        print(f"trying url: {url}")
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an error for bad responses (e.g., 403, 500)
        return response.content  # Return image content (binary data)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from {url}: {e}")

def get_image_response(payload):
    img_id = payload.get("img_id")  # Assume your payload contains an 'id' field
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(fetch_image, url, payload): url for url in API_URLS}

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result is not None:
                print(f"Successfully fetched image from: {futures[future]}")
                saveImg(result, img_id)  # Save the image with the payload ID
                return result  # Return the first successful response

    print("All requests failed for this payload.")
    return None  # Return None if all requests failed


def saveImg(imgBytes, img_id):
    # Create the directory if it doesn't exist
    os.makedirs('./images', exist_ok=True)

    print(f"Saving img with ID: {img_id}...")
    filename = f"./images/{img_id}.png"  # Change the extension if needed
    with open(filename, 'wb') as f:
        f.write(imgBytes)
    print(f"Image saved as {filename}")

def fetch_new_payloads():
        driver.get("https://vk.com/feed?section=notifications")
        time.sleep(1)
        notifications = fetchNotifications(driver)
        payloads = []
        repliedNotifications = filterByRepliedNotifications(notifications)
        payloads = []
        for notification in repliedNotifications:
            replyTxt = notification.find_element(By.CSS_SELECTOR, ".feedback_text").text
            img_id = notification.get_attribute("id")
            if "-d" in replyTxt:
                payloads.append({"img_id": img_id, "inputs": replyTxt.replace('-d', '')})
        print(payloads)
        return payloads




def process_payloads(stop_event):
        while not stop_event.is_set():
            fetched_ids = load_fetched_ids()
            new_payloads = fetch_new_payloads()  # Fetch new payloads from the source
            for payload in new_payloads:
                img_id = payload.get("img_id")
                if img_id not in fetched_ids:
                    print(f"Starting processing for payload ID: {img_id}")
                    save_fetched_id(img_id, './ids.xlsx')
                    Thread(target=get_image_response, args=(payload,)).start()
                else:
                    print(f"Payload ID: {img_id} has already been fetched.")

            time.sleep(5)  # Adjust the sleep time as needed



if __name__ == "__main__":
    stop_event = Event()
    driver = initiateDriver()
    login(driver)
    driver.get("https://vk.com/feed?section=notifications")


    thread = Thread(target=process_payloads, args=(stop_event,), daemon=True)
    thread.start()


    while True:
        time.sleep(1)  # Main thread can perform other tasks here
