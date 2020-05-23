"""
文件服务器 客户端
"""

from socket import *

# 服务器地址
ADDR = ('127.0.0.1',7779)

class FTPClient:
    def __init__(self,sockfd):
        self.sockfd = sockfd

    def do_list(self):
        self.sockfd.send(b"L") # 发请求
        data = self.sockfd.recv(128).decode() # 等反馈
        # 根据反馈选择做什么
        if data == 'OK':
            # 接收文件列表
            data = self.sockfd.recv(1024 * 1024)
            print(data.decode())
        else:
            print("文件库为空")

    def do_get_file(self,file_name):
        data = "D "+file_name
        self.sockfd.send(data.encode())
        data = self.sockfd.recv(128).decode()
        if data == "OK":
            with open(file_name,"wb") as f:
                while True:
                    words = self.sockfd.recv(1024)
                    if words == b"##":
                        break
                    f.write(words)
        else:
            print("文件不存在")

    def do_put_file(self,path_file):
        try:
            f = open(path_file,"rb")
        except:
            print("該文件不存在，上傳失敗！")
            return
        file_name = path_file.split("/")[-1]
        data = "U "+file_name
        self.sockfd.send(data.encode())
        data = self.sockfd.recv(128).decode()
        if data == "OK":
            while True:
                data = f.read(1024 * 10)
                if not data:
                    self.sockfd.send(b"##")
                    break
                self.sockfd.send(data)
        else:
            print("有同名文件，上傳失敗！")

    def do_quit(self):
        self.sockfd.send(b"quit")
        self.sockfd.close()




# 客户端启动函数
def main():
    # 链接服务器
    sockfd = socket()
    sockfd.connect(ADDR)

    ftp = FTPClient(sockfd) # 实例化对象，调用类中的方法

    while True:
        print("=================命令选项====================")
        print("*****            list               *****")
        print("*****          get file             *****")
        print("*****          put file             *****")
        print("*****            quit               *****")
        print("============================================")
        try:
            cmd = input("输入命令:")
        except:
            ftp.do_quit()
            return
        if cmd == 'list': #查看
            ftp.do_list()
        elif cmd[:3] == "get": #下載
            ftp.do_get_file(cmd.split(" ")[-1])
        elif cmd[:3] == "put": #上傳
            ftp.do_put_file(cmd.split(" ")[-1])
        elif cmd == "quit":
            ftp.do_quit()
            return
if __name__ == '__main__':
    main()
