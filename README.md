# 				ChatRoom

> [!CAUTION]
>
> 该项目暂时无法运行
>
> 运行方法如下

```cmd
pip install -r ./requirements
python server_start.py
python client_start.py
```

> [!TIP]
>
> 运行环境：
>
> win11_64x
>
> Python 3.9
>
> 使用socket通信，包含可自定义的host和port



将来会加上的feature

- 用户认证
- 连接数据库
- 传输加密
- 断线重连
- 分配运行在线程上的多个聊天室
- 离开聊天室销毁数据
- 聊天室限定expire时间



连接数据库不知道会对性能产生什么影响，用户认证只使用匿名认证，通过用户提交的昵称生成密钥并由服务器保存，使用完关闭房间后销毁。随着聊天室用户增多，内存使用也可能会出现问题，是否连接数据库进行用户存储有待商榷。
