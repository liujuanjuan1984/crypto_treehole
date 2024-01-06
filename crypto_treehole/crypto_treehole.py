"""treehole bot"""

import base64
import datetime
import json
import logging

import requests
from mixinsdk.clients.client_blaze import BlazeClient
from mixinsdk.clients.client_http import HttpClient_WithAppConfig
from mixinsdk.clients.config import AppConfig
from mixinsdk.types.message import pack_message, pack_text_data
from mixinsdk.utils import parse_rfc3339_to_datetime
from quorum_data_py import feed
from quorum_mininode_py import MiniNode

logging.basicConfig(
    level=logging.WARNING, format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger("treehole")


TEXT_LENGTH_MIN = 10
TEXT_LENGTH_MAX = 500
HTTP_ZEROMESH = "https://mixin-api.zeromesh.net"
BLAZE_ZEROMESH = "wss://mixin-blaze.zeromesh.net"


def init_welcome_text(
    private_key_type: str, text_length_min: int, text_length_max: int, rss_mixin_id: int
):
    private_key_text = (
        "随机账号模式，每条树洞随机生成一对新密钥。"
        if private_key_type != "SAME"
        else "相同账号模式，任何人的所有树洞采用同一对密钥。"
    )
    welcome_text = f"""👋 hi, I am TreeHole bot\n\n采用 {private_key_text}\n\n向我发送图片或文本（长度不低于 {text_length_min} ，不超出 {text_length_max}）；\n我将以密钥签名，把该图片或文本以“树洞”的形式发送到 RUM 种子网络。\n\n我不存储任何数据，请放心享受真正匿名的“树洞”吧。\n\n想要查阅已发布的树洞或互动？\n访问网页 https://feed.base.one/ 或在 Mixin 上使用 bot：@{rss_mixin_id}\n"""
    return welcome_text


def init_reply_text(trx_id, rss_mixin_id, private_key_type):
    reply_text = f"树洞已发布到链上 trx {trx_id}，您可通过 RUM 微博广场 @{rss_mixin_id} 或查看网页 https://feed.base.one "
    if private_key_type != "SAME":
        reply_text += (
            "\n\n本次为您生成树洞专属私钥，您可弃之不用，也可点击机器人头像访问网页 https://feed.base.one 导入该私钥继续使用。"
        )
    return reply_text


class TreeHoleBot(BlazeClient):
    def __init__(
        self,
        mixin_bot_keystore: dict,
        rum_seed_url: str,
        rss_mixin_id: int,
        rum_same_pvtkey: str,
        private_key_type: str,
        http_api_base: str = HTTP_ZEROMESH,
        blaze_api_base: str = BLAZE_ZEROMESH,
        text_length_max: int = TEXT_LENGTH_MAX,
        text_length_min: int = TEXT_LENGTH_MIN,
        same_tag: str = "#树洞 ",
        welcome_text: str = None,
        reply_text: str = None,
        last_active_seconds: int = 10,  # 单个连接的发送消息间隔
    ):
        self.config = AppConfig.from_payload(mixin_bot_keystore)
        super().__init__(
            self.config,
            on_message=self.message_handle,
            on_error=self.message_handle_error_callback,
            api_base=blaze_api_base,
        )
        self.xin = HttpClient_WithAppConfig(self.config, api_base=http_api_base)
        self.text_length_max = text_length_max
        self.text_length_min = text_length_min
        self.private_key_type = private_key_type
        self.rss_mixin_id = rss_mixin_id
        self.rum_seed_url = rum_seed_url
        self.welcome_text = welcome_text or init_welcome_text(
            private_key_type, text_length_min, text_length_max, rss_mixin_id
        )
        self.rum_same_pvtkey = rum_same_pvtkey
        self.same_tag = same_tag
        self.reply_text = reply_text
        self.last_active = {}  # uuid: datetime
        self.last_active_seconds = last_active_seconds

    def run(self):
        super().run_forever(2)

    def message_handle_error_callback(self, error, details):
        """message_handle_error_callback"""
        logger.error("===== error_callback =====")
        logger.error("error: %s", error)
        logger.error("details: %s", details)

    @staticmethod
    def message_handle(self, message):
        """message_handle"""

        action = message["action"]
        if action == "ERROR":
            logger.warning(message["error"])
        if action != "CREATE_MESSAGE":
            return
        error = message.get("error")
        if error:
            logger.warning(str(error))
            return

        message_data = message.get("data", {})
        message_id = message_data.get("message_id")
        conversation_id = message_data.get("conversation_id")

        if not message_id or not conversation_id:
            super().echo(message_id)
            return
        if message_data.get("type") != "message":
            super().echo(message_id)
            return

        create_at = parse_rfc3339_to_datetime(message_data.get("created_at"))
        blaze_for_hour = datetime.datetime.now() + datetime.timedelta(hours=-32)
        if create_at <= blaze_for_hour:
            super().echo(message_id)
            return

        data = message_data.get("data")
        if not (data and isinstance(data, str)):
            super().echo(message_id)
            return

        category = message_data.get("category")
        if category not in ["PLAIN_TEXT", "PLAIN_IMAGE"]:
            super().echo(message_id)
            return

        to_send_data = {}
        reply_text = ""
        reply_msgs = []

        if category == "PLAIN_TEXT":
            text = super().parse_message_data(data, category)
            if text.lower() in ["hi", "hello", "nihao", "你好", "help", "?", "？", "1"]:
                reply_text = self.welcome_text
            elif len(text) <= self.text_length_min or len(text) >= self.text_length_max:
                reply_text = f"text length should be >= {self.text_length_min} and <= {self.text_length_max}, please retry or send 'help'"
            else:
                to_send_data = {"content": text}
        elif category == "PLAIN_IMAGE":
            try:
                attachment_id = json.loads(base64.b64decode(data)).get("attachment_id")
                attachment = self.xin.api.message.read_attachment(attachment_id)
                view_url = attachment["data"]["view_url"]
                content = requests.get(view_url, timeout=15).content  # 图片 content
                to_send_data = {"images": [content]}
            except Exception as err:
                to_send_data = None
                logger.warning(err)

        if conversation_id not in self.last_active:
            self.last_active[conversation_id] = datetime.datetime.now()
        else:
            delta = datetime.datetime.now() - self.last_active[conversation_id]
            if delta.total_seconds() < self.last_active_seconds:
                reply_text = "发送太快了，请稍后再试"
                to_send_data = None

        if to_send_data:
            try:
                if self.private_key_type == "SAME":
                    to_send_data["content"] = self.same_tag + to_send_data.get(
                        "content", ""
                    )
                    rum = MiniNode(self.rum_seed_url, self.rum_same_pvtkey)
                else:
                    rum = MiniNode(self.rum_seed_url)
                post = feed.new_post(**to_send_data)
                post["origin"] = {"type": "mixin", "name": f"treehole-bot"}
                resp = rum.api.post_content(post)
                if "trx_id" in resp:
                    logger.warning("sent_to_rum done.%s", resp["trx_id"])
                    reply_text = self.reply_text or init_reply_text(
                        resp["trx_id"], self.rss_mixin_id, self.private_key_type
                    )
                    if self.private_key_type != "SAME":
                        reply_msgs.append(
                            pack_message(
                                pack_text_data(rum.account.pvtkey),
                                conversation_id=conversation_id,
                                quote_message_id=message_id,
                            )
                        )
            except Exception as err:
                logger.warning(err)

        if reply_text:
            reply_msg = pack_message(
                pack_text_data(reply_text),
                conversation_id=conversation_id,
                quote_message_id=message_id,
            )
            reply_msgs.insert(0, reply_msg)
        if reply_msgs:
            for msg in reply_msgs:
                self.xin.api.send_messages(msg)
        super().echo(message_id)
        return
