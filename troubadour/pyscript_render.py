from typing import Any, Callable, Optional, TypeVar, Generic, Type, overload

import jsonpickle as jsp
from pyodide.code import run_js  # type: ignore
from pyodide.ffi import create_proxy  # type: ignore
from pyscript import HTML  # type: ignore
from pyscript import Element  # type: ignore
from pyscript import js  # type: ignore
from pyscript import display as psdisplay  # type: ignore


def onclick(id: str, func: Callable[[Any], None]) -> None:
    Element(id).element.addEventListener("click", create_proxy(func))


def insert_end(id: str, html: str) -> None:
    Element(id).element.insertAdjacentHTML("beforeend", html)


def set_html(id: str, html: str) -> None:
    Element(id).element.innerHTML = html


def clear(id: str) -> None:
    set_html(id, "")


def click(id: str) -> None:
    Element(id).element.click()


def set_src(id: str, value: str) -> None:
    Element(id).element.src = value


def set_alt(id: str, value: str) -> None:
    Element(id).element.alt = value


def get_value(id: str) -> str:
    return Element(id).element.value


def add_tooltip(id: str, text: str) -> None:
    run_js(
        f"""tippy("#{id}",
                {{
                    content:"{text}",
                    allowHTML:true,
                }}
            );"""
    )


def add_class(id: str, cls: str) -> None:
    Element(id).add_class(cls)


def remove_class(id: str, cls: str) -> None:
    Element(id).remove_class(cls)


def activate_modal(id: str) -> None:
    add_class(id, "is-active")


def deactivate_modal(id: str) -> None:
    remove_class(id, "is-active")


def disable(id: str) -> None:
    Element(id).element.disabled = "disabled"


def enable(id: str) -> None:
    Element(id).element.disabled = None


T = TypeVar("T")


class LocalStorage:
    def __getitem__(self, key: str) -> Optional[str]:
        return js.localStorage.getItem(key)

    def __setitem__(self, key: str, value: Any) -> None:
        js.localStorage.setItem(key, jsp.encode(value))

    def __call__(self, cls: Type[T]) -> "TypedLocalStorage[T]":
        return TypedLocalStorage(cls)


class TypedLocalStorage(Generic[T]):
    def __init__(self, cls: Type[T]) -> None:
        self.cls = cls

    def __getitem__(self, key: str) -> Optional[T]:
        result = js.localStorage.getItem(key)
        if result is not None:
            decoded_result = jsp.decode(result)
            assert isinstance(decoded_result, self.cls)
            return decoded_result
        else:
            return None


local_storage = LocalStorage()


def file_download_button(id: str, content: str, filename: str) -> None:
    run_js(
        f"""
const blob = new Blob(
    [`{content.encode("unicode_escape").decode("utf-8")}`], {{type: 'text/json'}});
const button = document.getElementById("{id}");
button.href = URL.createObjectURL(blob);
button.download = "{filename}";
        """
    )
    # FIXME revoke url


def display_story(text: str) -> None:
    psdisplay(HTML(text), target="story")


@overload
def on_file_upload(id: str, callback: Callable[[str], None], cls: None = None) -> None:
    pass


@overload
def on_file_upload(id: str, callback: Callable[[T], None], cls: Type[T]) -> None:
    pass


def on_file_upload(
    id: str,
    callback: Callable[[str], None] | Callable[[T], None],
    cls: Optional[Type[T]] = None,
) -> None:
    async def event_handler(event: Any, cb: Callable = callback) -> None:
        file_list = event.target.files.to_py()
        for f in file_list:
            raw = await f.text()
            if cls is None:
                cb(raw)
            else:
                decoded = jsp.decode(raw)
                assert isinstance(decoded, cls)
                cb(decoded)
        Element(id).element.value = ""

    Element(id).element.addEventListener("change", create_proxy(event_handler))
