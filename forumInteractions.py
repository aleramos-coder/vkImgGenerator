from selenium.webdriver.common.by import By


def fetchNotifications(driver):
    notifications = driver.find_elements(By.CSS_SELECTOR, '.feedback_row_wrap')
    return  notifications

def filterByRepliedNotifications(notifications):
    filteredList = []
    for notif in notifications:
        header = notif.find_element(By.CSS_SELECTOR, '.feedback_header')
        if "replied" in header.text:
            filteredList.append(notif)
    return filteredList