from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Optional
from enum import Enum

import jsonpickle as jsp

from troubadour.id import get_id
import troubadour.interfaces as itf
import troubadour.pyscript_render as psr
from troubadour.rich_text import RichText, make_rich_text


@dataclass
class InfoPanel(itf.InfoPanel):
    text: RichText
    title: Optional[RichText] = None
    markdown: bool = True

    def set_title(self, text: Optional[str | RichText]) -> None:
        if text is None:
            self.title = None
        else:
            self.title = make_rich_text(text)

    def get_title(self) -> Optional[RichText]:
        return self.title

    def set_text(self, text: str | RichText, markdown: bool = True) -> None:
        self.text = make_rich_text(text)
        self.markdown = markdown

    def get_text(self) -> RichText:
        return self.text


@dataclass
class ImagePanel(itf.ImagePanel):
    url = ""
    alt = ""

    def get_url(self) -> str:
        return self.url

    def set_url(self, value: str) -> None:
        self.url = value

    def get_alt(self) -> str:
        return self.alt

    def set_alt(self, value: str) -> None:
        self.alt = value


class ColorMode(Enum):
    light = 1
    dark = 2


@dataclass
class GameState:
    game: itf.Game
    interface: list[itf.Input]


@dataclass
class GameSave:
    nb: int
    name: str
    save: GameState
    date: datetime


@dataclass
class GameSaves:
    saves: list[GameSave] = field(default_factory=list)

    def init(self) -> None:
        def load_saves(saves: GameSaves) -> None:
            old_saves = psr.local_storage(GameSaves)["saves"]
            assert old_saves is not None
            old_saves.merge(saves)
            old_saves.render()
            psr.local_storage["saves"] = old_saves

        psr.on_file_upload("load-modal-import", load_saves, GameSaves)

    def render(self) -> None:
        psr.clear("saves-table")
        for save in self.saves:
            psr.insert_end(
                "saves-table",
                f"""
<tr>
    <th>{save.nb}</th>
    <th>{save.name}</th>
    <th>{save.date.strftime("%Y-%m-%d %H:%M")}</th>
    <th>
        <a id="troubadour-load-{save.nb}" href="javascript:void(0);">Load</a> -
        <a id="troubadour-rmsave-{save.nb}" href="javascript:void(0);">Delete</a>
    </th>
</tr>""",
            )
            psr.onclick(
                f"troubadour-rmsave-{save.nb}",
                lambda _, id=save.nb: delete_save(id),  # type:ignore
            )
            psr.onclick(
                f"troubadour-load-{save.nb}",
                lambda _, id=save.nb: load_save(id),  # type:ignore
            )

        psr.file_download_button(
            "load-modal-download",
            str(jsp.encode(self)),
            f"saves{datetime.today().strftime('-%Y%m%d-%H%M')}.json",
        )

    def get_next_id(self) -> int:
        if self.saves == []:
            return 0
        else:
            return max(save.nb for save in self.saves) + 1

    def merge(self, other: "GameSaves") -> None:
        next_id = self.get_next_id()
        for save in other.saves:
            if save not in self.saves:
                save.nb = next_id
                next_id += 1
                self.saves.append(save)


def render_porthole(porthole: Optional[itf.ImagePanel]) -> None:
    if porthole is not None:
        psr.set_display("porthole-container", "block")
        psr.set_src("porthole", porthole.get_url())
        psr.set_alt("porthole", porthole.get_alt())
    else:
        psr.set_display("porthole-container", "none")


def render_info(info: Optional[itf.InfoPanel]) -> None:
    if info is not None:
        psr.set_display("info", "block")
        text, tooltips = info.get_text().render()
        psr.set_html("info-content", text)

        title = info.get_title()
        if title is not None:
            title_text, title_tooltips = title.render()
            psr.set_html("info-title", title_text)
            tooltips |= title_tooltips
            psr.set_display("info-header", "flex")
        else:
            psr.set_display("info-header", "none")

        for id, text in tooltips.items():
            psr.add_tooltip(id, text)
    else:
        psr.set_display("info", "none")


@dataclass
class Story(itf.Story):
    history: list[itf.Cmd] = field(default_factory=list)

    def display(self, text: str | RichText) -> None:
        rich_text = make_rich_text(text)

        self.history.insert(0, itf.DisplayCmd(rich_text))

        html_text, tooltips = rich_text.render()

        psr.display_story(html_text)

        for name, tt in tooltips.items():
            psr.add_tooltip(name, tt)

    def newpage(self) -> None:
        self.history.insert(0, itf.NewPageCmd())
        t = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        psr.display_story(f'<div class="divider">{t}</div>')

    def image(self, url: str, alt: str) -> None:
        self.history.insert(0, itf.ImageCmd(url, alt))
        id = get_id()
        psr.display_story(
            f"""<div class="card">
                <div class="card-image">
                    <figure class="image">
                    <img id="troubadour_image_{id}" src="{url}" alt="{alt}">
                    </figure>
                </div>
            </div>"""
        )
        psr.onload(f"troubadour_image_{id}", lambda _: psr.scroll_to_bottom("story"))


def add_button(
    text: str, continuation: Callable, tooltip: Optional[str] = None
) -> None:
    id = get_id()
    psr.insert_end(
        "story-interface",
        (
            '<button class="button" type="button" '
            f'id="troubadour_button_{id}">{text}</button>'
        ),
    )
    psr.onclick(f"troubadour_button_{id}", continuation)


def add_text_input(
    continuation: Callable[[str], None],
    button_text: str,
    default_value: str = "",
    placeholder_text: str = "",
) -> None:
    id = get_id()
    psr.insert_end(
        "story-interface",
        f"""
        <div class="field has-addons">
            <div class="control is-flex-grow-1">
                <input id="troubadour_inputtext_input_{id}"
                    class="input" type="text" placeholder="{placeholder_text}">
            </div>
            <div class="control">
                <a id="troubadour_inputtext_button_{id}" class="button">
                    {button_text}
                </a>
            </div>
        </div>""",
    )

    def callback(_: Any) -> None:
        value: str = psr.get_value(f"troubadour_inputtext_input_{id}")
        if value == "":
            value = default_value
        continuation(value)

    psr.onclick(f"troubadour_inputtext_button_{id}", callback)


def get_state() -> Optional[GameState]:
    return psr.local_storage(GameState)["state"]


def get_saves() -> Optional[GameSaves]:
    return psr.local_storage(GameSaves)["saves"]


def render_interface(game: itf.Game, interface: list[itf.Input]) -> None:
    for element in interface:
        match element:
            case itf.Button(text, _method, tooltip):
                add_button(
                    text,
                    lambda _, _method=_method: run_page(game, _method),
                    tooltip,
                )
            case itf.TextInput(
                button_text=button_text,
                method=method,
                default_value=default_value,
                placeholder_text=placeholder_text,
            ):
                add_text_input(
                    lambda v, _m=method: run_page(game, _m, msg=v),  # type:ignore
                    button_text,
                    default_value,
                    placeholder_text,
                )
            case _:
                raise NotImplementedError()


def run_page(game: itf.Game, method: str, **args: Any) -> None:
    interface = getattr(game, method)(**args)
    render_info(game.info)
    render_porthole(game.porthole)
    psr.clear("story-interface")
    render_interface(game, interface)
    psr.local_storage["state"] = GameState(game, interface)


def save_game() -> None:
    saves = get_saves()
    state = get_state()
    assert isinstance(state, GameState)
    assert isinstance(saves, GameSaves)
    id = saves.get_next_id()
    name = psr.get_value("save-input")
    time = datetime.today()
    saves.saves.append(GameSave(id, name, state, time))
    saves.render()
    psr.local_storage["saves"] = saves
    psr.remove_class("save-modal", "is-active")


def delete_save(id: int) -> None:
    saves = get_saves()
    assert isinstance(saves, GameSaves)
    saves.saves = [save for save in saves.saves if save.nb != id]
    psr.local_storage["saves"] = saves
    saves.render()


def load_save(id: int) -> None:
    saves = get_saves()
    assert isinstance(saves, GameSaves)
    save = next(save for save in saves.saves if save.nb == id)
    psr.local_storage["state"] = save.save
    load_cache_data(None)
    psr.remove_class("load-modal", "is-active")


def run_game(game: itf.Game) -> None:
    # saves
    match get_saves():
        case None:
            saves = GameSaves()
            psr.local_storage["saves"] = saves
        case GameSaves() as saves:
            saves.render()
    saves.init()

    psr.onclick("load-button", lambda _: psr.activate_modal("load-modal"))
    psr.onclick("load-modal-cancel", lambda _: psr.deactivate_modal("load-modal"))
    psr.onclick("save-button", lambda _: psr.activate_modal("save-modal"))
    psr.onclick("save-modal-save", lambda _: save_game())
    psr.onclick("save-modal-cancel", lambda _: psr.deactivate_modal("save-modal"))
    psr.onclick("load-modal-import-button", lambda _: psr.click("load-modal-import"))

    # dark mode
    psr.onclick("dark-mode-toggle", toggle_mode)

    # resume modal
    def restart(_: Any) -> None:
        run_page(game, "start")
        close_resume_modal(None)
        psr.add_class("screen-cover", "invisible")  # remove screen cover

    psr.onclick("resume-modal-restart", restart)
    psr.onclick("resume-modal-load", load_cache_data)

    # restart button
    def restart2(_: Any, new_game: itf.Game = deepcopy(game)) -> None:
        psr.clear("story")
        run_page(deepcopy(new_game), "start")
        psr.deactivate_modal("restart-modal")

    psr.onclick("restart-button", lambda _: psr.activate_modal("restart-modal"))
    psr.onclick("restart-modal-restart", restart2)
    psr.onclick(
        "restart-modal-cancel",
        lambda _: psr.deactivate_modal("restart-modal"),
    )

    # python terminal
    psr.onclick("python-button", lambda _: psr.activate_modal("python-modal"))
    psr.onclick(
        "python-modal-cancel",
        lambda _: psr.deactivate_modal("python-modal"),
    )

    # tooltips
    psr.add_tooltip("save-button", "Save current game")
    psr.add_tooltip("load-button", "Load game and manage saves")
    psr.add_tooltip("python-button", "Access the python console")
    psr.add_tooltip("dark-mode-toggle", "Toggle color mode (light/dark)")
    psr.add_tooltip("restart-button", "Restart the game")

    # color mode
    match psr.local_storage(ColorMode)["color-mode"]:
        case None:
            psr.local_storage["color-mode"] = ColorMode.light
        case ColorMode.dark:
            enable_dark_mode()

    # start game
    match get_state():
        case None:
            run_page(game, "start")
            psr.add_class("screen-cover", "invisible")  # remove screen cover
        case GameState():
            psr.activate_modal("resume-modal")


def enable_light_mode() -> None:
    psr.disable("dark-style")
    psr.enable("light-style")
    psr.remove_class("body", "dark-mode")
    psr.remove_class("dark-mode-icon", "fa-sun")
    psr.add_class("dark-mode-icon", "fa-moon")
    psr.local_storage["color-mode"] = ColorMode.light


def enable_dark_mode() -> None:
    psr.enable("dark-style")
    psr.disable("light-style")
    psr.add_class("body", "dark-mode")
    psr.remove_class("dark-mode-icon", "fa-moon")
    psr.add_class("dark-mode-icon", "fa-sun")
    psr.local_storage["color-mode"] = ColorMode.dark


def toggle_mode(_: Any) -> None:
    color_mode = psr.local_storage(ColorMode)["color-mode"]
    assert color_mode is not None
    if color_mode == ColorMode.dark:
        enable_light_mode()
    elif color_mode == ColorMode.light:
        enable_dark_mode()


def close_resume_modal(_: Any) -> None:
    psr.remove_class("resume-modal", "is-active")


def load_cache_data(_: Any) -> None:
    state = get_state()
    assert isinstance(state, GameState)

    psr.clear("story")
    old_history = state.game.story.history.copy()
    state.game.story.history = []
    for cmd in reversed(old_history):
        match cmd:
            case itf.DisplayCmd(text):
                state.game.story.display(text)
            case itf.NewPageCmd():
                state.game.story.newpage()
            case itf.ImageCmd(url, alt):
                state.game.story.image(url, alt)
            case _:
                raise NotImplementedError()

    render_info(state.game.info)
    render_porthole(state.game.porthole)

    psr.clear("story-interface")
    render_interface(state.game, state.interface)

    close_resume_modal(None)
    psr.add_class("screen-cover", "invisible")  # remove screen cover
