from __future__ import annotations

from app.services.dice_service import description_from_args, parse_args, roll


def sequence(values: list[int]):
    iterator = iter(values)
    return lambda _start, _end: next(iterator)


def test_parse_args_preserves_legacy_flags() -> None:
    assert parse_args("15", "n4", "c6", "d3", "r18", "!") == {
        "treshold": 15,
        "n_dices": 4,
        "crit_value": 6,
        "difficulty": 3,
        "complications_range": 18,
        "use_determination": True,
    }


def test_roll_success_with_difficulty_and_momentum() -> None:
    result = roll(15, n_dices=4, crit_value=6, difficulty=3, complications_range=18, use_determination=True, randint=sequence([10, 15, 5]))
    assert result == (
        "*Успехов: 6!*\n"
        "*ПРОЙДЕНО!*\n"
        "Создано Очков Импульса: 3\n\n"
        "Порог: 15, Криты на: 6, Сложность: 3\n"
        "Бросок: [[1, 10, 15, 5]]"
    )


def test_roll_failure_and_complication() -> None:
    result = roll(8, n_dices=2, crit_value=1, difficulty=3, complications_range=20, randint=sequence([19, 20]))
    assert result == (
        "*Успехов: 0!*\n"
        "*ПРОВАЛ!*\n"
        "Получи 1 Очко Развития!\n"
        "Получено затруднений: 1\n\n"
        "Порог: 8, Криты на: 1, Сложность: 3\n"
        "Бросок: [[19, 20]]"
    )


def test_description_from_args_preserves_legacy_text() -> None:
    assert description_from_args("14", "c5") == (
        "Порог успеха: 14; Криты на: 5; n - число кубиков; d - Сложность; r - затруднения; ! - Решимость"
    )

