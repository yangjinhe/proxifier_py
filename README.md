使用python调用redsocks，在Linux上实现类似proxifier的功能。

依赖iptables和redsocks，先安装
```
sudo apt-get install iptables redsocks
```

支持多组配置，目的地址支持ip段、单个ip、指定ip加端口
