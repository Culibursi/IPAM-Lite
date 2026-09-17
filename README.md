# IPAM Lite

A lightweight, single-file IP address management tool for small ops teams.  
Simple UI, focused features.  
No database server, no web server setup — just one Python file + one SQLite file.  
View, add, edit, filter, and export IPs in your browser. Data travels with the files.

[English](#english) | [中文](#中文)

---

## English

### Table of Contents

- [Features](#features)
- [Files](#files)
- [Requirements](#requirements)
- [Quick Start (Windows)](#quick-start-windows)
- [Quick Start (Linux / macOS)](#quick-start-linux--macos)
- [Usage](#usage)
  - [Add IP](#add-ip)
  - [Domain Management](#domain-management)
  - [Import Data](#import-data)
  - [Edit / Delete](#edit--delete)
  - [Filter and Search](#filter-and-search)
  - [Export CSV](#export-csv)
- [Backup and Migration](#backup-and-migration)
- [Multi-User Access](#multi-user-access)
- [FAQ](#faq)
- [Notes](#notes)
- [License](#license)

---

### Features

- Browser-based, no client installation required
- Records IP, status, domain, hostname, user, owner, MAC, subnet, VLAN, note, updated time
- Domain management to separate different organizations (e.g., A Bureau, B Office, C Department)
- Status categories: free, used, reserved, conflict, deprecated
- Filter by status and domain, one-click view of all free IPs
- Keyword search: IP, hostname, user, owner, note
- Import from CSV (Excel) — existing IPs are updated, new ones are added
- One-click CSV export, opens directly in Excel
- Data stored in a single `ipam.db` file; backup is just copying the file
- Only one `ipam.py` file; copy two files to another machine and it keeps working
- No MySQL / PostgreSQL / Redis / Nginx required

---

### Files

```text
D:\ipam\
├── ipam.py      # Main program
├── ipam.db      # Database, auto-generated on first run
├── README.md    # This file
└── LICENSE      # MIT License
```

- `ipam.py`: Python program with web UI and database logic.
- `ipam.db`: SQLite database, all IP records are stored here.
- `README.md`: Usage documentation.
- `LICENSE`: MIT License.


---

### Requirements

- Python 3.8 or later
- Flask (installed via pip)
- Browser: Chrome, Edge, Firefox, etc.

No extra database installation needed.

---

### Quick Start (Windows)

#### 1. Install Python

1. Download Python 3 from <https://www.python.org/downloads/>.
2. During installation, make sure to check **Add python.exe to PATH**.
3. After installation, press `Win + R`, type `cmd`, press Enter.
4. Verify with:

   ```cmd
   python --version
   ```

   If you see `Python 3.x.x`, installation is successful.

#### 2. Create Project Folder

1. Create a folder on D drive (or anywhere you want): `D:\ipam`
2. Create a text file in it and rename it to `ipam.py`
   - Note: Windows hides file extensions by default. Enable "File name extensions" in View first, and make sure the name is `ipam.py`, not `ipam.py.txt`.
3. Open `ipam.py` with VS Code, Notepad++, or Notepad.
4. Paste the source code, save as **UTF-8**.

If you already have the source file, skip this step.

#### 3. Install Flask

Open cmd, go to the project directory:

```cmd
cd /d D:\ipam
```

Install Flask:

```cmd
python -m pip install flask
```

If you see `Successfully installed flask...`, it worked.

#### 4. Start the Program

In the same cmd window:

```cmd
python ipam.py
```

You should see something like:

```text
IPAM 已启动: http://127.0.0.1:5000
 * Running on http://127.0.0.1:5000
```

**Do not close this window**, or the service will stop. You can minimize it.

#### 5. Open in Browser

Enter in the address bar:

```text
http://127.0.0.1:5000
```

Press Enter to see the IP management page.

#### 6. Quick Command Reference

1. Open cmd
2. `cd /d D:\ipam`
3. `python ipam.py`
4. Open `http://127.0.0.1:5000` in browser

To stop: press `Ctrl + C` in the cmd window.

---

### Quick Start (Linux / macOS)

```bash
# 1. Create directory
mkdir -p ~/ipam && cd ~/ipam

# 2. Create ipam.py, paste code and save
# 3. Install Flask
python3 -m pip install flask

# 4. Start
python3 ipam.py
```

Open `http://127.0.0.1:5000` in your browser.

To run in background:

```bash
nohup python3 ipam.py > ipam.log 2>&1 &
```

To stop:

```bash
pkill -f ipam.py
```

---

### Usage

#### Add IP

1. Click **+ 新增** at the top
2. Fill in the IP address (required)
3. Select status: free / used / reserved / conflict / deprecated
4. Select a domain (optional; leave as "Unclassified" if not needed)
5. Optionally fill in hostname, MAC, user, owner, subnet, VLAN, note
6. Click **保存**

#### Domain Management

1. Click **管理域** at the top of the IP list
2. Enter a name (e.g., "xx Bureau", "xx Office", "xxx Department") and a note
3. Click **添加域**
4. You can edit or delete a domain later
   - Deleting a domain does **not** delete its IPs. They simply become "Unclassified".

#### Import Data

1. Click **导入数据** at the top
2. Prepare your data:
   - Save your Excel file as **CSV (comma-separated)**
   - Header row should include: `IP, 状态, 域, 主机名, 使用者, 负责人, MAC, 网段, VLAN, 备注`
   - Status can be Chinese (空闲/已用/保留/冲突/停用) or English (free/used/reserved/conflict/deprecated)
   - If a domain in the CSV does not exist yet, it will be created automatically
3. Download the CSV template if you're not sure about the format
4. Select the CSV file and click **开始导入**
5. Existing IPs will be updated; new IPs will be added

#### Edit / Delete

- Click **编辑** on the right of a row to edit
- Click **删除** to delete; a confirmation dialog will appear

#### Filter and Search

- Top buttons: All, Free, Used, Reserved
- Domain row above: filter by domain
- Search box on the right: fuzzy search by IP, hostname, user, owner, note
- Free IPs are highlighted in green for quick identification

#### Export CSV

Click **导出 CSV** at the top; the browser downloads a CSV file.  
Open it directly in Excel; Chinese characters won't be garbled (BOM included).  
The export includes domain and user columns.

#### About "Free IP"

This tool is ledger-based:  
You need to enter an IP and mark it as "free" for it to appear in the "Free" filter.  
It does not scan the network automatically and will not discover unregistered IPs.

If you need "enter a subnet and auto-list all IPs with free/used status", please wait for a future version.

---

### Backup and Migration

#### Backup

Simply copy the `ipam.db` file.  
It's recommended to copy it daily or weekly with a date, for example:

```text
ipam_2026-09-16.db
```

#### Migrate to Another Computer

1. Copy `ipam.py` and `ipam.db` to the same directory on the new machine
2. Install Python and Flask
3. Run `python ipam.py`
4. Open `http://127.0.0.1:5000`

#### Migrate from Excel

Use the built-in **导入数据** feature:  
1. Open your Excel file and save it as **CSV (comma-separated)**
2. Make sure the header matches the recommended format
3. Upload it via the **导入数据** page

If you have a lot of records, this is much faster than entering them one by one.

---

### Multi-User Access

Recommended: **one machine runs the service, others access via browser.**

1. Use a machine that stays on, or an internal server. Put `D:\ipam` on it.
2. Run on that machine:

   ```cmd
   python ipam.py
   ```

3. Find its IP: run `ipconfig` in cmd, look for the IPv4 address, e.g. `192.168.1.50`.
4. Others open in their browser:

   ```text
   http://192.168.1.50:5000
   ```

If it doesn't open, check the **Windows Firewall** on that machine and allow port 5000.

> Do not run separate `ipam.py` instances on different machines and edit separately — data will not sync.  
> Run one server, everyone accesses the same address.

---

### FAQ

#### 1. `python` is not recognized

Python is not installed properly, or **Add python.exe to PATH** was not checked.  
Reinstall Python, check PATH, and try again.

#### 2. `pip install flask` is slow or fails

Use a mirror:

```cmd
python -m pip install flask -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 3. Browser can't open `127.0.0.1:5000`

- Make sure the program is still running in cmd, with no errors
- Make sure the window is not closed
- Make sure the port is not occupied

#### 4. Port 5000 is occupied

Edit the last line of `ipam.py`:

```python
app.run(host="0.0.0.0", port=5000, debug=False)
```

Change `5000` to another port, e.g. `8080`.  
Then open `http://127.0.0.1:8080`.

#### 5. Others can't access my service

- Make sure you are on the same LAN
- Make sure your IP address is correct (check with `ipconfig`)
- Make sure Windows Firewall allows port 5000
- Make sure the program listens on `0.0.0.0`, not `127.0.0.1`

#### 6. Will data be lost?

Data is in the `ipam.db` file.  
As long as you back it up regularly, it won't be lost.  
Do not edit `ipam.db` with a text editor; it's a binary database file.

#### 7. Chinese characters are garbled

- Save `ipam.py` as UTF-8
- Exported CSV includes BOM, so Excel opens it correctly
- If the browser shows garbled text, check system locale or use Chrome/Edge

#### 8. How to stop the program?

Press `Ctrl + C` in the cmd window running the program.

#### 9. How to change the listening port?

Edit the last line of `ipam.py`, change `port=5000` to another port.

#### 10. How to auto-start on boot?

On Windows, use `nssm` to register `python ipam.py` as a service.  
On Linux, use `systemd`.

#### 11. Database is locked

This usually happens when multiple people write at the same time, or an external tool has the `ipam.db` file open.  
The program now includes `timeout=15` and WAL mode to reduce this.  
If it still happens, close any external tools that may have the database open, and restart the program.

---

### Notes

- This is a simple ledger tool, not an automatic discovery tool. Suitable for personal IP ops or small teams.
- Back up `ipam.db` regularly.
- Do not expose the service directly to the public internet.
- Use firewall and access control for internal use.
- Back up `ipam.db` before modifying `ipam.py`.
- If two people edit the same record simultaneously, the later save overwrites the earlier one. Coordinate accordingly.

---

### License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## 中文

一个给小型运维团队用的轻量IP台账工具。
UI简洁，功能专一。
不用装数据库服务，不用配 Web 服务器，一个 Python 文件 + 一个 SQLite 文件就能直接运行。
浏览器里查看、新增、编辑、筛选、导出 IP，数据跟着文件走。

### 目录

- [功能特性](#功能特性)
- [文件说明](#文件说明)
- [环境要求](#环境要求)
- [快速开始（Windows）](#快速开始windows)
- [快速开始（Linux / macOS）](#快速开始linux--macos)
- [使用说明](#使用说明)
  - [新增 IP](#新增-ip)
  - [域管理](#域管理)
  - [导入数据](#导入数据)
  - [编辑 / 删除](#编辑--删除)
  - [筛选与搜索](#筛选与搜索)
  - [导出 CSV](#导出-csv)
- [数据备份与迁移](#数据备份与迁移)
- [多人如何共用](#多人如何共用)
- [常见问题](#常见问题)
- [注意事项](#注意事项)
- [许可](#许可)

---

### 功能特性

- 浏览器操作，不需要装客户端
- 记录 IP、状态、域、主机名、使用者、负责人、MAC、网段、VLAN、备注、更新时间
- 支持分域管理，可将不同机构与部门的 IP 分开
- 状态分类：空闲、已用、保留、冲突、停用
- 按状态和域筛选，一键查看所有空闲 IP
- 关键字搜索：IP、主机名、使用者、负责人、备注
- 支持从 CSV（Excel）导入数据，已有 IP 自动更新，新 IP 自动新增
- 一键导出 CSV，Excel 可直接打开
- 数据存在单个 `ipam.db` 文件里，备份可直接复制文件
- 程序只有一个 `ipam.py`，换电脑拷两个文件就能继续用
- 不需要 MySQL / PostgreSQL / Redis，也不需要 Nginx

---

### 文件说明

```text
D:\ipam\
├── ipam.py      # 程序本体
├── ipam.db      # 数据文件，第一次运行后自动生成
├── README.md    # 本说明文件
└── LICENSE      # MIT 许可证
```

- `ipam.py`：Python 程序，包含网页界面和数据库逻辑。
- `ipam.db`：SQLite 数据库，所有的 IP 记录都在这里。
- `README.md`：使用说明，就是当前这个文件。
- `LICENSE`：MIT 许可证。

---

### 环境要求

- Python 3.8 或更高版本
- Flask（通过 pip 安装）
- 浏览器：Chrome、Edge、Firefox 等均可

不需要额外安装数据库。

---

### 快速开始（Windows）

#### 1. 安装 Python

1. 打开 <https://www.python.org/downloads/> 下载 Python 3。
2. 安装时务必勾选 **Add python.exe to PATH**。
3. 安装完成后，按 `Win + R`，输入 `cmd`，回车。
4. 输入以下命令验证：

   ```cmd
   python --version
   ```

   看到 `Python 3.x.x` 就表示安装成功。

#### 2. 创建项目文件夹

1. 在 D 盘（或任意你想要部署的位置）新建文件夹：`D:\ipam`
2. 在文件夹里新建文本文件，重命名为 `ipam.py`
   - 注意：Windows 默认隐藏扩展名，请先在“查看”里勾选“文件扩展名”，确保文件名是 `ipam.py`，不是 `ipam.py.txt`
3. 用 VS Code、Notepad++ 或记事本打开 `ipam.py`
4. 把源代码粘贴进去，保存，编码选 **UTF-8**

若已有源文件，可跳过此步骤。

#### 3. 安装 Flask

打开 cmd，进入项目目录：

```cmd
cd /d D:\ipam
```

安装 Flask：

```cmd
python -m pip install flask
```

看到 `Successfully installed flask...` 就成功了。

#### 4. 启动程序

在同一个 cmd 窗口输入：

```cmd
python ipam.py
```

看到类似输出：

```text
IPAM 已启动: http://127.0.0.1:5000
 * Running on http://127.0.0.1:5000
```

**这个黑窗口不要关**，关了会导致服务停止。可以最小化。

#### 5. 打开浏览器

地址栏输入：

```text
http://127.0.0.1:5000
```

回车即可看到 IP 管理页面。

#### 6. 指令速查

1. 打开 cmd
2. 输入 `cd /d D:\ipam`
3. 输入 `python ipam.py`
4. 浏览器打开 `http://127.0.0.1:5000`

停止程序：在 cmd 窗口按 `Ctrl + C`。

---

### 快速开始（Linux / macOS）

```bash
# 1. 创建目录
mkdir -p ~/ipam && cd ~/ipam

# 2. 创建 ipam.py，粘贴代码并保存
# 3. 安装 Flask
python3 -m pip install flask

# 4. 启动
python3 ipam.py
```

浏览器打开 `http://127.0.0.1:5000`。

如果希望后台运行：

```bash
nohup python3 ipam.py > ipam.log 2>&1 &
```

停止：

```bash
pkill -f ipam.py
```

---

### 使用说明

#### 新增 IP

1. 点击顶部 **+ 新增**
2. 填写 IP 地址（必填）
3. 选择状态：空闲 / 已用 / 保留 / 冲突 / 停用
4. 选择所属域（可选，不选则归为“未分类”）
5. 按需填写主机名、MAC、使用者、负责人、网段、VLAN、备注
6. 点击 **保存**

#### 域管理

1. 在 IP 列表顶部点击 **管理域**
2. 输入名称（如：xx局、xx所、xxx部门）和备注
3. 点击 **添加域**
4. 之后可以编辑或删除域
   - 删除域 **不会** 删除该域下的 IP，它们会自动变为“未分类”

#### 导入数据

1. 点击顶部 **导入数据**
2. 准备数据：
   - 将 Excel 文件另存为 **CSV（逗号分隔）** 格式
   - 表头建议包含：`IP, 状态, 域, 主机名, 使用者, 负责人, MAC, 网段, VLAN, 备注`
   - 状态列填中文（空闲/已用/保留/冲突/停用）或英文（free/used/reserved/conflict/deprecated）均可
   - 如果 CSV 中的域不存在，导入时会自动创建
3. 如果不确定格式，可以点击“下载 CSV 模板”
4. 选择 CSV 文件，点击 **开始导入**
5. 已存在的 IP 会被更新，不存在的 IP 会被新增

#### 编辑 / 删除

- 在列表右侧点击 **编辑** 修改记录
- 点击 **删除** 会弹出确认框，确认后删除

#### 筛选与搜索

- 顶部按钮：全部、空闲、已用、保留
- 上方“域”行：按域筛选
- 右侧搜索框：支持 IP、主机名、使用者、负责人、备注模糊搜索
- 空闲 IP 会以绿色背景显示，方便快速识别

#### 导出 CSV

点击顶部 **导出 CSV**，浏览器会下载一个 CSV 文件。  
用 Excel 直接打开即可，中文不会乱码（已加 BOM）。  
导出内容包含“域”和“使用者”列。

#### 关于“空闲 IP”

这个工具是“台账式”管理：  
你需要先录入 IP，并把状态标为“空闲”，它才会出现在“空闲”筛选里。  
它不是自动扫描整个网段，不会自动发现未登记的 IP。

如果你需要“输入网段自动列出所有 IP 并标记空闲/已用”，请等待版本更新。

---

### 数据备份与迁移

#### 备份

直接复制 `ipam.db` 文件即可。  
建议每天或每周复制一份，加上日期，例如：

```text
ipam_2026-09-16.db
```

#### 迁移到另一台电脑

1. 复制 `ipam.py` 和 `ipam.db` 到新电脑的同一目录
2. 在新电脑安装 Python 和 Flask
3. 运行 `python ipam.py`
4. 浏览器打开 `http://127.0.0.1:5000`

#### 从 Excel 迁移

推荐使用内置的 **导入数据** 功能：  
1. 打开 Excel，另存为 **CSV（逗号分隔）**
2. 确保表头符合推荐格式
3. 在 **导入数据** 页面上传该 CSV

如果记录很多，这比手动一条条录入快很多。

---

### 多人如何共用

推荐方式：**一台电脑跑服务，其他人用浏览器访问。**

1. 找一台常开的电脑或内网服务器，把 `D:\ipam` 放上去。
2. 在那台机器上运行：

   ```cmd
   python ipam.py
   ```

3. 查看那台机器的 IP：在该机器 cmd 输入 `ipconfig`，找到 IPv4 地址，例如 `192.168.1.50`。
4. 另一个人在自己电脑浏览器访问：

   ```text
   http://192.168.1.50:5000
   ```

如果打不开，检查那台机器的 **Windows 防火墙**，放行 5000 端口。

> 不要几个人各自跑各自的 `ipam.py`，然后各改各的，数据会不同步。  
> 跑一个服务器，大家访问同一个地址，可以统合IP地址。

---

### 常见问题

#### 1. `python` 不是内部或外部命令

说明 Python 没装好，或者安装时没有勾选 **Add python.exe to PATH**。  
重新安装 Python，勾选 PATH，再试。

#### 2. `pip install flask` 很慢或失败

使用国内镜像：

```cmd
python -m pip install flask -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 3. 浏览器打不开 `127.0.0.1:5000`

- 确认 cmd 窗口里程序还在运行，没有报错
- 确认没有关闭黑窗口
- 确认端口没有被占用

#### 4. 端口 5000 被占用

修改 `ipam.py` 最后一行：

```python
app.run(host="0.0.0.0", port=5000, debug=False)
```

把 `5000` 改成其他端口，比如 `8080`。  
然后浏览器访问 `http://127.0.0.1:8080`。

#### 5. 别人访问不了我的服务

- 确认对方和你在同一内网
- 确认你的 IP 地址正确（`ipconfig` 查看）
- 确认 Windows 防火墙放行了 5000 端口
- 确认程序监听的是 `0.0.0.0` 而不是 `127.0.0.1`

#### 6. 数据会丢吗？

数据在 `ipam.db` 文件里。  
只要定期复制备份，就不会丢。  
不要手动用文本编辑器改 `ipam.db`，它是二进制数据库文件。

#### 7. 中文乱码

- `ipam.py` 保存为 UTF-8
- 导出的 CSV 已带 BOM，Excel 打开正常
- 如果浏览器显示乱码，检查系统区域设置或换 Chrome/Edge

#### 8. 怎么停止程序？

在运行程序的 cmd 窗口按 `Ctrl + C`。

#### 9. 怎么修改监听端口？

编辑 `ipam.py` 最后一行，修改 `port=5000` 为其他端口。

#### 10. 怎么开机自启？

Windows 可以用 `nssm` 把 `python ipam.py` 注册成服务。  
Linux 可以用 `systemd`。

#### 11. 数据库被锁定（database is locked）

通常是因为多个人同时写入，或者有外部工具（如 DB Browser、VSCode）打开了 `ipam.db` 文件。  
当前代码已加入 `timeout=15` 和 WAL 模式来减少这个问题。  
如果仍然出现，请关掉可能占用数据库的外部工具，然后重启程序。

---

### 注意事项

- 本工具是简易台账式IP管理工具，不是自动扫描发现工具，无法自动扫描网段获取IP。仅适用于个人 IP 运维或小型团队。
- 请定期备份 `ipam.db`。
- 不要把服务直接暴露到公网。
- 内网使用建议配合防火墙和访问控制。
- 修改 `ipam.py` 代码前，先备份 `ipam.db`。
- 如果多人同时编辑同一条记录，后保存的会覆盖先保存的，请注意协调。
- 请勿重复快速操作修改指令，可能会导致数据库锁死。

---

### 许可

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE)。