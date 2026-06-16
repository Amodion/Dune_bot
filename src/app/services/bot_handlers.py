from __future__ import annotations

import logging

from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.constants import ParseMode
from telegram.ext import CallbackContext, ContextTypes

from app.services.dice_service import description_from_args, roll_from_args
from app.services.keyboard_service import (
    WizardState,
    apply_action,
    build_roll_keyboard,
    render_wizard_text,
    roll_wizard_state,
)
from app.utils.paths import read_static_text

logger = logging.getLogger(__name__)


def get_help_text() -> str:
    return read_static_text("help.md")


async def start_or_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_message is None:
        return
    await update.effective_message.reply_text(get_help_text(), parse_mode=ParseMode.MARKDOWN)


async def roll_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_message is None:
        return
    args = context.args
    if args:
        try:
            result = roll_from_args(*args)
        except (IndexError, ValueError) as exc:
            logger.info("Invalid roll command: %s", exc)
            await update.effective_message.reply_text("Не получилось разобрать бросок. Напиши /help для синтаксиса.")
            return
        await update.effective_message.reply_text(result, parse_mode=ParseMode.MARKDOWN)
        return

    state = WizardState()
    await update.effective_message.reply_text(
        render_wizard_text(state),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=build_roll_keyboard(state),
    )


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query
    if query is None:
        return

    text = query.query.strip()
    if not text:
        return

    if text.lower() == "help":
        result = InlineQueryResultArticle(
            id="help",
            title="Help",
            input_message_content=InputTextMessageContent(get_help_text(), parse_mode=ParseMode.MARKDOWN),
            description="Get help",
        )
        await query.answer([result], cache_time=0)
        return

    if not text[0].isdigit():
        return

    try:
        args = text.split()
        result_text = roll_from_args(*args)
        description = description_from_args(*args)
    except (IndexError, ValueError) as exc:
        logger.info("Invalid inline roll query: %s", exc)
        return

    result = InlineQueryResultArticle(
        id="roll",
        title="Roll",
        input_message_content=InputTextMessageContent(result_text, parse_mode=ParseMode.MARKDOWN),
        description=description,
    )
    await query.answer([result], cache_time=0)


async def roll_keyboard_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if query is None or query.data is None:
        return

    await query.answer()
    action, _, state_data = query.data.partition("|")
    state = WizardState.from_callback_data(state_data)

    if action == "roll":
        await query.edit_message_text(roll_wizard_state(state), parse_mode=ParseMode.MARKDOWN)
        return

    new_state = apply_action(action, state)
    await query.edit_message_text(
        render_wizard_text(new_state),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=build_roll_keyboard(new_state),
    )

