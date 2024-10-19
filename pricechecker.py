import asyncio
import telegram
import schedule
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from datetime import datetime

# PriceChecker 봇 데이터
TOKEN = ""
CHAT_ID = 
bot = telegram.Bot(TOKEN)

print("정상적으로 프로그램이 실행됨.")

# 비동기적으로 웹 크롤링
async def web_crawling():
    options = webdriver.ChromeOptions()
    options.add_argument('window-size=607,1080') #웹사이트 크기
    options.add_argument('headless') # 백그라운드에서 웹사이트가 실행되게

    driver = webdriver.Chrome(options=options)
    driver.get('https://www.binance.com/en/futures/markets/overview-um') #웹사이트 주소

    # 웹사이트 확대 배율
    driver.execute_script("document.body.style.zoom='130%';")

    # 불필요한 상단 head를 모두 삭제함
    element_xpaths = [
        '//*[@id="__APP"]/div[1]',
        '//*[@id="__APP"]/div[2]/div[1]',
        '//*[@id="__APP"]/div[2]/div[2]/div/div[1]/div[1]',
        '//*[@id="__APP"]/div[2]/div[2]/div/div[1]/div[2]/div/div[1]'
    ]

    for element_xpaths in element_xpaths:
        driver.execute_script(f"document.evaluate('{element_xpaths}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.style.display='none';")

    # 현재 시간을 웹사이트에 삽입
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    driver.execute_script(f"""
        var timeElement = document.createElement('div');
        timeElement.innerHTML = '<h1 style="position: fixed; top: 0px; left: 5px; font-size: 24px; color: white; z-index: 9999;">{current_time}</h1>';
        document.body.appendChild(timeElement);
    """)

    # 쿠키 배너 차단
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="onetrust-reject-all-handler"]'))
        ).click()
    except Exception as e:
        print(f'쿠키 배너를 찾을 수 없음: {e}')
    sleep(1)

    # 코드 단축용 함수
    def change_click():
        driver.find_element(By.XPATH, '//*[@id="__APP"]/div[2]/div[2]/div/div[1]/div[2]/div/div[2]/div[1]/div/div/div/div/table/thead/tr/th[3]/div').click()
        sleep(1)

    # 스크린샷 1
    change_click()
    driver.save_screenshot("binance-lose.png")

    # 스크린샷 2
    change_click()
    driver.save_screenshot("binance-gain.png")
    
    driver.quit()

# 비동기적으로 저장된 이미지를 묶음 형식으로 전송
async def send_image_to_telegram():
    media = []
    with open("binance-gain.png", 'rb') as gain_img, open("binance-lose.png", 'rb') as lose_img:
        media.append(telegram.InputMediaPhoto(gain_img))
        media.append(telegram.InputMediaPhoto(lose_img))

    await bot.send_media_group(CHAT_ID, media)

async def run_async_task():
    await web_crawling() # 웹 크롤링 수행
    await send_image_to_telegram() # 텔레그램으로 이미지 전송

def schedule_task():
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.ensure_future(run_async_task())
    else:
        loop.run_until_complete(run_async_task())

if __name__ == "__main__":
    schedule.every().hour.at(":00").do(schedule_task) # 매 시 정각마다 schedule_task 함수를 수행
    while True:
        schedule.run_pending()
        sleep(1)
