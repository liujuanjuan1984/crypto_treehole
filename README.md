# crypto_treehole 加密树洞

树洞 Bot，基于 [Mixin Messenger](https://mixin.one/) 和 [Rum System](https://rumsystem.net/) 开发。

特点：

- 用户通过 mixin bot 作为内容发布入口
- 除了树洞内容，用户的任何隐私数据、行为数据均不采集或存储
- 树洞内容，将采用 Ethereum 规范的密钥签名，即时推送到 RUM 种子网络上链存储

部署时，有两种密钥方案可选择（修改 PRIVATE_KEY_TYPE 参数）：

- DIFF: 每条树洞随机生成新密钥
- SAME: 所有树洞采用同一个密钥

### 部署

1、mixin bot：在 mixin 开发者后台申请创建，获得 session keystore 作为 MIXIN_BOT_KEYSTORE 

2、seed url:通过 rum fullnode 创建 group 并生成轻节点 seedurl，或获取现有的 轻节点 seedurl

3、安装 crypto_treehole：```pip install crypto_treehole```

4、修改配置并运行：```python do_treehole.py &```

### Source

- Mixin python sdk https://github.com/nodewee/mixin-sdk-python
- quorum data module for python: https://github.com/liujuanjuan1984/quorum-data-py
- quorum mininode sdk for python: https://github.com/liujuanjuan1984/quorum-mininode-py 
- and more ...  https://github.com/okdaodine/awesome-quorum

### License

This work is released under the `MIT` license. A copy of the license is provided in the [LICENSE](https://github.com/liujuanjuan1984/crypto_treehole/blob/master/LICENSE) file.
