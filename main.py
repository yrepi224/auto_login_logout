import random
import schedule
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("auto_login_logout.log"), logging.StreamHandler()])


def login_and_check(username, password):
    # 크롬 드라이버 경로 설정
    service = Service('driver/chromedriver.exe')  # 크롬 드라이버 경로를 설정하세요
    driver = webdriver.Chrome(service=service)

    try:
        # 웹사이트 로그인 페이지로 이동
        driver.get('http://gw.vaiv.kr/gw/uat/uia/egovLoginUsr.do')  # 로그인 페이지 URL을 설정하세요
        logging.info('로그인 페이지에 접속했습니다.')

        # 로그인 과정
        username_input = driver.find_element(By.ID, 'userId')  # 사용자명 입력 필드의 ID
        password_input = driver.find_element(By.ID, 'userPw')  # 비밀번호 입력 필드의 ID
        login_button = driver.find_element(By.CLASS_NAME, 'log_btn')  # 로그인 버튼의 CLASS

        username_input.send_keys(username)  # 사용자명 입력
        password_input.send_keys(password)  # 비밀번호 입력
        login_button.click()  # 로그인 버튼 클릭
        logging.info('로그인 정보를 입력하고 로그인 버튼을 클릭했습니다. (비밀번호는 기록되지 않음)')

        # 로그인 확인
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//li[@rel='tab2']"))
        )
        logging.info('로그인에 성공했습니다.')
        return driver

    except Exception as e:
        logging.error(f'로그인 오류 발생: {e}')
        driver.quit()
        logging.info('브라우저를 종료했습니다.')
        return None


def click_attendance_button(driver, button_rel, tab_id):
    try:
        # 로그인 완료 후 버튼 클릭 대기
        button_xpath = f"//li[@rel='{button_rel}']"
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, button_xpath))
        )
        button.click()  # li 버튼 클릭
        logging.info(f'{button_rel} 버튼을 클릭했습니다.')

        # 해당 div 내의 a 태그 클릭 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//div[@id='{tab_id}']//a"))
        )
        attendance_button = driver.find_element(By.XPATH, f"//div[@id='{tab_id}']//a")
        attendance_button.click()  # a 태그 클릭
        logging.info(f'{tab_id} 내의 출퇴근 버튼을 클릭했습니다.')

        # 모달창에서 확인 버튼 클릭 대기
        confirm_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'btnConfirm'))
        )
        confirm_button.click()  # 확인 버튼 클릭
        logging.info('모달창의 확인 버튼을 클릭했습니다.')

    except Exception as e:
        logging.error(f'오류 발생: {e}')
    finally:
        driver.quit()  # 브라우저 종료
        logging.info('브라우저를 종료했습니다.')


def schedule_jobs(username, password):
    # 월화수목금 8시 55분 ~ 8시 58분 사이에 출근 버튼 클릭
    for day in [schedule.every().monday, schedule.every().tuesday, schedule.every().wednesday,
                schedule.every().thursday, schedule.every().friday]:
        random_minute = random.randint(55, 58)
        random_time = f"08:{random_minute:02d}"
        day.at(random_time).do(lambda: click_attendance_button(
            login_and_check(username, password), 'tab1', 'portletTemplete_mybox_tab1'))
        logging.info(f'출근 버튼 클릭 스케줄 설정: {day} at {random_time} (사용자: {username})')

    # 월화수목금 6시 03분에 퇴근 버튼 클릭
    for day in [schedule.every().monday, schedule.every().tuesday, schedule.every().wednesday,
                schedule.every().thursday, schedule.every().friday]:
        day.at("18:03").do(lambda: click_attendance_button(
            login_and_check(username, password), 'tab2', 'portletTemplete_mybox_tab2'))
        logging.info(f'퇴근 버튼 클릭 스케줄 설정: {day} at 18:03 (사용자: {username})')


def main():
    # 사용자로부터 아이디와 패스워드를 입력받음
    username = input("아이디를 입력하세요: ")
    password = input("패스워드를 입력하세요: ")

    schedule_jobs(username, password)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
