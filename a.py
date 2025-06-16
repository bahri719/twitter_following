import time
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
driver.get("https://x.com/")

#  پیدا کردن و کلیک کردن تب تویفیکیشن
def press_notification_tab():
    notification_tab = driver.find_element(
        By.CSS_SELECTOR, "a[href='/notifications']")
    click(notification_tab)


def was_the_notifications_loaded(wait_time=20):
    try:
        # منتظر ماندن تا یک عنصر خاص به طور کامل بارگذاری شود
        element = WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.css-175oi2r[data-testid='cellInnerDiv']"))
        )
        return True
    except:
        print("Loading took too much time!")
        return False


def was_the_my_post_loaded(wait_time=20):
    try:
        # Construct the CSS selector string based on the classes and style
        css_selector = "div.css-146c3p1.r-bcqeeo.r-1ttztb7.r-qvutc0.r-37j5jr.r-a023e6.r-rjixqe.r-16dba41[style='text-overflow: unset; color: rgb(113, 118, 123);']"

        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
        )
        return True
    except:
        print("Loading took too much time!")
        return False


# وقتی در پروفایل کاربر هستیم چک می کند که این کاربر مییوت هست یا خیر
#  اگر مییوت باشد درست وگرنه غلط را بر میگرداند
def is_muted():
    try:
        unmute_button = driver.find_element(
            By.XPATH, "//button[.//span[text()='Unmute']]")
        return True
    except:
        return False


#  بررسی می کنیم اگر قبلا این کاربر را مییوت نکرده ایم او را فالوو می کنیم
def if_user_is_unmute_press_follow_button():
    sw = False
    if not (is_muted()):
        follow_button = driver.find_element(
            By.XPATH, "//button[.//span[text()='Follow']]")
        click(follow_button)
        sw = True
    back_button = driver.find_element(
        By.CSS_SELECTOR, "button[aria-label='Back']")
    click(back_button)
    return sw  # نشان میدهد کی فالوو انجام شد یا نشد


#  بررسی می کنیم اگر قبلا این کاربر را مییوت نکرده ایم او را فالوو می کنیم
def check_and_follow_if_everything_is_ok():
    driver.execute_script("window.scrollTo(0, 0);")
    unfollower_interactions = driver.find_elements(
        By.XPATH, "//div[@class='css-175oi2r' and @data-testid='cellInnerDiv' and .//button[.//span[text()='Follow']]]")
    if (len(unfollower_interactions) > 0):
        click(unfollower_interactions[0])
        return if_user_is_unmute_press_follow_button()


def click(item):
    item.click()
    time.sleep(3)


def post_reply_path(notification):
    click(notification)
    analyticsButton = driver.find_element(
        By.CSS_SELECTOR, "[data-testid='analyticsButton']")
    click(analyticsButton)

    sw_find_new_follower = True
    while (sw_find_new_follower):
        sw_find_new_follower = False

        repostTab = driver.find_element(
            By.XPATH, "//a[@role='tab' and .//span[text()='Reposts']]")
        click(repostTab)
        if check_and_follow_if_everything_is_ok():
            sw_find_new_follower = True

    sw_find_new_follower = True
    while (sw_find_new_follower):
        sw_find_new_follower = False

        likeTab = driver.find_element(
            By.XPATH, "//a[@role='tab' and .//span[text()='Likes']]")
        click(likeTab)
        if check_and_follow_if_everything_is_ok():
            sw_find_new_follower = True


def repost_path(notification):
    repost_liker_list = notification.find_elements(
        By.CSS_SELECTOR, "div[data-testid^='UserAvatar-Container-']")
    click(repost_liker_list[0])
    if_user_is_unmute_press_follow_button()
    
    
def check_local_limitation_rate():
    try:
        element = driver.find_element(By.XPATH, "//*[text()='local_rate_limited']")
        return True
    except:
        pass

    try:
        button = driver.find_element(By.XPATH, "//button[.//span[text()='Retry']]")
        return True
    except:
        pass

    try:
        span_element = driver.find_element(By.XPATH, "//span[text()='Something went wrong. Try reloading.']")
        return True
    except:
        pass

    return False
# لیست کلیه کسانی که در نوتیفیکیشن حضور دارند از دیتابیس حذف می شود تا فقط افرادی که اینتراکشنی نداشته اند در آن باقی بمانند
def delete_itractive_user_from_db():
    intractors = driver.find_elements(
                    By.CSS_SELECTOR, "a.css-175oi2r.r-1pi2tsx.r-13qz1uu.r-o7ynqc.r-6416eg.r-1ny4l3l.r-1loqt21")
    conn = sqlite3.connect('following.db')
    cursor = conn.cursor()
    for user in intractors:
        user_link = user.get_attribute("href")
        cursor.execute('''
        DELETE FROM following_table
        WHERE user_name = ?
        ''', (user_link,))
    conn.commit()
    conn.close()

def main():
    try:
        driver.get("https://x.com/notifications")
        time.sleep(3)
        #  اسکرول آپ کردن به ابتدای نتیفیکیشن ها
        driver.execute_script("window.scrollTo(0, 0);")

        if (was_the_notifications_loaded()):
            notifications = driver.find_elements(      #  لیست کل نوتیفیکشن های درون قسمت نوتیفیکیشن ها را تهیه می کند
                By.CSS_SELECTOR, "div.css-175oi2r[data-testid='cellInnerDiv']")
            find_sw = False
            for index, notification in enumerate(notifications):
                article = notification.find_element(By.TAG_NAME, "article")
                if not ("r-1eltapf" in article.get_attribute("class")):
                    break  # یعنی به یک نوتیفیکشن غیر هایلایت رسیده ایم و باید کار را متوقف کنیم

                if index > 10:
                    break
                discription = notification.find_element(   #  توصیف می کند که چه نوع نوتیفیکشنی داریم 
                    By.CSS_SELECTOR, "div.css-146c3p1.r-bcqeeo.r-1ttztb7.r-qvutc0.r-37j5jr.r-a023e6.r-rjixqe.r-16dba41.r-1udh08x")
                # print(index, ' - ', discription.text[-9:])
                if (discription.text[-9:] == "your post" or discription.text[-10:] == "your reply" or discription.text[-11:] == "your repost"):
                    find_sw = True
                    break
            if (find_sw):
                if (discription.text[-11:] == "your repost"):   #  لایک یا ری پست چیزی که من از کاربر دیگری ری پست کرده ام
                    repost_path(notification)
                else:
                    post_reply_path(notification)    #  نوشته من (پست یا ریپلای) را لایک یا ری پست کرده اند

            else:  # اگر هیچ عنصری برای لایک یا ریتوییتی وجود نداشته باشد
                driver.get("https://x.com/notifications")
                time.sleep(5)
        else:  # رفع مشکل اینکه صفحه لود نشود
            driver.get("https://x.com/notifications")
            time.sleep(5)
    except:
        {}


if __name__ == '__main__':
    while True:

        if check_local_limitation_rate():
            time.sleep(30 * 60)
            driver.get("https://x.com/")
            time.sleep(3)
            continue
       
        main()
        time.sleep(5)