import pytest
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from troubadour.rich_text import RichText


@pytest.mark.web
def test_launch() -> None:
    opts: FirefoxOptions = FirefoxOptions()
    opts.add_argument("--headless")
    driver = webdriver.Firefox(options=opts)

    # load page
    driver.get("localhost:8888/build")
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "troubadour_tooltip_0"))
    )

    story = driver.find_element(By.ID, "story")
    story_interface = driver.find_element(By.ID, "story-interface")

    # basic check of initial page
    assert "doomed" in story.text
    buttons = story_interface.find_elements(By.CLASS_NAME, "button")
    assert len(buttons) == 1

    # click first button and check output
    buttons[0].click()
    assert "sit amet sodales" in story.text
    buttons = story_interface.find_elements(By.CLASS_NAME, "button")
    assert len(buttons) == 2
    assert buttons[1].text == "Send"

    # click second button and check output
    buttons[1].click()
    assert "This is the message: hello world" in story.text
    buttons = story_interface.find_elements(By.CLASS_NAME, "button")
    assert [b.text for b in buttons] == ["Pouac", "Pouic"]


def test_richtext() -> None:
    # Basic format
    a = RichText("Hello {}!").format("world")
    assert a.render() == ("<p>Hello world!</p>\n", {})

    # Markdown
    b = RichText("# Hello\nWorld!")
    assert b.render() == ("<h1>Hello</h1>\n<p>World!</p>\n", {})

    # Tooltip
    c = RichText("This is not clear").tooltip("explanation")
    assert c.render() == (
        (
            '<p><span id="troubadour_tooltip_0" class="tooltip">'
            "This is not clear</span></p>\n"
        ),
        {"troubadour_tooltip_0": "<p>explanation</p>\n"},
    )
