# TreeHole 树洞

一个基于 Mixin 和 Rum 种子网络的 树洞 Bot demo 的源码。采用 GPLv3 协议开源。

### 简介

这个树洞的特点：

- 用户通过 mixin bot 作为内容发布入口
- 除了树洞内容，用户的任何隐私数据、行为数据，不采集也不存储
- 树洞内容，将采用密钥签名（有 2 种实现方案可选），即时推送到 RUM 种子网络上链存储

密钥有两种实现方案可选，可通过 PRIVATE_KEY_TYPE 来控制。

- DIFF: 随机生成的全新密钥（一次性，不存储）
- SAME: 采用统一密钥

### 部署

1、mixin bot： 在 mixin 开发者后台申请创建，获得 session keystore 填入 config_private.py 的 MIXIN_BOT_KEYSTORE 参数 

2、拷贝 treehole 源码，初始化环境

2.1 环境：

- 安装并激活 [git](https://git-scm.com/download)
- 安装 [python](https://www.python.org/downloads/)，版本建议选择 3.9

2.2 源码：

```bash
git clone https://github.com/liujuanjuan1984/tree_hole.git
cd tree_hole
```

2.3 依赖：

```pip install -r requirements.txt```

2.4 配置文件：

- config_private.py，采用 config_private_sample.py 作为参考模板，请修改所有参数。

3、启动服务：无需守护进程，将自动持续运行。

```bash
python treehole.py
```

### 其它

不建议提交 PR，欢迎 fork 后自行修改使用。

#### 依赖

- Mixin [mixinsdk](https://pypi.org/project/mixinsdk/0.1.5/)
- [quorum-mininode-py](https://github.com/liujuanjuan1984/quorum-mininode-py)
- [quorum-data-py](https://github.com/liujuanjuan1984/quorum-data-py)

#### 格式化

Install:

```bash
pip install black
pip install isort
```

Format:

```bash
isort .
black -l 120 -t py39 .
```
