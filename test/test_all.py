from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_launch() -> None:
    opts: FirefoxOptions = FirefoxOptions()  # type:ignore
    opts.add_argument("--headless")  # type:ignore
    driver = webdriver.Firefox(options=opts)  # type:ignore

    driver.get("localhost:8888/build")
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "troubadour_tooltip_0"))
    )
    assert "doomed" in driver.find_element(By.ID, "story").text
