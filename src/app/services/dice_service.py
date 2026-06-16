from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class RollParams:
    treshold: int
    n_dices: int = 2
    crit_value: int = 1
    difficulty: int | None = None
    complications_range: int = 20
    use_determination: bool = False


def parse_args(*args: str) -> dict[str, int | bool]:
    """
    Preserve the legacy syntax:
    /roll treshold cX nY dZ rV !
    """
    d: dict[str, int | bool] = {"treshold": int(args[0])}
    for arg in args[1:]:
        if "c" in arg:
            d["crit_value"] = int(arg[1:])
        if "n" in arg:
            d["n_dices"] = int(arg[1:])
        if "d" in arg:
            d["difficulty"] = max(0, int(arg[1:]))
        if "r" in arg:
            d["complications_range"] = int(arg[1:])
        if "!" in arg:
            d["use_determination"] = True
    return d


def params_from_args(*args: str) -> RollParams:
    parsed = parse_args(*args)
    return RollParams(**parsed)


def description_from_args(*args: str) -> str:
    d = parse_args(*args)

    description = f'Порог успеха: {d["treshold"]}; '
    if "crit_value" in d:
        description += f'Криты на: {d["crit_value"]}; '
    else:
        description += "c - криты; "

    if "n_dices" in d:
        description += f'Число кубиков: {d["n_dices"]}; '
    else:
        description += "n - число кубиков; "

    if "difficulty" in d:
        description += f'Сложность: {d["difficulty"]}; '
    else:
        description += "d - Сложность; "

    if "complications_range" in d:
        description += f'Затруднения на: {d["complications_range"]}; '
    else:
        description += "r - затруднения; "

    if "use_determination" in d:
        description += "Потрачена Решимость"
    else:
        description += "! - Решимость"

    return description


def roll_from_args(*args: str) -> str:
    return roll(**parse_args(*args))


def roll(
    treshold: int,
    n_dices: int = 2,
    crit_value: int = 1,
    difficulty: int | None = None,
    complications_range: int = 20,
    use_determination: bool = False,
    randint: Callable[[int, int], int] | None = None,
) -> str:
    random_int = randint or random.randint
    if use_determination:
        rolls = [1] + [random_int(1, 20) for _ in range(n_dices - 1)]
    else:
        rolls = [random_int(1, 20) for _ in range(n_dices)]

    successes = 0
    complications = 0
    for result in rolls:
        if result <= crit_value:
            successes += 2
        elif result <= treshold:
            successes += 1

        if result >= complications_range:
            complications += 1

    result = f"*Успехов: {successes}!*"
    if type(difficulty) is int:
        if successes >= difficulty:
            result += "\n*ПРОЙДЕНО!*"
            momentum = successes - difficulty
            if momentum:
                result += f"\nСоздано Очков Импульса: {momentum}"
        else:
            result += "\n*ПРОВАЛ!*"
            if difficulty >= 3:
                result += "\nПолучи 1 Очко Развития!"
    if complications:
        result += f"\nПолучено затруднений: {complications}"

    result += f"\n\nПорог: {treshold}, Криты на: {crit_value}"
    if type(difficulty) is int:
        result += f", Сложность: {difficulty}"
    result += f"\nБросок: [{rolls}]"
    return result

