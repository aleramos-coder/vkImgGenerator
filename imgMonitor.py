import os
import time
from queue import Queue
from threading import Thread

from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from cartolaImgBot.forumInteractions import getNotificationCardById, getNotificationTextDiv
from v2CartolaImgBot.utils import initiateDriver, login


# Function to handle new files
def handle_new_file(file_path):
    driver.get("https://vk.com/feed?section=notifications")
    print(f"New file created: {file_path}")
    fileName, extension = os.path.splitext(os.path.basename(file_path))
    print(fileName)
    try:
        notification = getNotificationCardById(driver, fileName)
        notificationTextDiv = getNotificationTextDiv(notification)
        notificationTextDiv.click()

        replyBox = notification.find_element(By.CSS_SELECTOR, f'#{fileName.replace("feedback_row", "reply_field")}')
        actions = ActionChains(driver)
        photoIcon = notification.find_element(By.CSS_SELECTOR, '.MediaSelector__mediaIcon')
        photoIcon.click()
        time.sleep(2)

        photoInput = driver.find_element(By.ID, 'photos_upload_input_271229943_-14')
        photoInput.send_keys(os.path.abspath(file_path))
        replyBox.click()
        replyBox.send_keys("Aqui sua imagem")
        time.sleep(2)
        submit = notification.find_element(By.CSS_SELECTOR, '.FlatButton__in')
        submit.click()
        time.sleep(2)
        actions.key_down(Keys.CONTROL).send_keys(Keys.ENTER).key_up(Keys.CONTROL).perform()
        time.sleep(3)

        os.remove(file_path)
    except Exception as e:
        print(e)
        driver.get("https://vk.com/feed?section=notifications")
        time.sleep(2)
# Custom event handler
class MyHandler(FileSystemEventHandler):
    def __init__(self, queue):
        self.queue = queue

    def on_created(self, event):
        # Only handle file creations, ignore directories
        if not event.is_directory:
            self.queue.put(event.src_path)  # Add the file path to the queue


# Worker function to process files from the queue
def worker(queue):
    while True:
        file_path = queue.get()  # Get a file path from the queue
        if file_path is None:  # Stop signal
            break
        handle_new_file(file_path)
        queue.task_done()  # Mark the task as done


def main(directory_to_watch):
    # Create a queue to hold file paths
    queue = Queue()

    # Start a worker thread to process items from the queue
    thread = Thread(target=worker, args=(queue,))
    thread.start()

    # Set up watchdog observer
    event_handler = MyHandler(queue)
    observer = Observer()
    observer.schedule(event_handler, directory_to_watch, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)  # Keep the main thread alive
    except KeyboardInterrupt:
        observer.stop()  # Stop the observer on interrupt
    observer.join()  # Wait for the observer to finish

    # Stop the worker thread
    queue.put(None)  # Send stop signal
    thread.join()  # Wait for the thread to finish


if __name__ == "__main__":
    driver = initiateDriver()
    login(driver)
    directory_to_watch = "./images"  # Change this to your directory
    main(directory_to_watch)
