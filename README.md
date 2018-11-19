# icon-score-dev
[![CircleCI](https://circleci.com/gh/LayerXcom/icon-score-dev.svg?style=shield)](https://circleci.com/gh/LayerXcom/icon-score-dev)

an example of icon-score smart contract development

## setting up

prepare python environment by `pyenv` and `virtualenv`

```bash
pyenv install 3.6.5
pyenv virtualenv 3.6.5 icon-dev
```

clone the repository

```bash
git clone git@github.com:LayerXcom/icon-score-dev.git
cd icon-score-dev
pyenv local icon-dev && pip install -U pip
```

install dependencies

```
brew install leveldb
brew install autoconf automake libtool pkg-config
brew install rabbitmq && brew services start rabbitmq
```

set up t-bears and sdks


```bash
git clone https://github.com/icon-project/t-bears.git
cd t-bears && ./build.sh
cd dist && pip install <t-bears>.whl
```

start local network

```bash
tbears start
```

## test

```bash
tberas test layerx
```


## deploy

password of `Key@Top1` keystore equals its file name: `Key@Top1`

```
❯ tbears deploy layerx
Input your keystore password:
Send deploy request successfully.
If you want to check SCORE deployed successfully, execute txresult command
transaction hash: 0x40bc6423fb87434f206fc541b5524c10f01bebe09f35a4e6af927496760cc4c2
```

and then check its SCORE address

```
❯ tbears txresult 0xa4f7987ac4cf325da246381506f72615e932d8e9376a542eb67fa85d57f9af79
Transaction result: {
    "jsonrpc": "2.0",
    "result": {
        "txHash": "0xa4f7987ac4cf325da246381506f72615e932d8e9376a542eb67fa85d57f9af79",
        "blockHeight": "0x631",
        "blockHash": "0x7ffeed4e27c7c307e6afc006bda7667b5353bb4f95e8e3cc56c387c659026fda",
        "txIndex": "0x0",
        "to": "cx0000000000000000000000000000000000000000",
        "scoreAddress": "cx3a2115b00690f39e14ec227e0ad50f980f480a53",
        "stepUsed": "0x13c8100",
        "stepPrice": "0x0",
        "cumulativeStepUsed": "0x13c8100",
        "eventLogs": [],
        "logsBloom": "0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
        "status": "0x1"
    },
    "id": 1
}
```

## call methods

```
❯ tbears call calls/call_hello.json
response : {
    "jsonrpc": "2.0",
    "result": "Hello",
    "id": 1
}
```

## References

- ICON sdk references: https://github.com/icon-project/icon-sdk-python
- IRC2 token standard: https://github.com/icon-project/IIPs/blob/master/IIPS/iip-2.md
- Reference implementation of IRC2: https://github.com/sink772/IRC2-token-standard
- ICON Smart Contract - SCORE: https://icon-project.github.io/score-guide/
