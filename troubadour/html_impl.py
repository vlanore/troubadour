from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Optional

import jsonpickle as jsp
import mistune
from pyscript import HTML  # type: ignore
from pyscript import display as psdisplay  # type: ignore

from troubadour.id import get_id
from troubadour.interfaces import (
    AbstractGame,
    AbstractImagePanel,
    AbstractInfoPanel,
    AbstractInterface,
    AbstractStory,
    Button,
    Cmd,
    DisplayCmd,
    ImageCmd,
    NewPageCmd,
    TextInput,
)
from troubadour.troubadown import troubadownify
import troubadour.pyscript_render as psr


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
        psr.onclick("load-modal-import", lambda _: None)  # TODO
        psr.file_download_button("load-modal-download", str(jsp.encode(self)))

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


def render_porthole(porthole: AbstractImagePanel) -> None:
    psr.set_src("porthole", porthole.get_url())
    psr.set_alt("porthole", porthole.get_alt())


def render_panels(info: AbstractInfoPanel, extra: AbstractInfoPanel) -> None:
    extra_raw, extra_md = extra.get_text()
    extra_html = mistune.html(extra_raw) if extra_md else extra_raw
    psr.set_html("extra-content", extra_html)
    psr.set_html("extra-title", str(extra.get_title()))

    info_raw, info_md = info.get_text()
    info_html = mistune.html(info_raw) if info_md else info_raw
    psr.set_html("info-content", info_html)
    psr.set_html("info-title", str(info.get_title()))


@dataclass
class Story(AbstractStory):
    history: list[Cmd] = field(default_factory=list)

    # def _scroll_to_bottom(self) -> None:
    #     tgt = Element("story").element
    #     tgt.scrollTop = tgt.scrollHeight

    def display(
        self,
        text: str,
        markdown: bool = True,
        tooltips: Optional[list[str]] = None,
        named_tooltips: Optional[dict[str, str]] = None,
    ) -> None:
        self.history.insert(0, DisplayCmd(text, markdown, tooltips, named_tooltips))

        html_text, tt_labels = troubadownify(text)

        if markdown:
            psdisplay(HTML(mistune.html(html_text)), target="story")
        else:
            psdisplay(HTML(html_text), target="story")

        if tooltips is not None:
            for i, tt in enumerate(tooltips):
                psr.add_tooltip(tt_labels[i], tt)

        if named_tooltips is not None:
            for name, tt in named_tooltips.items():
                psr.add_tooltip(tt_labels[name], tt)

    def newpage(self) -> None:
        self.history.insert(0, NewPageCmd())
        t = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        psdisplay(HTML(f'<div class="divider">{t}</div>'), target="story")

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
                <input id="troubadour_inputtext_input_{id}" class="input" type="text" placeholder="{placeholder_text}">
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
    encoded_state = psr.local_storage["state"]
    if encoded_state is not None:
        state = jsp.decode(encoded_state)
        assert isinstance(state, GameState)
        return state
    else:
        return None


def get_saves() -> Optional[GameSaves]:
    encoded_saves = psr.local_storage["saves"]
    if encoded_saves is not None:
        saves = jsp.decode(encoded_saves)
        assert isinstance(saves, GameSaves)
        return saves
    else:
        return None


def render_interface(game: AbstractGame, interface: list[AbstractInterface]) -> None:
    for element in interface:
        match element:
            case Button(text, _method, tooltip):  # type:ignore
                add_button(
                    text,
                    lambda _, _method=_method: run_page(game, _method),
                    tooltip,
                )
            case TextInput(  # type:ignore
                button_text=button_text,
                method=method,
                default_value=default_value,
                placeholder_text=placeholder_text,
            ):
                add_text_input(
                    lambda v, _method=method: run_page(game, _method, msg=v),
                    button_text,
                    default_value,
                    placeholder_text,
                )
            case _:
                raise NotImplementedError()


def run_page(game: AbstractGame, method: str, **args: Any) -> None:
    interface = getattr(game, method)(**args)
    render_panels(game.info, game.extra)
    render_porthole(game.porthole)
    psr.clear("story-interface")
    render_interface(game, interface)
    psr.local_storage["state"] = GameState(game, interface, LIGHT_MODE)


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


def run_game(game: AbstractGame) -> None:
    # saves
    match get_saves():
        case None:
            psr.local_storage["saves"] = GameSaves()
        case GameSaves() as saves:
            saves.render()

    psr.onclick("load-button", lambda _: psr.activate_modal("load-modal"))
    psr.onclick("load-modal-cancel", lambda _: psr.deactivate_modal("load-modal"))
    psr.onclick("save-button", lambda _: psr.activate_modal("save-modal"))
    psr.onclick("save-modal-save", lambda _: save_game())
    psr.onclick("save-modal-cancel", lambda _: psr.deactivate_modal("save-modal"))

    # dark mode
    psr.onclick("dark-mode-toggle", toggle_mode)

    # resume modal
    def restart(_: Any) -> None:
        run_page(game, "start")
        close_resume_modal(None)

    psr.onclick("resume-modal-restart", restart)
    psr.onclick("resume-modal-load", load_cache_data)

    # restart button
    def restart2(_: Any, new_game: AbstractGame = deepcopy(game)) -> None:
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

    # start game
    match get_state():
        case None:
            run_page(game, "start")
        case GameState(color_mode=color_mode):
            if color_mode == "dark":
                toggle_mode(None)
            psr.activate_modal("resume-modal")


LIGHT_MODE = "light"


def toggle_mode(_: Any) -> None:
    global LIGHT_MODE
    if LIGHT_MODE == "dark":
        psr.disable("dark-style")
        psr.enable("light-style")
        psr.remove_class("story-container", "dark-mode")
        LIGHT_MODE = "light"
        psr.remove_class("dark-mode-icon", "fa-sun")
        psr.add_class("dark-mode-icon", "fa-moon")
    elif LIGHT_MODE == "light":
        psr.enable("dark-style")
        psr.disable("light-style")
        psr.add_class("story-container", "dark-mode")
        LIGHT_MODE = "dark"
        psr.remove_class("dark-mode-icon", "fa-moon")
        psr.add_class("dark-mode-icon", "fa-sun")
    state = get_state()
    assert state is not None
    state.color_mode = LIGHT_MODE
    psr.local_storage["state"] = state


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

    psr.clear("story-interface")
    render_interface(state.game, state.interface)

    close_resume_modal(None)


if __name__ == "__main__":
    s = Story()
    i = InfoPanel()
