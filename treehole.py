"""treehole bot"""
import base64
import datetime
import json
import logging

import requests
from mixinsdk.clients.blaze_client import BlazeClient
from mixinsdk.clients.http_client import HttpClient_AppAuth
from mixinsdk.clients.user_config import AppConfig
from mixinsdk.types.message import (
    MessageView,
    pack_contact_data,
    pack_message,
    pack_text_data,
)
from mixinsdk.utils import parse_rfc3339_to_datetime
from quorum_data_py import feed
from quorum_mininode_py import MiniNode

from config_private import *

__version__ = "0.1.1"
logger = logging.getLogger(__name__)
logger.info("treehole bot version: %s", __version__)


class TreeHoleBot:
    """init"""

    def __init__(self, mixin_keystore, rum_seedurl, pvtkey):
        self.config = AppConfig.from_payload(mixin_keystore)
        if PRIVATE_KEY_TYPE == "SAME":
            self.rum = MiniNode(rum_seedurl, pvtkey)
        else:
            self.rum = MiniNode(rum_seedurl)
        self.xin = HttpClient_AppAuth(self.config, api_base=HTTP_ZEROMESH)


def message_handle_error_callback(error, details):
    """message_handle_error_callback"""
    logger.error("===== error_callback =====")
    logger.error("error: %s", error)
    logger.error("details: %s", details)


async def message_handle(message):
    """message_handle"""
    global bot
    action = message["action"]

    if action == "ERROR":
        logger.warning(message["error"])

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
    if not (data and isinstance(data, str)):
        await bot.blaze.echo(msg_id)
        return

    category = msg_data.get("category")
    if category not in ["PLAIN_TEXT", "PLAIN_IMAGE"]:
        await bot.blaze.echo(msg_id)
        return

    to_send_data = {}
    reply_text = ""
    reply_msgs = []
    is_echo = True

    if category == "PLAIN_TEXT":
        text = MessageView.from_dict(msg_data).data_decoded
        _text_length = f"文本长度需在 {TEXT_LENGTH_MIN} 至 {TEXT_LENGTH_MAX} 之间"
        if text.lower() in ["hi", "hello", "nihao", "你好", "help", "?", "？"]:
            reply_text = WELCOME_TEXT
        elif len(text) <= TEXT_LENGTH_MIN:
            reply_text = f"消息太短，无法处理。{_text_length}"
        elif len(text) >= TEXT_LENGTH_MAX:
            reply_text = f"消息太长，无法处理。{_text_length}"
        else:
            to_send_data = {"content": "#树洞# " + text}
    elif category == "PLAIN_IMAGE":
        try:
            _bytes = base64.b64decode(data)
            attachment_id = json.loads(_bytes).get("attachment_id")
            attachment = bot.xin.api.message.read_attachment(attachment_id)
            view_url = attachment["data"]["view_url"]
            content = requests.get(view_url).content  # 图片 content
            to_send_data = {"content": "#树洞# ", "images": [content]}
        except Exception as err:
            to_send_data = None
            is_echo = False
            logger.warning(err)

    if to_send_data:
        try:
            post = feed.new_post(**to_send_data)
            resp = bot.rum.api.post_content(post)
            if "trx_id" in resp:
                print(datetime.datetime.now(), resp["trx_id"], "sent_to_rum done.")
                reply_text = f"树洞已生成 trx {resp['trx_id']}，您可通过 RUM 微博广场 或网页 https://feed.base.one/groups/82f1e717-92d4-42d5-98cc-2457793d5f14 查看已上链成功的信息。"
                reply_msgs.append(
                    pack_message(pack_contact_data(RSS_MIXIN_ID), msg_cid)
                )
            else:
                is_echo = False
        except Exception as err:
            is_echo = False
            logger.warning(err)

    if reply_text:
        reply_msg = pack_message(
            pack_text_data(reply_text),
            conversation_id=msg_cid,
            quote_message_id=msg_id,
        )
        reply_msgs.insert(0, reply_msg)

    if reply_msgs:
        for msg in reply_msgs:
            bot.xin.api.send_messages(msg)

    if is_echo:
        await bot.blaze.echo(msg_id)
    return


bot = TreeHoleBot(MIXIN_BOT_KEYSTORE, RUM_SEED_URL, SAME_PVTKEY)
bot.blaze = BlazeClient(
    bot.config,
    on_message=message_handle,
    on_message_error_callback=message_handle_error_callback,
    api_base=BLAZE_ZEROMESH,
)
bot.blaze.run_forever(2)
