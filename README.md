# 				ChatRoom

> [!CAUTION]
>
> 该项目暂时维护到生成房间，正在开发聊天服务迁移和客户端重新连接
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



feature确认

- 用户认证（√）
- 聊天室登录认证（现在卡在这一环）
- 连接数据库（√）
- 传输加密（×）
- 断线重连（做了一半）
- 分配运行在线程上的多个聊天室（√）
- 离开聊天室销毁数据（做了一半）
- 聊天室限定expire时间（√）
- 端口检测（√）



使用了sqlite3数据库进行服务器数据的存储，包含四个表Keys、Map、Users、Rooms，分别存储房间token，用户和房间关系，用户列表和房间列表。

> [!NOTE]
>
> Update Note 2024/10/12

- 增加了 Timer 模块 但是还在研究如何获取 pid
- 将服务器端用户收发信息独立出来，防止类变量赋值出错
- 更新了data数据结构，重写了Forward函数，现在的端口转发分为密钥服务和聊天服务器专用的转发函数，用户的create动作已经可以使用了
- ban掉了用户接收 ’ChatRoom‘ 模式的部分
- 提升了部分程序安全性，包括发送函数重命名， 分离用户初始动作和后续的信息收发
- 由于还在debug阶段，用户信息收发主体的错误文本可读性依旧很高，这部分请通融

[流程图 || 分享密码:ssss](https://boardmix.cn/app/share/CAE.CIiKngwgASoQy8Vz3-jClB3qam4Hb3WaKzAGQAE/dr3QyY)
