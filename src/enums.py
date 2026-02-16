import typing


actions_map: typing.Dict[int, typing.Text] = {
    1: "up",
    2: "down",
    3: "left",
    4: "right",
    5: "enter",
    6: "options",
    7: "toggle_view",
    8: "close",
}

actions_map_reversed: typing.Dict[typing.Text, int] = {y: x for x, y in actions_map.items()}
