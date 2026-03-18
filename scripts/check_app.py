#!/usr/bin/env python3
"""本地自检：确认应用能启动、登录页和首页能渲染，便于排查“打不开”。"""
import sys
from pathlib import Path

# 项目根目录
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

def main():
    print("1. 导入 app ...")
    from app import app
    print("   OK")

    print("2. 请求 /login ...")
    with app.test_client() as c:
        r = c.get("/login")
        if r.status_code != 200:
            print(f"   失败: status={r.status_code}")
            print(r.data[:500].decode("utf-8", errors="replace"))
            return 1
    print("   OK")

    print("3. 请求 / (未登录应 302 到 /login) ...")
    with app.test_client() as c:
        r = c.get("/")
        if r.status_code not in (200, 302):
            print(f"   失败: status={r.status_code}")
            return 1
    print("   OK")

    print("\n自检通过。若浏览器仍打不开，请：")
    print("  - 在项目目录执行: python run.py")
    print("  - 浏览器打开: http://127.0.0.1:5000 或 http://localhost:5000")
    print("  - 若出现 500 错误，看运行 run.py 的终端里是否有红色 Traceback")
    return 0

if __name__ == "__main__":
    sys.exit(main())
