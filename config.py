from rumpy.utils import decode_seed

import config_private as PVT

HTTP_DEFAULT = "https://api.mixin.one"
HTTP_ZEROMESH = "https://mixin-api.zeromesh.net"
BLAZE_DEFAULT = "wss://blaze.mixin.one"
BLAZE_ZEROMESH = "wss://mixin-blaze.zeromesh.net"

# update these:
DEV_MIXIN_ID = PVT.DEV_MIXIN_ID
RSS_MIXIN_ID = PVT.RSS_MIXIN_ID
MIXIN_BOT_KEYSTORE = PVT.MIXIN_BOT_KEYSTORE

# about PRIVATE_KEY_TYPE: "SAME" or "DIFF"
# DIFF: each treehole got a private key
# SAME: user the same privtea key; better for users to ban the treehole contents
PRIVATE_KEY_TYPE = "SAME"
SAME_PVTKEY = PVT.SAME_PVTKEY
RUM_SEED_URL = PVT.RUM_SEED_URL
GROUP_NAME = decode_seed({"seed": RUM_SEED_URL})["group_name"]

WELCOME_TEXT = f"""👋 你好，我是 TreeHole 机器人。

向我发送图片，或文本（长度不低于 10 ，不超出 500）；
我将以密钥签名，把该图片或文本以“树洞”的形式发送到 RUM 种子网络{GROUP_NAME}。

我不存储任何数据，请放心享受真正匿名的“树洞”吧。

想要查阅已发布的树洞或互动？
请通过 Rum 应用加入种子网络 {GROUP_NAME} 或在 Mixin 上使用 RUM种子网络订阅器 bot：
"""
