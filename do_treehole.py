from crypto_treehole import TreeHoleBot

# the treehole bot's keystore file, init from dashboard of mixin.
MIXIN_BOT_KEYSTORE = {
    "pin": "123474",
    "client_id": "30789e31-xxxx-xxxx-xxxx-1a45e781ae2e",
    "session_id": "d92a35ea-xxxx-xxxx-xxxx-3ccb3491e013",
    "pin_token": "q0ij-E04eCWXpq3SXzp2UXnaitt3JMwPlh1a9NsCQ3M",
    "private_key": "nxw2h201ESDA2_ReiExxxxxt06qj5i2Men_SIUP2IZiwgGe0g8pAsItelRNNNgvjyIKYg0eWvtecH9essI-xqg",
}

# eth account private key to sign trx to rum group
SAME_PVTKEY = "0x71918e304c3813560eb3c62xxxxa786870b06d9941ca2eb0a77fa60d19917526"

# the rum group's seed url, init by fullnode joined or created the group.
RUM_SEED_URL = "rum://seed?v=1&e=0&n=0&b=i7pFz0vLTxCwu...WSMvSM"

# about PRIVATE_KEY_TYPE: "SAME" or "DIFF"
# DIFF: each treehole got a private key
# SAME: user the same privtea key; better for users to ban the treehole contents

PRIVATE_KEY_TYPE = "SAME"
RSS_MIXIN_ID = "7000123456"


TreeHoleBot(
    MIXIN_BOT_KEYSTORE, RUM_SEED_URL, RSS_MIXIN_ID, SAME_PVTKEY, PRIVATE_KEY_TYPE
).run()
