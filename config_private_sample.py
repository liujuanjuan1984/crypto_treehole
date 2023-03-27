# the treehole bot's keystore file, init from dashboard of mixin.
MIXIN_BOT_KEYSTORE = {
    "pin": "123474",
    "client_id": "30789e31-xxxx-xxxx-xxxx-1a45e781ae2e",
    "session_id": "d92a35ea-xxxx-xxxx-xxxx-3ccb3491e013",
    "pin_token": "q0ij-E04eCWXpq3SXzp2UXnaitt3JMwPlh1a9NsCQ3M",
    "private_key": "nxw2h201ESDA2_ReiExxxxxt06qj5i2Men_SIUP2IZiwgGe0g8pAsItelRNNNgvjyIKYg0eWvtecH9essI-xqg",
}

# update the mixin_id of rss bot
RSS_MIXIN_ID = "30789e31-xxxx-xxxx-xxxx-1a45e781ae2e"

# eth account private key to sign trx to rum group
SAME_PVTKEY = "0x71918e304c3813560eb3c62xxxxa786870b06d9941ca2eb0a77fa60d19917526"

# the rum group's seed url, init by fullnode joined or created the group.
RUM_SEED_URL = "rum://seed?v=1&e=0&n=0&b=i7pFz0vLTxCwu...WSMvSM"
GROUP_NAME = "种子网络的名字"

# about PRIVATE_KEY_TYPE: "SAME" or "DIFF"
# DIFF: each treehole got a private key
# SAME: user the same privtea key; better for users to ban the treehole contents
PRIVATE_KEY_TYPE = "SAME"


HTTP_ZEROMESH = "https://mixin-api.zeromesh.net"
BLAZE_ZEROMESH = "wss://mixin-blaze.zeromesh.net"

TEXT_LENGTH_MIN = 10
TEXT_LENGTH_MAX = 500
RSS_MIXIN_ID_NUM = "7000123456"
WELCOME_TEXT = f"""👋 hi, I am TreeHole bot

向我发送图片或文本（长度不低于 {TEXT_LENGTH_MIN} ，不超出 {TEXT_LENGTH_MAX}）；
我将以密钥签名，把该图片或文本以“树洞”的形式发送到 RUM 种子网络{GROUP_NAME}。

我不存储任何数据，请放心享受真正匿名的“树洞”吧。

想要查阅已发布的树洞或互动？
请通过 Rum 应用加入种子网络 {GROUP_NAME} 或在 Mixin 上使用 bot：{RSS_MIXIN_ID_NUM}
"""
