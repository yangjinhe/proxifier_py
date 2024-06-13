## 这是什么？
使用python调用redsocks，在Linux上实现类似proxifier的功能。
支持多组配置，目的地址支持ip段、单个ip、指定ip加端口

## 如何使用？

- 编辑好配置文件
```json
[
  {
    "proxy": "socks5://192.168.56.130:33080",
    "targets": [
      "10.123.123.0/24",
      "10.124.124.0/24"
    ]
  },
  {
    "proxy": "socks5://192.168.56.131:33080",
    "targets": [
      "172.18.35.0/24",
      "172.18.36.0/24",
      "192.168.33.123:443",
      "192.168.123.124"
    ]
  }
]

```
- 安装好依赖的iptables和redsocks
```shell
sudo apt-get install iptables redsocks
```

- 启动
```shell
sudo python3 main.py
```