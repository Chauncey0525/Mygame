#!/usr/bin/env python3
"""
启动脚本
"""
import socket
from app import app


def _local_ip():
    """获取本机局域网 IP，便于 127.0.0.1 无法访问时使用"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None


if __name__ == '__main__':
    ip = _local_ip()
    if ip:
        print(' * 推荐（若 127.0.0.1 打不开请用）: http://%s:5000' % ip)
    app.run(host='0.0.0.0', port=5000, debug=True)
