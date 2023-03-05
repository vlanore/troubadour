from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_launch() -> None:
    opts: FirefoxOptions = FirefoxOptions()
    opts.add_argument("--headless")
    driver = webdriver.Firefox(options=opts)

    driver.get("localhost:8888/build")
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "troubadour_tooltip_0"))
    )

    story = driver.find_element(By.ID, "story")
    story_interface = driver.find_element(By.ID, "story-interface")

    assert "doomed" in story.text
    buttons = story_interface.find_elements(By.CLASS_NAME, "button")
    assert len(buttons) == 1
    buttons[0].click()

    assert "sit amet sodales" in story.text
    buttons = story_interface.find_elements(By.CLASS_NAME, "button")
    assert len(buttons) == 2
