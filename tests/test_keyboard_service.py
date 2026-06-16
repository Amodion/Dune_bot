from __future__ import annotations

from app.services.keyboard_service import WizardState, apply_action


def test_wizard_state_round_trip() -> None:
    state = WizardState(treshold=15, n_dices=4, crit_value=6, difficulty=3, complications_range=18, use_determination=True)
    assert WizardState.from_callback_data(state.to_callback_data()) == state


def test_apply_action_changes_stateless_state() -> None:
    state = apply_action("t+", WizardState())
    state = apply_action("det", state)
    assert state.treshold == 15
    assert state.use_determination is True

