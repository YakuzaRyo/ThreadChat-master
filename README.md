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
