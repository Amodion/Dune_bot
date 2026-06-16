from __future__ import annotations

from dataclasses import dataclass

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from app.services.dice_service import RollParams, roll

NO_DIFFICULTY = "-"


@dataclass(frozen=True)
class WizardState:
    treshold: int = 14
    n_dices: int = 2
    crit_value: int = 1
    difficulty: int | None = None
    complications_range: int = 20
    use_determination: bool = False

    @classmethod
    def from_callback_data(cls, data: str) -> "WizardState":
        parts = data.split(":")
        if len(parts) != 7 or parts[0] != "r":
            return cls()
        difficulty = None if parts[4] == NO_DIFFICULTY else int(parts[4])
        return cls(
            treshold=int(parts[1]),
            n_dices=int(parts[2]),
            crit_value=int(parts[3]),
            difficulty=difficulty,
            complications_range=int(parts[5]),
            use_determination=parts[6] == "1",
        )

    def to_callback_data(self) -> str:
        difficulty = NO_DIFFICULTY if self.difficulty is None else str(self.difficulty)
        determination = "1" if self.use_determination else "0"
        return f"r:{self.treshold}:{self.n_dices}:{self.crit_value}:{difficulty}:{self.complications_range}:{determination}"

    def with_delta(self, field: str, delta: int) -> "WizardState":
        values = self.__dict__.copy()
        current = values[field]
        if current is None:
            current = 0
        values[field] = int(current) + delta
        return WizardState(**values)

    def toggle_determination(self) -> "WizardState":
        return WizardState(
            treshold=self.treshold,
            n_dices=self.n_dices,
            crit_value=self.crit_value,
            difficulty=self.difficulty,
            complications_range=self.complications_range,
            use_determination=not self.use_determination,
        )

    def toggle_difficulty(self) -> "WizardState":
        return WizardState(
            treshold=self.treshold,
            n_dices=self.n_dices,
            crit_value=self.crit_value,
            difficulty=1 if self.difficulty is None else None,
            complications_range=self.complications_range,
            use_determination=self.use_determination,
        )

    def to_roll_params(self) -> RollParams:
        return RollParams(
            treshold=self.treshold,
            n_dices=self.n_dices,
            crit_value=self.crit_value,
            difficulty=self.difficulty,
            complications_range=self.complications_range,
            use_determination=self.use_determination,
        )


def render_wizard_text(state: WizardState) -> str:
    difficulty = "нет" if state.difficulty is None else str(state.difficulty)
    determination = "да" if state.use_determination else "нет"
    return (
        "*Настрой бросок:*\n"
        f"Порог: {state.treshold}\n"
        f"Кубики: {state.n_dices}\n"
        f"Криты на: {state.crit_value}\n"
        f"Сложность: {difficulty}\n"
        f"Затруднения на: {state.complications_range}\n"
        f"Решимость: {determination}"
    )


def _button(label: str, action: str, state: WizardState) -> InlineKeyboardButton:
    return InlineKeyboardButton(label, callback_data=f"{action}|{state.to_callback_data()}")


def build_roll_keyboard(state: WizardState) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_button("Порог -", "t-", state), _button(f"Порог {state.treshold}", "noop", state), _button("Порог +", "t+", state)],
            [_button("Кубики -", "n-", state), _button(f"Кубики {state.n_dices}", "noop", state), _button("Кубики +", "n+", state)],
            [_button("Крит -", "c-", state), _button(f"Крит {state.crit_value}", "noop", state), _button("Крит +", "c+", state)],
            [
                _button("Сложн. вкл/выкл", "dt", state),
                _button(f"Сложн. {'-' if state.difficulty is None else state.difficulty}", "noop", state),
            ],
            [_button("Сложн. -", "d-", state), _button("Сложн. +", "d+", state)],
            [_button("Затр. -", "r-", state), _button(f"Затр. {state.complications_range}", "noop", state), _button("Затр. +", "r+", state)],
            [_button(f"Решимость: {'да' if state.use_determination else 'нет'}", "det", state)],
            [_button("Бросить", "roll", state)],
        ]
    )


def apply_action(action: str, state: WizardState) -> WizardState:
    match action:
        case "t-":
            return state.with_delta("treshold", -1)
        case "t+":
            return state.with_delta("treshold", 1)
        case "n-":
            return state.with_delta("n_dices", -1)
        case "n+":
            return state.with_delta("n_dices", 1)
        case "c-":
            return state.with_delta("crit_value", -1)
        case "c+":
            return state.with_delta("crit_value", 1)
        case "dt":
            return state.toggle_difficulty()
        case "d-":
            if state.difficulty is None:
                return state
            return state.with_delta("difficulty", -1)
        case "d+":
            if state.difficulty is None:
                return state
            return state.with_delta("difficulty", 1)
        case "r-":
            return state.with_delta("complications_range", -1)
        case "r+":
            return state.with_delta("complications_range", 1)
        case "det":
            return state.toggle_determination()
        case _:
            return state


def roll_wizard_state(state: WizardState) -> str:
    params = state.to_roll_params()
    return roll(
        treshold=params.treshold,
        n_dices=params.n_dices,
        crit_value=params.crit_value,
        difficulty=params.difficulty,
        complications_range=params.complications_range,
        use_determination=params.use_determination,
    )

