import datetime
import json
import logging

import requests
from mixinsdk.clients.blaze_client import BlazeClient
from mixinsdk.clients.http_client import HttpClient_AppAuth
from mixinsdk.clients.user_config import AppConfig
from mixinsdk.types.message import MessageView, pack_contact_data, pack_message, pack_text_data
from mixinsdk.utils import parse_rfc3339_to_datetime
from rumpy import MiniNode
from rumpy.utils import get_filebytes

from config import *

logger = logging.getLogger(__name__)


class TreeHoleBot:
    def __init__(self, mixin_keystore, rum_seedurl):
        self.config = AppConfig.from_payload(mixin_keystore)
        self.rum = MiniNode(rum_seedurl)


def message_handle_error_callback(error, details):
    logger.error("===== error_callback =====")
    logger.error(f"error: {error}")
    logger.error(f"details: {details}")


async def message_handle(message):
    global bot
    action = message["action"]

    # messages sent by bot
    if action == "ACKNOWLEDGE_MESSAGE_RECEIPT":
        # logger.info("Mixin blaze server: received the message")
        return

    if action == "LIST_PENDING_MESSAGES":
        # logger.info("Mixin blaze server: list pending message")
        return

    if action == "ERROR":
        logger.warning(message["error"])
        return

    if action != "CREATE_MESSAGE":
        return

    error = message.get("error")
    if error:
        logger.info(str(error))
        return

    msg_data = message.get("data", {})

    msg_id = msg_data.get("message_id")
    if not msg_id:
        await bot.blaze.echo(msg_id)
        return

    msg_type = msg_data.get("type")
    if msg_type != "message":
        await bot.blaze.echo(msg_id)
        return

    # 和 server 有 -8 时差。-9 也就是只处理 1 小时内的 message
    create_at = parse_rfc3339_to_datetime(msg_data.get("created_at"))
    blaze_for_hour = datetime.datetime.now() + datetime.timedelta(hours=-9)
    if create_at <= blaze_for_hour:
        await bot.blaze.echo(msg_id)
        return

    msg_cid = msg_data.get("conversation_id")
    if not msg_cid:
        await bot.blaze.echo(msg_id)
        return

    data = msg_data.get("data")
    if not (data and type(data) == str):
        await bot.blaze.echo(msg_id)
        return

    category = msg_data.get("category")
    to_send_data = None
    reply_text = ""
    reply_msgs = []

    if category not in ["PLAIN_TEXT", "PLAIN_IMAGE"]:
        reply_text = f"暂时不支持此类消息，如有需求，请联系开发者\ncategory: {category}"
        reply_msgs.append(pack_message(pack_contact_data(DEV_MIXIN_ID), msg_cid))
    elif category == "PLAIN_TEXT":
        msgview = MessageView.from_dict(msg_data)
        if len(msgview.data_decoded) <= 10:
            reply_text = WELCOME_TEXT
            reply_msgs.append(pack_message(pack_contact_data(RSS_MIXIN_ID), msg_cid))
        elif len(msgview.data_decoded) >= 500:
            reply_text = "消息太长，无法处理。请输入低于 500 个字符长度的文本。"
        else:
            to_send_data = {"content": "#树洞# " + msgview.data_decoded}
    elif category == "PLAIN_IMAGE":
        try:
            _bytes, _ = get_filebytes(data)
            attachment_id = json.loads(_bytes).get("attachment_id")
            attachment = bot.xin.api.message.read_attachment(attachment_id)
            view_url = attachment["data"]["view_url"]
            content = requests.get(view_url).content  # 图片 content
            to_send_data = {"content": "#树洞# ", "images": [{"content": content}]}
        except Exception as e:
            to_send_data = None
            reply_text = "Mixin 服务目前不稳定，请稍后再试，或联系开发者\n" + str(e)
            reply_msgs.append(pack_message(pack_contact_data(DEV_MIXIN_ID), msg_cid))

    if to_send_data:
        if PRIVATE_KEY_TYPE == "SAME":
            pvtkey = SAME_PVTKEY  # config.py
        else:  # DIFF
            pvtkey = bot.rum.create_private_key()
        try:
            r = bot.rum.send_note(pvtkey, **to_send_data)
            if "trx_id" in r:
                print(datetime.datetime.now(), r["trx_id"], "sent_to_rum done.")
                reply_text = f"树洞已发布到 RUM 种子网络 {GROUP_NAME}\ntrx_id <{r['trx_id']}>"
            else:
                reply_text = f"树洞发送到 RUM 种子网络时出错，请稍后再试，或联系开发者\n\n{r}"
                reply_msgs.append(pack_message(pack_contact_data(DEV_MIXIN_ID), msg_cid))
        except Exception as e:
            reply_text = f"树洞发送到 RUM 种子网络时出错，请稍后再试，或联系开发者\n\n{e}"
            reply_msgs.append(pack_message(pack_contact_data(DEV_MIXIN_ID), msg_cid))

    if reply_text:
        reply_msg = pack_message(
            pack_text_data(reply_text),
            conversation_id=msg_cid,
            quote_message_id=msg_id,
        )
        reply_msgs.insert(0, reply_msg)

    if reply_msgs:
        for msg in reply_msgs:
            resp = bot.xin.api.send_messages(msg)

    await bot.blaze.echo(msg_id)
    return


bot = TreeHoleBot(MIXIN_BOT_KEYSTORE, RUM_SEED_URL)
bot.xin = HttpClient_AppAuth(bot.config, api_base=HTTP_ZEROMESH)
bot.blaze = BlazeClient(
    bot.config,
    on_message=message_handle,
    on_message_error_callback=message_handle_error_callback,
    api_base=BLAZE_ZEROMESH,
)
bot.blaze.run_forever(2)
