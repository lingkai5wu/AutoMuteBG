# AutoMuteBG
让设定的进程在后台时自动静音，切换到前台恢复。

程序的原理为调用系统的音量合成器，仅Windows可用。

开源地址：[Gitee](https://gitee.com/lingkai5wu/AutoMuteBG) | [GitHub](https://github.com/lingkai5wu/AutoMuteBG)

## 使用方法

1. 前往[Gitee Releases](https://gitee.com/lingkai5wu/AutoMuteBG/releases/latest)或[GitHub Releases](https://github.com/lingkai5wu/AutoMuteBG/releases/latest)下载最近版本的`background_muter.exe`
2. 打开游戏本体
3. 运行`background_muter.exe`
4. 关闭游戏后会自动退出本程序，也可以从状态栏中手动退出。

### 已知问题

- **在游戏运行时强制关闭本程序（例如使用任务管理器或直接关机），本程序无法自动恢复音量**，遇到该问题可以再次启动本程序，或在音量合成器中手动复原。
- ~~有时会忘记自己还在打游戏~~

### 运行截图

![image-20230506110911354](README.assets/image-20230506110911354.png)

![image-20230506111158848](README.assets/image-20230506111158848.png)