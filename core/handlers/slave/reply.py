from tornado.gen import coroutine

from core.bot import CommandFilterTextRegexp, CommandFilterTextAny
from core.slave_command_filters import CommandFilterIsModerationChat
from helpers import pgettext, report_botan
from telegram import ForceReply


@coroutine
@CommandFilterIsModerationChat()
@CommandFilterTextRegexp(r'/reply_(?P<chat_id>\d+)_(?P<message_id>\d+)')
def reply_command(bot, message, chat_id, message_id):
    report_botan(message, 'slave_reply_cmd')
    yield bot.send_message(pgettext('Reply message request', 'What message should I send to user?'),
                           reply_to_message=message, reply_markup=ForceReply(True))
    return {
        'chat_id': chat_id,
        'message_id': message_id,
    }


@coroutine
@CommandFilterTextAny()
def plaintext_reply_handler(bot, message, chat_id, message_id):
    msg = message['text'].strip()
    if len(msg) < 10:
        report_botan(message, 'slave_reply_short_msg')
        yield bot.send_message(pgettext('Reply message is too short', 'Message is too short (10 symbols required), try '
                                                                      'again or send /cancel'),
                               reply_to_message=message, reply_markup=ForceReply(True))
    else:
        try:
            yield bot.send_message(msg, chat_id=chat_id, reply_to_message_id=message_id)
            yield bot.send_message(pgettext('Reply delivery confirmation', 'Message sent'), reply_to_message=message)
        except Exception as e:
            yield bot.send_message(pgettext('Reply failed', 'Failed: {reason}').format(reason=str(e)),
                                   reply_to_message=message)

        return True