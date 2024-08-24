import time
import random
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
driver.get("https://x.com/")


def go_to_following_page():
    if is_the_true_page():
        return True

    driver.get("https://x.com/")
    time.sleep(10)
    profile = driver.find_element(
        By.CSS_SELECTOR, "a[aria-label='Profile'][data-testid='AppTabBar_Profile_Link']")
    profile.click()
    time.sleep(5)
    followings = driver.find_element(
        By.CSS_SELECTOR, "div.css-175oi2r.r-1rtiivn > a[href='/Mehr_mihan/following']")
    followings.click()
    time.sleep(5)


def go_down(n):
    try:
        # Create ActionChains object
        actions = ActionChains(driver)

        # Scroll down by simulating "Page Down" key press
        for _ in range(n):  # Adjust the range for the number of scrolls needed
            driver.execute_script("window.scrollBy(0, window.innerHeight);")
            # Adjust the pause as needed to allow content to load
            time.sleep(4)

        return True
    except Exception as e:
        print(e)
        return False


def following_list():
    try:
        return driver.find_elements(By.CSS_SELECTOR, "div[data-testid='cellInnerDiv']")
    except:
        return False


def insert_user_name_to_table(text):
    conn = sqlite3.connect('following.db')
    cursor = conn.cursor()

    # Check if the text already exists in the table
    cursor.execute('''
    SELECT COUNT(*)
    FROM following_table
    WHERE user_name = ?
    ''', (text,))

    # Fetch the result
    count = cursor.fetchone()[0]

    # If count is 0, the text does not exist, so insert it
    if count == 0:
        cursor.execute('''
        INSERT INTO following_table (user_name)
        VALUES (?)
        ''', (text,))
        conn.commit()
        conn.close()


def delete_user_name_from_table(text):
    # Connect to SQLite database
    conn = sqlite3.connect('following.db')

    # Create a cursor object using the cursor() method
    cursor = conn.cursor()

    # SQL command to delete the text from the table
    cursor.execute('''
    DELETE FROM following_table
    WHERE user_name = ?
    ''', (text,))

    # Check if any row was deleted
    if cursor.rowcount == 0:
        print(f"Text '{text}' does not exist in the table.")
    else:
        print(f"Text '{text}' deleted successfully.")

    # Commit the changes
    conn.commit()

    # Close the connection
    conn.close()


def count_table_records():
    # Connect to SQLite database
    conn = sqlite3.connect('following.db')

    # Create a cursor object using the cursor() method
    cursor = conn.cursor()

    # SQL command to delete the text from the table
    cursor.execute('SELECT COUNT(*) FROM following_table')

    # Fetch the result
    count = cursor.fetchone()[0]

    # Close the connection
    conn.close()

    # Return the count
    return count


def no_follow_back_list(list_of_followings):
    if not (is_the_true_page()):
        return False

    try:
        # List to hold items that didn't give a follow back
        no_follow_back_list = []

        # Iterate through each list item
        for following in list_of_followings:
            try:
                # Try to find the "Follows you" indicator within the following
                following.find_element(
                    By.CSS_SELECTOR, "div[data-testid='userFollowIndicator']")
                user_name = following.find_element(
                    By.CSS_SELECTOR, "a.css-175oi2r.r-1wbh5a2.r-dnmrzs.r-1ny4l3l.r-1loqt21").get_attribute("href")
                insert_user_name_to_table(user_name)
            except:
                # If the indicator is not found, add the following to the list
                no_follow_back_list.append(following)
        return no_follow_back_list

    except:
        return False


def unfollow_the_list(list_of_followings):
    try:
        list_for_unfollowing = no_follow_back_list(list_of_followings)
        if list_for_unfollowing:
            for item in list_for_unfollowing:
                try:
                    unfollow_button = item.find_element(
                        By.CSS_SELECTOR, "div.css-175oi2r.r-1cwvpvk > button[aria-label^='Following @'][role='button']")
                    driver.execute_script(
                        "arguments[0].scrollIntoView(true);", unfollow_button)
                    # Optional: Add a small delay to ensure the element is in view
                    time.sleep(2)
                    # Click the button using JavaScript
                    driver.execute_script(
                        "arguments[0].click();", unfollow_button)
                    time.sleep(2)
                    confirm_unfollow = driver.find_element(
                        By.CSS_SELECTOR, "button.css-175oi2r[data-testid='confirmationSheetConfirm'][role='button']")
                    confirm_unfollow.click()
                    time.sleep(random.randint(2, 10))
                except:
                    continue
        return True
    except:
        return False


def is_the_true_page():
    try:
        driver.find_element(
            By.CSS_SELECTOR, "div.css-175oi2r.r-14tvyh0.r-cpa5s6.r-16y2uox > a[href='/Mehr_mihan/verified_followers'][role='tab']")
        driver.find_element(
            By.CSS_SELECTOR, "div.css-175oi2r.r-14tvyh0.r-cpa5s6.r-16y2uox > a[href='/Mehr_mihan/followers'][role='tab']")
        driver.find_element(
            By.CSS_SELECTOR, "div.css-175oi2r.r-14tvyh0.r-cpa5s6.r-16y2uox > a[href='/Mehr_mihan/following'][role='tab'][aria-selected='true']")
        return True
    except:
        return False


def check_local_limitation_rate():
    try:
        element = driver.find_element(
            By.XPATH, "//*[text()='local_rate_limited']")
        return True
    except:
        pass

    try:
        button = driver.find_element(
            By.XPATH, "//button[.//span[text()='Retry']]")
        return True
    except:
        pass

    try:
        span_element = driver.find_element(
            By.XPATH, "//span[text()='Something went wrong. Try reloading.']")
        return True
    except:
        pass

    return False


def main():
    try:
        if not is_the_true_page():
            go_to_following_page()

        go_down(1)
        list_of_followings = following_list()
        if unfollow_the_list(list_of_followings):
            return True
        else:
            return False

    except:
        return False


if __name__ == '__main__':
    time.sleep(120)
    go_to_following_page()

    while True:
        if check_local_limitation_rate():
            time.sleep(30 * 60)
            driver.refresh()
            continue

        if main():
            time.sleep(60)
        else:
            time.sleep(60)
            driver.refresh()
            go_to_following_page()
