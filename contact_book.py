# ==========================================
# [W1] Week 1 通讯录管理程序 · 最终版
#
# 综合运用：类设计 + JSON持久化 + logging + 异常处理 + CLI菜单
# 每处关键代码都有注释说明"为什么这么写"
# ==========================================

import json
import os
import logging
from pathlib import Path

# ──────── logging 配置 ────────
# basicConfig = 一次性的基础配置
# level=logging.INFO → 只显示 INFO 及以上级别（忽略 DEBUG）
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S"
)
# 创建命名 logger，之后用 logger.info() 而不是 logging.info()
logger = logging.getLogger("通讯录")


# ──────── ContactBook 类 ────────

class ContactBook:
    def __init__(self, filepath=None):
        """初始化通讯录"""
        # 如果没传路径，默认存桌面 contacts.json
        if filepath is None:
            desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
            filepath = os.path.join(desktop, "contacts.json")
        self.filepath = filepath      # 文件存哪
        self.contacts = []            # 内存中的数据（列表，每个元素是字典）
        self.load()                   # 启动时从文件读取

    # ── JSON 持久化 ──

    def load(self):
        """从 JSON 文件加载联系人到 self.contacts"""
        try:
            if Path(self.filepath).exists():
                with open(self.filepath, "r", encoding="utf-8") as f:
                    # json.load(f) 的参数是文件对象 f，不是路径字符串
                    self.contacts = json.load(f)
                logger.info(f"已加载 {len(self.contacts)} 个联系人")
            else:
                logger.info("未找到文件，创建新的通讯录")
                self.contacts = []
        except json.JSONDecodeError:
            logger.error("文件损坏，无法读取")
        except Exception as e:
            logger.error(f"加载失败: {e}")

    def save(self):
        """把 self.contacts 写回 JSON 文件"""
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                # ensure_ascii=False → 中文不变成 \u...
                # indent=2 → 格式化输出，方便直接看文件
                json.dump(self.contacts, f, ensure_ascii=False, indent=2)
            logger.info(f"已保存 {len(self.contacts)} 个联系人")
        except Exception as e:
            logger.error(f"保存失败: {e}")

    # ── 核心功能 ──

    def add(self, name, phone, email=""):
        """添加联系人（有重名检查）"""
        # 遍历现有联系人，检查是否重名
        for c in self.contacts:
            if c["name"] == name:          # c 是字典，通过键取值
                logger.warning(f"联系人 \"{name}\" 已存在")
                return False
        # 新建联系人字典 {}
        contact = {"name": name, "phone": phone, "email": email}
        self.contacts.append(contact)      # 加入内存列表
        self.save()                        # 立即写文件
        logger.info(f"已添加: {name}")
        return True

    def search(self, keyword):
        """按姓名搜索（支持部分匹配，忽略大小写）"""
        # 列表推导式：遍历 self.contacts，筛选 name 包含 keyword 的
        results = [
            c for c in self.contacts
            if keyword.lower() in c["name"].lower()
        ]
        if results:
            logger.info(f"找到 {len(results)} 个匹配")
        else:
            logger.info(f"未找到 \"{keyword}\"")
        return results                     # 返回列表，不是数量

    def delete(self, name):
        """按姓名删除联系人"""
        before = len(self.contacts)
        # 列表推导式：保留所有 name 不等于目标值的
        self.contacts = [
            c for c in self.contacts
            if c["name"] != name
        ]
        if len(self.contacts) < before:    # 删掉了
            self.save()
            logger.info(f"已删除: {name}")
            return True
        else:
            logger.warning(f"未找到: {name}")
            return False

    def list_all(self):
        """列出所有联系人"""
        if not self.contacts:              # 空列表 = False
            logger.info("通讯录为空")
            return []
        logger.info(f"共 {len(self.contacts)} 个联系人")
        return self.contacts


# ──────── CLI 菜单 ────────

def show_menu():
    print("\n" + "=" * 40)
    print("          [通讯录] 通讯录管理系统")
    print("=" * 40)
    print("  1. [+] 添加联系人")
    print("  2. [搜索] 搜索联系人")
    print("  3. [删除]  删除联系人")
    print("  4. [列表] 显示全部")
    print("  5. [X] 退出")
    print("=" * 40)

def main():
    """主程序 — 注意：这里只需要创建实例，不要重新定义类"""
    book = ContactBook()   # 创建实例

    while True:            # 循环显示菜单
        show_menu()
        choice = input("请选择 [1-5]: ").strip()

        if choice == "1":
            name = input("姓名: ").strip()
            if not name:
                print("[X] 姓名不能为空")
                continue
            phone = input("电话: ").strip()
            email = input("邮箱(可选): ").strip()
            book.add(name, phone, email)

        elif choice == "2":
            keyword = input("输入姓名关键词: ").strip()
            results = book.search(keyword)
            if results:
                for i, c in enumerate(results, 1):
                    print(f"  {i}. {c['name']} | {c['phone']} | {c['email']}")
            else:
                print("[X] 未找到")

        elif choice == "3":
            name = input("输入要删除的姓名: ").strip()
            if book.delete(name):
                print(f"[OK] 已删除: {name}")
            else:
                print(f"[X] 未找到: {name}")

        elif choice == "4":
            contacts = book.list_all()
            if contacts:
                for i, c in enumerate(contacts, 1):
                    print(f"  {i}. {c['name']} | {c['phone']} | {c['email']}")
            else:
                print("[空] 通讯录为空")

        elif choice == "5":
            print("再见 再见！")
            logger.info("程序退出")
            break          # ← 没有 break 就死循环

        else:
            print("[X] 无效选择，请输入 1-5")


# ──────── 运行入口 ────────
# 这行的作用：只有直接运行这个文件时才执行 main()
# 如果是被其他文件 import，不会自动运行
if __name__ == "__main__":
    print("[W1] Week 1 通讯录管理程序")
    main()
