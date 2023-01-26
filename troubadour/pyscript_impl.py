from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Callable, Any

import jsonpickle as jsp
import mistune
from pyodide.code import run_js  # type: ignore
from pyodide.ffi import create_proxy  # type: ignore
from pyscript import HTML  # type: ignore
from pyscript import Element  # type: ignore
from pyscript import display as psdisplay  # type: ignore
from pyscript import js  # type: ignore

from troubadour.interfaces import (
    AbstractGame,
    AbstractImagePanel,
    AbstractInfoPanel,
    AbstractInterface,
    AbstractStory,
    Button,
    ImageCmd,
    DisplayCmd,
    NewPageCmd,
    Cmd,
)
from troubadour.troubadown import troubadownify
from troubadour.id import get_id


class InfoPanel(AbstractInfoPanel):
    def __init__(self) -> None:
        self.title: Optional[str] = None
        self.text = ""

    def set_title(self, text: str) -> None:
        self.title = text

    def get_title(self) -> Optional[str]:
        return self.title

    def set_text(self, text: str, markdown: bool = True) -> None:
        self.text = text
        self.markdown = markdown

    def get_text(self) -> tuple[str, bool]:
        return self.text, self.markdown


class ImagePanel(AbstractImagePanel):
    def __init__(self) -> None:
        self.url = ""
        self.alt = ""

    def get_url(self) -> str:
        return self.url

    def set_url(self, value: str) -> None:
        self.url = value

    def get_alt(self) -> str:
        return self.alt

    def set_alt(self, value: str) -> None:
        self.alt = value


@dataclass
class GameState:
    game: AbstractGame
    interface: list[AbstractInterface]
    color_mode: str


@dataclass
class GameSave:
    nb: int
    name: str
    save: GameState
    date: datetime


@dataclass
class GameSaves:
    saves: list[GameSave] = field(default_factory=list)

    def render(self) -> None:
        Element("saves-table").element.innerHTML = ""
        for save in self.saves:
            Element("saves-table").element.insertAdjacentHTML(
                "beforeend",
                f"""
            <tr>
                <th>{save.nb}</th>
                <th>{save.name}</th>
                <th>{save.date.strftime("%Y-%m-%d %H:%M:%S")}</th>
                <th>
                    <a id="troubadour-load-{save.nb}" href="javascript:void(0);">Load</a> -
                    <a id="troubadour-rmsave-{save.nb}" href="javascript:void(0);">Delete</a>
                </th>
            </tr>""",
            )


def render_porthole(porthole: AbstractImagePanel) -> None:
    Element("porthole").element.src = porthole.get_url()
    Element("porthole").element.alt = porthole.get_alt()


def render_panels(info: AbstractInfoPanel, extra: AbstractInfoPanel) -> None:
    extra_raw, extra_md = extra.get_text()
    extra_html = mistune.html(extra_raw) if extra_md else extra_raw
    Element("extra-content").element.innerHTML = extra_html
    Element("extra-title").element.innerHTML = extra.get_title()

    info_raw, info_md = info.get_text()
    info_html = mistune.html(info_raw) if info_md else info_raw
    Element("info-content").element.innerHTML = info_html
    Element("info-title").element.innerHTML = info.get_title()


def render_tooltip(id: int, text: str) -> None:
    run_js(
        f"""tippy("#troubadour_tooltip_{id}",
                {{
                    content:"{text}",
                    allowHTML:true,
                }}
            );"""
    )


@dataclass
class Story(AbstractStory):
    history: list[Cmd] = field(default_factory=list)

    def _scroll_to_bottom(self) -> None:
        tgt = Element("story").element
        tgt.scrollTop = tgt.scrollHeight

    def display(
        self,
        text: str,
        markdown: bool = True,
        tooltips: Optional[list[str]] = None,
        named_tooltips: Optional[dict[str, str]] = None,
    ) -> None:
        self.history.insert(0, DisplayCmd(text, markdown, tooltips, named_tooltips))

        html, tt_labels = troubadownify(text)

        if markdown:
            psdisplay(HTML(mistune.html(html)), target="story")
        else:
            psdisplay(HTML(html), target="story")

        if tooltips is not None:
            for i, tt in enumerate(tooltips):
                render_tooltip(tt_labels[i], tt)

        if named_tooltips is not None:
            for name, tt in named_tooltips.items():
                render_tooltip(tt_labels[name], tt)

        self._scroll_to_bottom()

    def newpage(self) -> None:
        self.history.insert(0, NewPageCmd())
        t = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        psdisplay(HTML(f'<div class="divider">{t}</div>'), target="story")
        self._scroll_to_bottom()

    def image(self, url: str, alt: str) -> None:
        self.history.insert(0, ImageCmd(url, alt))
        id = get_id()
        psdisplay(
            HTML(
                f"""<div class="card">
                <div class="card-image">
                    <figure class="image">
                    <img id="troubadour_image_{id}" src="{url}" alt="{alt}">
                    </figure>
                </div>
            </div>"""
            ),
            target="story",
        )

        stb = lambda _: self._scroll_to_bottom()

        Element(f"troubadour_image_{id}").element.addEventListener(
            "load", create_proxy(stb)
        )


def add_button(
    text: str, continuation: Callable, tooltip: Optional[str] = None
) -> None:
    id = get_id()
    Element("story-interface").element.insertAdjacentHTML(
        "beforeend",
        (
            '<button class="button" type="button" '
            f'id="troubadour_button_{id}">{text}</button>'
        ),
    )
    onclick(f"troubadour_button_{id}", continuation)


def get_state() -> Optional[GameState]:
    encoded_state = js.localStorage.getItem("state")
    if encoded_state is not None:
        state = jsp.decode(encoded_state)
        assert isinstance(state, GameState)
        return state
    else:
        return None


def get_saves() -> Optional[GameSaves]:
    encoded_saves = js.localStorage.getItem("saves")
    if encoded_saves is not None:
        saves = jsp.decode(encoded_saves)
        assert isinstance(saves, GameSaves)
        return saves
    else:
        return None


def run_page(game: AbstractGame, method: str) -> None:
    interface = getattr(game, method)()
    render_panels(game.info, game.extra)
    render_porthole(game.porthole)
    Element("story-interface").element.innerHTML = ""
    for element in interface:
        match element:
            case Button(text, _method, tooltip):  # type:ignore
                add_button(
                    text, lambda _, _method=_method: run_page(game, _method), tooltip
                )
            case _:
                raise NotImplementedError()
    js.localStorage.setItem("state", jsp.encode(GameState(game, interface, LIGHT_MODE)))


def onclick(id: str, func: Callable[[Any], None]) -> None:
    Element(id).element.addEventListener("click", create_proxy(func))


def save_game() -> None:
    saves = get_saves()
    state = get_state()
    assert isinstance(state, GameState)
    assert isinstance(saves, GameSaves)
    id = max(save.nb for save in saves.saves) + 1
    name = Element("save-input").element.value
    time = datetime.today()
    saves.saves.append(GameSave(id, name, state, time))
    saves.render()
    js.localStorage.setItem("saves", jsp.encode(saves))
    Element("save-modal").remove_class("is-active")


def run_game(game: AbstractGame) -> None:
    # saves
    match get_saves():
        case None:
            js.localStorage.setItem("saves", jsp.encode(GameSaves()))
        case GameSaves() as saves:
            saves.render()

    onclick("load-button", lambda _: Element("load-modal").add_class("is-active"))
    onclick(
        "load-modal-cancel", lambda _: Element("load-modal").remove_class("is-active")
    )
    onclick("save-button", lambda _: Element("save-modal").add_class("is-active"))
    onclick("save-modal-save", lambda _: save_game())
    onclick(
        "save-modal-cancel", lambda _: Element("save-modal").remove_class("is-active")
    )

    # dark mode
    onclick("dark-mode-toggle", toggle_mode)

    # reload modal
    def restart(_: Any) -> None:
        run_page(game, "start")
        close_reload_modal(None)

    onclick("reload-modal-restart", restart)
    onclick("reload-modal-load", load_cache_data)

    # restart button
    def restart2(_: Any, new_game: AbstractGame = deepcopy(game)) -> None:
        Element("story").element.innerHTML = ""
        run_page(deepcopy(new_game), "start")
        Element("restart-modal").remove_class("is-active")

    onclick("restart-button", lambda _: Element("restart-modal").add_class("is-active"))
    onclick("restart-modal-restart", restart2)
    onclick(
        "restart-modal-cancel",
        lambda _: Element("restart-modal").remove_class("is-active"),
    )

    # start game
    match get_state():
        case None:
            run_page(game, "start")
        case GameState(color_mode=color_mode):
            if color_mode == "dark":
                toggle_mode(None)
            Element("reload-modal").add_class("is-active")


LIGHT_MODE = "light"


def toggle_mode(_: Any) -> None:
    global LIGHT_MODE
    if LIGHT_MODE == "dark":
        Element("dark-style").element.disabled = "disabled"
        Element("light-style").element.disabled = None
        Element("story").remove_class("dark-mode")
        LIGHT_MODE = "light"
        Element("dark-mode-icon").remove_class("fa-sun")
        Element("dark-mode-icon").add_class("fa-moon")
    elif LIGHT_MODE == "light":
        Element("dark-style").element.disabled = None
        Element("light-style").element.disabled = "disabled"
        Element("story").add_class("dark-mode")
        LIGHT_MODE = "dark"
        Element("dark-mode-icon").remove_class("fa-moon")
        Element("dark-mode-icon").add_class("fa-sun")
    state = jsp.decode(js.localStorage.getItem("state"))
    assert isinstance(state, GameState)
    state.color_mode = LIGHT_MODE
    js.localStorage.setItem("state", jsp.encode(state))


def close_reload_modal(_: Any) -> None:
    Element("reload-modal").remove_class("is-active")


def load_cache_data(_: Any) -> None:
    state = jsp.decode(js.localStorage.getItem("state"))
    assert isinstance(state, GameState)

    Element("story").element.innerHTML = ""
    old_history = state.game.story.history.copy()
    state.game.story.history = []
    for cmd in reversed(old_history):
        match cmd:
            case DisplayCmd(text, markdown, tooltips, named_tooltips):  # type:ignore
                state.game.story.display(text, markdown, tooltips, named_tooltips)
            case NewPageCmd():  # type:ignore
                state.game.story.newpage()
            case ImageCmd(url, alt):  # type:ignore
                state.game.story.image(url, alt)
            case _:
                raise NotImplementedError()

    render_panels(state.game.info, state.game.extra)
    render_porthole(state.game.porthole)

    Element("story-interface").element.innerHTML = ""
    for element in state.interface:
        match element:
            case Button(text, _method, tooltip):  # type:ignore
                add_button(
                    text,
                    lambda _, _method=_method: run_page(state.game, _method),
                    tooltip,
                )
            case _:
                raise NotImplementedError()

    close_reload_modal(None)


if __name__ == "__main__":
    s = Story()
    i = InfoPanel()
