import pickle
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def initiateDriver():
    chrome_driver_path = r"C:\development\chromedriver.exe"
    options = Options()
    # options.add_argument(r'--user-data-dir=C:\Users\fcn_a\AppData\Local\Google\Chrome\User Data')
    options.add_argument("--headless")  # Ensure GUI is off
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    return driver

def login(driver):
    try:
        driver.get("https://www.vk.com")
        email = driver.find_element(By.ID, "index_email")
        signInButton = driver.find_element(By.CLASS_NAME, "VkIdForm__signInButton")

        # Perform login
        email.send_keys("fpr_alexandre@hotmail.com")
        signInButton.click()

        time.sleep(3)
        confirmButton = driver.find_element(By.CLASS_NAME, "vkc__ConfirmOTP__button")
        confirmButton.click()

        time.sleep(3)
        buttonPass = driver.find_element(By.CSS_SELECTOR, '[data-test-id="verificationMethod_password"]')
        buttonPass.click()

        time.sleep(3)
        password = driver.find_element(By.CSS_SELECTOR,
                                       ".vkc__Password__Wrapper > div:nth-child(1) > div:nth-child(1) > input:nth-child(1)")
        password.send_keys("Deadpoolboladao")

        time.sleep(3)
        confirmButton = driver.find_element(By.CSS_SELECTOR, "button.vkuiTappable:nth-child(1)")
        confirmButton.click()

        # save cookies
        time.sleep(5)
        pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))
        print("cookie saved")

    except Exception as e:
        # If login elements are not found, continue without login
        print(e)