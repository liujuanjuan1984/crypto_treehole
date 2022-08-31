"""treehole bot"""
import datetime
import json
import logging

import requests
from mininode import MiniNode
from mininode.crypto import create_private_key
from mininode.utils import decode_seed_url, get_filebytes
from mixinsdk.clients.blaze_client import BlazeClient
from mixinsdk.clients.http_client import HttpClient_AppAuth
from mixinsdk.clients.user_config import AppConfig
from mixinsdk.types.message import MessageView, pack_contact_data, pack_message, pack_text_data
from mixinsdk.utils import parse_rfc3339_to_datetime

import config_private as PVT

logger = logging.getLogger(__name__)


HTTP_ZEROMESH = "https://mixin-api.zeromesh.net"
BLAZE_ZEROMESH = "wss://mixin-blaze.zeromesh.net"

DEV_MIXIN_ID = PVT.DEV_MIXIN_ID
RSS_MIXIN_ID = PVT.RSS_MIXIN_ID
MIXIN_BOT_KEYSTORE = PVT.MIXIN_BOT_KEYSTORE

PRIVATE_KEY_TYPE = PVT.PRIVATE_KEY_TYPE
SAME_PVTKEY = PVT.SAME_PVTKEY
RUM_SEED_URL = PVT.RUM_SEED_URL
GROUP_NAME = decode_seed_url(RUM_SEED_URL)["group_name"]

WELCOME_TEXT = f"""👋 你好，我是 TreeHole 机器人。

向我发送图片，或文本（长度不低于 10 ，不超出 500）；
我将以密钥签名，把该图片或文本以“树洞”的形式发送到 RUM 种子网络{GROUP_NAME}。

我不存储任何数据，请放心享受真正匿名的“树洞”吧。

想要查阅已发布的树洞或互动？
请通过 Rum 应用加入种子网络 {GROUP_NAME} 或在 Mixin 上使用 RUM种子网络订阅器 bot：
"""


class TreeHoleBot:
    """init"""

    def __init__(self, mixin_keystore, rum_seedurl):
        self.config = AppConfig.from_payload(mixin_keystore)
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

    # messages sent by bot
    if action == "ACKNOWLEDGE_MESSAGE_RECEIPT":
        logger.info("Mixin blaze server: received the message")

    if action == "LIST_PENDING_MESSAGES":
        logger.info("Mixin blaze server: list pending message")

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
            to_send_data = {"content": "#树洞# ", "images": [content]}
        except Exception as err:
            to_send_data = None
            reply_text = "Mixin 服务目前不稳定，请稍后再试，或联系开发者\n" + str(err)
            reply_msgs.append(pack_message(pack_contact_data(DEV_MIXIN_ID), msg_cid))
            logger.warning(err)

    if to_send_data:
        if PRIVATE_KEY_TYPE == "SAME":
            pvtkey = SAME_PVTKEY
        else:
            pvtkey = create_private_key()
        try:
            resp = bot.rum.api.send_content(pvtkey, **to_send_data)
            if "trx_id" in resp:
                print(datetime.datetime.now(), resp["trx_id"], "sent_to_rum done.")
                reply_text = f"树洞已发布到 RUM 种子网络 {GROUP_NAME}\ntrx_id <{resp['trx_id']}>"
            else:
                reply_text = f"树洞发送到 RUM 种子网络时出错，请稍后再试，或联系开发者\n\n{resp}"
                reply_msgs.append(pack_message(pack_contact_data(DEV_MIXIN_ID), msg_cid))
        except Exception as err:
            reply_text = f"树洞发送到 RUM 种子网络时出错，请稍后再试，或联系开发者\n\n{err}"
            reply_msgs.append(pack_message(pack_contact_data(DEV_MIXIN_ID), msg_cid))
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

    await bot.blaze.echo(msg_id)
    return


bot = TreeHoleBot(MIXIN_BOT_KEYSTORE, RUM_SEED_URL)
bot.blaze = BlazeClient(
    bot.config,
    on_message=message_handle,
    on_message_error_callback=message_handle_error_callback,
    api_base=BLAZE_ZEROMESH,
)
bot.blaze.run_forever(2)
