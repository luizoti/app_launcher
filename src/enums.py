
actions_map: dict[int, str] = {
    1: "up",
    2: "down",
    3: "left",
    4: "right",
    5: "enter",
    6: "options",
    7: "toggle_view",
    8: "close",
}

actions_map_reversed: dict[str, int] = {y: x for x, y in actions_map.items()}
