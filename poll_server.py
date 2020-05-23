from socket import *
from select import * #切记一定要导入*　poll 和even事件类型是　同级类型的

#网络连接块
sockfd = socket()
ser_addr = ("0.0.0.0",8888)
sockfd.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
sockfd.bind(ser_addr)
sockfd.listen(5)
sockfd.setblocking(False) #非阻塞态
#多重IO块
p = poll() #创建poll对象
p.register(sockfd,POLLIN) #注册关注IO事件　 参数：sockfd  要关注的IO事件 event  要关注的IO事件类型
reg_map = {sockfd.fileno():sockfd} #创建一个以文件号为键：文件对象的字典

while True:
    print("等待事件发生.....")
    evens = p.poll() #监测关注的IO事件是否发生
    for fd_num,fd in evens:
        if reg_map[fd_num] == sockfd: #  if fd == sockfd.fileno():
            connfd,addr = reg_map[fd_num].accept()
            print("connfd from:",addr) # 该客户端来自那个地方
            connfd.setblocking(False)
            p.register(connfd,POLLIN) #注册一个IO关注事件(连接套接字)
            reg_map[connfd.fileno()] = connfd #更新字典，为了以后连接套接字的相应做准备
        else:
            info = reg_map[fd_num].recv(1024).decode()
            if not info:
                reg_map[fd_num].close() #关闭连接套接字
                p.unregister(fd_num) #参数：IO对象或者IO对象的fileno
                del reg_map[fd_num]
                continue
            print(info)
            reg_map[fd_num].send(b"ok")








