from __future__ import annotations

from app.services.keyboard_service import WizardState, apply_action, build_roll_keyboard, owner_from_callback_data, state_from_callback_payload


def test_wizard_state_round_trip() -> None:
    state = WizardState(treshold=15, n_dices=4, crit_value=6, difficulty=3, complications_range=18, use_determination=True)
    assert WizardState.from_callback_data(state.to_callback_data()) == state


def test_apply_action_changes_stateless_state() -> None:
    state = apply_action("t+", WizardState())
    state = apply_action("det", state)
    assert state.treshold == 15
    assert state.use_determination is True


def test_keyboard_callback_data_includes_owner_and_state() -> None:
    state = WizardState(treshold=15, n_dices=4, crit_value=6, difficulty=3, complications_range=18, use_determination=True)
    keyboard = build_roll_keyboard(state, owner_user_id=123456)
    callback_data = keyboard.inline_keyboard[0][0].callback_data

    assert callback_data is not None
    assert owner_from_callback_data(callback_data) == 123456
    assert state_from_callback_payload(callback_data) == state
    assert len(callback_data) <= 64
