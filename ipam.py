#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""IPAM Lite - 单文件、无数据库服务的轻量 IP 地址管理工具"""
import sqlite3, csv, io, os
from datetime import datetime
from flask import Flask, request, render_template_string, send_file, redirect, url_for

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "ipam.db")
app = Flask(__name__)

STATUS_LABEL = {"free": "空闲", "used": "已用", "reserved": "保留",
                "conflict": "冲突", "deprecated": "停用"}

def db():
    # 增加 timeout=15，增加15秒排队缓存
    conn = sqlite3.connect(DB, timeout=15)
    conn.row_factory = sqlite3.Row
    # 开启 WAL 模式，允许读写并发，极大减少 database is locked 但我估计现在这个规模最多8个人左右就会卡了
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    conn = db()
    conn.execute("""CREATE TABLE IF NOT EXISTS domains (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        note TEXT)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS ips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT UNIQUE NOT NULL,
        domain_id INTEGER,
        status TEXT NOT NULL DEFAULT 'free',
        hostname TEXT, mac TEXT, owner TEXT, user TEXT,
        subnet TEXT, vlan TEXT, note TEXT,
        updated TEXT)""")
    cols = [r[1] for r in conn.execute("PRAGMA table_info(ips)").fetchall()]
    if "domain_id" not in cols:
        conn.execute("ALTER TABLE ips ADD COLUMN domain_id INTEGER")
    if "user" not in cols:
        conn.execute("ALTER TABLE ips ADD COLUMN user TEXT")
    conn.commit()
    conn.close()

TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>IPAM Lite</title>
<style>
body{font-family:-apple-system,"Microsoft YaHei",sans-serif;margin:0;background:#f5f6f8;color:#333}
.c{max-width:1400px;margin:0 auto;padding:20px}
h1{margin:0 0 16px;font-size:22px}
.tb{margin-bottom:10px;display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.lbl{color:#666;font-size:14px;margin-right:2px}
.tb a{padding:7px 14px;background:#4a90d9;color:#fff;text-decoration:none;border-radius:4px;font-size:14px;white-space:nowrap}
.tb a:hover{background:#357ab8}.tb a.on{background:#2c5f8e}
.tb a.manage{background:#6c757d}.tb a.manage:hover{background:#5a6268}
.tb a.add{background:#28a745}.tb a.add:hover{background:#218838}
.tb a.export{background:#17a2b8}.tb a.export:hover{background:#138496}
.tb a.import{background:#f39c12}.tb a.import:hover{background:#e08e0b}
.cnt{background:rgba(255,255,255,.35);padding:1px 6px;border-radius:8px;font-size:11px;margin-left:4px}
form.s{margin-left:auto;display:flex;gap:6px}
input,select,textarea{padding:7px 10px;border:1px solid #ccc;border-radius:4px;font-size:14px;font-family:inherit}
table{width:100%;border-collapse:collapse;background:#fff;border-radius:6px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.08)}
th,td{padding:9px 12px;text-align:left;border-bottom:1px solid #eef0f2;font-size:14px}
th{background:#fafbfc;color:#555}
tr:last-child td{border-bottom:none}tr:hover{background:#f8fafc}
tr.free{background:#f0faf1}tr.reserved{background:#fffbf0}tr.conflict{background:#fef2f2}
.s{padding:2px 9px;border-radius:10px;font-size:12px}
.s.free{background:#d4edda;color:#1e6f2e}.s.used{background:#d6e9f8;color:#175a85}
.s.reserved{background:#fdeccb;color:#8a5a00}.s.conflict{background:#f8d7da;color:#9b2226}
.s.deprecated{background:#e2e3e5;color:#555}
.dm{background:#e9ecef;color:#495057;padding:2px 8px;border-radius:8px;font-size:12px}
.act a{color:#4a90d9;text-decoration:none;margin-right:8px;font-size:13px}
.act a.d{color:#d9534f}
.fc{background:#fff;padding:24px;border-radius:6px;box-shadow:0 1px 3px rgba(0,0,0,.08);max-width:720px}
.fc label{display:block;margin-bottom:12px}.fc label span{display:block;font-size:13px;color:#666;margin-bottom:4px}
.fc input,.fc select,.fc textarea{width:100%}
.fc .row{display:flex;gap:12px}.fc .row label{flex:1}
.fc .btns{margin-top:8px;display:flex;gap:8px;align-items:center}
.fc .btns button,.fc .btns a{padding:8px 18px;border-radius:4px;font-size:14px;text-decoration:none;border:none;cursor:pointer}
.fc .btns button{background:#4a90d9;color:#fff}.fc .btns a{background:#e9ecef;color:#333}
.hint{color:#888;font-size:12px}
.hint a{color:#4a90d9;text-decoration:none}
.empty{text-align:center;padding:40px;color:#888}
.alert{padding:15px;border-radius:4px;margin-bottom:15px;background:#d4edda;color:#155724;border:1px solid #c3e6cb}
.alert.err{background:#f8d7da;color:#721c24;border-color:#f5c6cb}
</style></head><body><div class="c">"""

INDEX = TEMPLATE + """
<h1>IPAM Lite-简单IP管理系统</h1>

<div class="tb">
  <span class="lbl">域：</span>
  <a href="{{ url_for('index', status=status or None, q=q or None) }}" class="{{ 'on' if not domain_id }}">全部</a>
  {% for d in domains %}
  <a href="{{ url_for('index', status=status or None, domain_id=d['id'], q=q or None) }}"
     class="{{ 'on' if domain_id == d['id']|string }}">{{ d['name'] }}<span class="cnt">{{ domain_counts.get(d['id'], 0) }}</span></a>
  {% endfor %}
  <a href="/domains" class="manage">管理域</a>
</div>

<div class="tb">
  <span class="lbl">状态：</span>
  <a href="{{ url_for('index', domain_id=domain_id or None, q=q or None) }}" class="{{ 'on' if not status }}">全部 {{ counts.total }}</a>
  <a href="{{ url_for('index', status='free', domain_id=domain_id or None, q=q or None) }}" class="{{ 'on' if status=='free' }}">空闲 {{ counts.free }}</a>
  <a href="{{ url_for('index', status='used', domain_id=domain_id or None, q=q or None) }}" class="{{ 'on' if status=='used' }}">已用 {{ counts.used }}</a>
  <a href="{{ url_for('index', status='reserved', domain_id=domain_id or None, q=q or None) }}" class="{{ 'on' if status=='reserved' }}">保留 {{ counts.reserved }}</a>
  <a href="/add" class="add">+ 新增</a>
  <a href="/import" class="import">导入数据</a>
  <a href="/export" class="export">导出 CSV</a>
  <form class="s" method="get">
    {% if status %}<input type="hidden" name="status" value="{{ status }}">{% endif %}
    {% if domain_id %}<input type="hidden" name="domain_id" value="{{ domain_id }}">{% endif %}
    <input type="text" name="q" placeholder="搜索..." value="{{ q or '' }}">
    <button type="submit">搜索</button>
  </form>
</div>

<table><thead><tr>
<th>IP</th><th>状态</th><th>域</th><th>主机名</th><th>使用者</th><th>负责人</th><th>MAC</th><th>网段</th><th>VLAN</th><th>备注</th><th>操作</th>
</tr></thead><tbody>
{% for r in rows %}
<tr class="{{ r['status'] }}">
  <td><strong>{{ r['ip'] }}</strong></td>
  <td><span class="s {{ r['status'] }}">{{ labels[r['status']] }}</span></td>
  <td>{% if r['domain_name'] %}<span class="dm">{{ r['domain_name'] }}</span>{% endif %}</td>
  <td>{{ r['hostname'] or '' }}</td>
  <td>{{ r['user'] or '' }}</td>
  <td>{{ r['owner'] or '' }}</td>
  <td>{{ r['mac'] or '' }}</td>
  <td>{{ r['subnet'] or '' }}</td>
  <td>{{ r['vlan'] or '' }}</td>
  <td>{{ r['note'] or '' }}</td>
  <td class="act"><a href="/edit/{{ r['id'] }}">编辑</a>
  <a href="/delete/{{ r['id'] }}" class="d" onclick="return confirm('删除 {{ r['ip'] }}?')">删除</a></td>
</tr>
{% else %}
<tr><td colspan="11" class="empty">暂无记录</td></tr>
{% endfor %}
</tbody></table></div></body></html>"""

FORM = TEMPLATE + """
<h1>{{ '编辑' if row else '新增' }} IP</h1>
<form class="fc" method="post">
  <div class="row">
    <label><span>IP 地址 *</span><input name="ip" required value="{{ row['ip'] if row else '' }}"></label>
    <label><span>状态</span>
      <select name="status">
        {% for k,v in labels.items() %}
        <option value="{{ k }}" {{ 'selected' if row and row['status']==k }}>{{ v }}</option>
        {% endfor %}
      </select>
    </label>
    <label><span>域</span>
      <select name="domain_id">
        <option value="">— 未分类 —</option>
        {% for d in domains %}
        <option value="{{ d['id'] }}" {{ 'selected' if row and row['domain_id']==d['id'] }}>{{ d['name'] }}</option>
        {% endfor %}
      </select>
    </label>
  </div>
  <div class="row">
    <label><span>主机名</span><input name="hostname" value="{{ row['hostname'] if row else '' }}"></label>
    <label><span>MAC</span><input name="mac" value="{{ row['mac'] if row else '' }}"></label>
  </div>
  <div class="row">
    <label><span>使用者</span><input name="user" value="{{ row['user'] if row else '' }}"></label>
    <label><span>负责人</span><input name="owner" value="{{ row['owner'] if row else '' }}"></label>
  </div>
  <div class="row">
    <label><span>网段</span><input name="subnet" placeholder="192.168.1.0/24" value="{{ row['subnet'] if row else '' }}"></label>
    <label><span>VLAN</span><input name="vlan" value="{{ row['vlan'] if row else '' }}"></label>
  </div>
  <label><span>备注</span><textarea name="note" rows="3">{{ row['note'] if row else '' }}</textarea></label>
  <div class="btns">
    <button type="submit">保存</button>
    <a href="/">取消</a>
    {% if not domains %}<span class="hint">还没有域，<a href="/domains">先去创建</a></span>{% endif %}
  </div>
</form></div></body></html>"""

DOMAINS = TEMPLATE + """
<h1>域管理</h1>
<div class="tb">
  <a href="/">← 返回 IP 列表</a>
</div>

<form class="fc" method="post" action="/domains/add" style="margin-bottom:20px">
  <div class="row">
    <label><span>名称 *</span><input name="name" required placeholder="如：xx局、xx所、xxx部门"></label>
    <label><span>备注</span><input name="note"></label>
  </div>
  <div class="btns">
    <button type="submit">添加域</button>
  </div>
</form>

<table><thead><tr>
<th>名称</th><th>备注</th><th>IP 数量</th><th>操作</th>
</tr></thead><tbody>
{% for d in domains %}
<tr>
  <td><strong>{{ d['name'] }}</strong></td>
  <td>{{ d['note'] or '' }}</td>
  <td>{{ counts.get(d['id'], 0) }}</td>
  <td class="act">
    <a href="/domains/edit/{{ d['id'] }}">编辑</a>
    <a href="/domains/delete/{{ d['id'] }}" class="d"
       onclick="return confirm('删除域 {{ d['name'] }}？该域下的 IP 会变成未分类，不会被删除。')">删除</a>
  </td>
</tr>
{% else %}
<tr><td colspan="4" class="empty">暂无域，先在上方添加</td></tr>
{% endfor %}
</tbody></table></div></body></html>"""

DOMAIN_FORM = TEMPLATE + """
<h1>{{ '编辑' if domain else '新增' }} 域</h1>
<form class="fc" method="post">
  <label><span>名称 *</span><input name="name" required value="{{ domain['name'] if domain else '' }}" placeholder="如：xx局、xx所、xxx部门"></label>
  <label><span>备注</span><input name="note" value="{{ domain['note'] if domain else '' }}"></label>
  <div class="btns">
    <button type="submit">保存</button>
    <a href="/domains">取消</a>
  </div>
</form></div></body></html>"""

IMPORT_PAGE = TEMPLATE + """
<h1>导入数据</h1>
<div class="tb">
  <a href="/">← 返回 IP 列表</a>
</div>

{% if result %}
<div class="alert {{ 'err' if result.err else '' }}">{{ result.msg|safe }}</div>
{% endif %}

<form class="fc" method="post" enctype="multipart/form-data" style="max-width:600px">
  <h3>1. 准备 CSV 文件</h3>
  <p class="hint">
    请将 Excel 另存为 <strong>CSV（逗号分隔）</strong> 格式。<br>
    表头建议包含：<br>
    <code>IP, 状态, 域, 主机名, 使用者, 负责人, MAC, 网段, VLAN, 备注</code><br>
    状态列填中文（空闲/已用/保留/冲突/停用）或英文（free/used/reserved/conflict/deprecated）均可。<br>
    域如果不存在，导入时会自动创建。
  </p>
  <hr style="border:0;border-top:1px solid #eee;margin:20px 0">
  <h3>2. 选择文件</h3>
  <label><span>CSV 文件 *</span><input type="file" name="file" accept=".csv" required></label>
  <div class="btns">
    <button type="submit">开始导入</button>
    <a href="/">取消</a>
  </div>
</form>

<div class="fc" style="margin-top:20px;max-width:600px">
  <h3>下载模板</h3>
  <p class="hint">不确定格式？可以下载一个空的模板先看看。</p>
  <a href="/import/template" class="export" style="display:inline-block;padding:8px 16px;background:#17a2b8;color:#fff;text-decoration:none;border-radius:4px;font-size:14px">下载 CSV 模板</a>
</div>
</div></body></html>"""

@app.route("/")
def index():
    status = request.args.get("status", "")
    domain_id = request.args.get("domain_id", "")
    q = request.args.get("q", "").strip()
    conn = db()
    sql = """SELECT ips.*, domains.name AS domain_name
             FROM ips LEFT JOIN domains ON ips.domain_id = domains.id
             WHERE 1=1"""
    params = []
    if status:
        sql += " AND ips.status=?"; params.append(status)
    if domain_id:
        sql += " AND ips.domain_id=?"; params.append(domain_id)
    if q:
        sql += """ AND (ips.ip LIKE ? OR ips.hostname LIKE ? OR ips.owner LIKE ?
                        OR ips.user LIKE ? OR ips.note LIKE ?)"""
        params += [f"%{q}%"] * 5
    sql += " ORDER BY ips.ip"
    rows = conn.execute(sql, params).fetchall()

    counts = {"total": 0, "free": 0, "used": 0, "reserved": 0, "conflict": 0}
    for r in conn.execute("SELECT status, COUNT(*) c FROM ips GROUP BY status"):
        counts[r["status"]] = r["c"]
        counts["total"] += r["c"]

    domains = conn.execute("SELECT * FROM domains ORDER BY name").fetchall()
    domain_counts = {}
    for r in conn.execute("SELECT domain_id, COUNT(*) c FROM ips GROUP BY domain_id"):
        if r["domain_id"] is not None:
            domain_counts[r["domain_id"]] = r["c"]
    conn.close()

    return render_template_string(INDEX, rows=rows, status=status, domain_id=domain_id, q=q,
                                  counts=counts, labels=STATUS_LABEL,
                                  domains=domains, domain_counts=domain_counts)

@app.route("/add", methods=["GET", "POST"])
def add():
    conn = db()
    if request.method == "POST":
        f = request.form
        did = f.get("domain_id") or None
        try:
            conn.execute("""INSERT INTO ips
                            (ip,status,domain_id,hostname,mac,owner,user,subnet,vlan,note,updated)
                            VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                         (f["ip"], f["status"], did, f.get("hostname"), f.get("mac"),
                          f.get("owner"), f.get("user"), f.get("subnet"), f.get("vlan"),
                          f.get("note"), datetime.now().strftime("%Y-%m-%d %H:%M")))
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        finally:
            conn.close()
        return redirect(url_for("index"))
    domains = conn.execute("SELECT * FROM domains ORDER BY name").fetchall()
    conn.close()
    return render_template_string(FORM, row=None, labels=STATUS_LABEL, domains=domains)

@app.route("/edit/<int:rid>", methods=["GET", "POST"])
def edit(rid):
    conn = db()
    row = conn.execute("SELECT * FROM ips WHERE id=?", (rid,)).fetchone()
    if not row:
        conn.close()
        return redirect(url_for("index"))
    if request.method == "POST":
        f = request.form
        did = f.get("domain_id") or None
        try:
            conn.execute("""UPDATE ips SET ip=?,status=?,domain_id=?,hostname=?,mac=?,owner=?,user=?,
                            subnet=?,vlan=?,note=?,updated=? WHERE id=?""",
                         (f["ip"], f["status"], did, f.get("hostname"), f.get("mac"),
                          f.get("owner"), f.get("user"), f.get("subnet"), f.get("vlan"),
                          f.get("note"), datetime.now().strftime("%Y-%m-%d %H:%M"), rid))
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        finally:
            conn.close()
        return redirect(url_for("index"))
    domains = conn.execute("SELECT * FROM domains ORDER BY name").fetchall()
    conn.close()
    return render_template_string(FORM, row=row, labels=STATUS_LABEL, domains=domains)

@app.route("/delete/<int:rid>")
def delete(rid):
    conn = db()
    conn.execute("DELETE FROM ips WHERE id=?", (rid,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/domains")
def domains_list():
    conn = db()
    domains = conn.execute("SELECT * FROM domains ORDER BY name").fetchall()
    counts = {}
    for r in conn.execute("SELECT domain_id, COUNT(*) c FROM ips GROUP BY domain_id"):
        if r["domain_id"] is not None:
            counts[r["domain_id"]] = r["c"]
    conn.close()
    return render_template_string(DOMAINS, domains=domains, counts=counts)

@app.route("/domains/add", methods=["POST"])
def domain_add():
    name = request.form.get("name", "").strip()
    note = request.form.get("note", "").strip()
    if name:
        conn = db()
        try:
            conn.execute("INSERT INTO domains (name, note) VALUES (?, ?)", (name, note))
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        finally:
            conn.close()
    return redirect(url_for("domains_list"))

@app.route("/domains/edit/<int:did>", methods=["GET", "POST"])
def domain_edit(did):
    conn = db()
    domain = conn.execute("SELECT * FROM domains WHERE id=?", (did,)).fetchone()
    if not domain:
        conn.close()
        return redirect(url_for("domains_list"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        note = request.form.get("note", "").strip()
        if name:
            conn.execute("UPDATE domains SET name=?, note=? WHERE id=?", (name, note, did))
            conn.commit()
        conn.close()
        return redirect(url_for("domains_list"))
    conn.close()
    return render_template_string(DOMAIN_FORM, domain=domain)

@app.route("/domains/delete/<int:did>")
def domain_delete(did):
    conn = db()
    conn.execute("UPDATE ips SET domain_id=NULL WHERE domain_id=?", (did,))
    conn.execute("DELETE FROM domains WHERE id=?", (did,))
    conn.commit()
    conn.close()
    return redirect(url_for("domains_list"))

@app.route("/import", methods=["GET", "POST"])
def import_data():
    if request.method == "POST":
        f = request.files.get("file")
        if not f or f.filename == "":
            return render_template_string(IMPORT_PAGE, result={"err": True, "msg": "没有选择文件。"})
        try:
            content = f.read().decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(content))
            # 去除表头空格
            if reader.fieldnames:
                reader.fieldnames = [h.strip() for h in reader.fieldnames]

            conn = db()
            imported = 0
            updated = 0
            errors = []
            
            # 构建状态映射：中文/英文 -> 内部值
            status_map = {}
            for k, v in STATUS_LABEL.items():
                status_map[v] = k  # 中文 -> 英文
                status_map[k] = k  # 英文 -> 英文

            # 获取所有域
            domains = {r["name"]: r["id"] for r in conn.execute("SELECT id, name FROM domains").fetchall()}

            for row_num, row in enumerate(reader, start=2):
                ip = row.get("IP", "").strip()
                if not ip:
                    continue
                
                # 状态
                raw_status = row.get("状态", "空闲").strip()
                status = status_map.get(raw_status, "free")
                
                # 域
                domain_name = row.get("域", "").strip()
                domain_id = None
                if domain_name:
                    if domain_name in domains:
                        domain_id = domains[domain_name]
                    else:
                        c = conn.execute("INSERT INTO domains (name) VALUES (?)", (domain_name,))
                        conn.commit()
                        domain_id = c.lastrowid
                        domains[domain_name] = domain_id

                hostname = row.get("主机名", "").strip()
                user = row.get("使用者", "").strip()
                owner = row.get("负责人", "").strip()
                mac = row.get("MAC", "").strip()
                subnet = row.get("网段", "").strip()
                vlan = row.get("VLAN", "").strip()
                note = row.get("备注", "").strip()
                now = datetime.now().strftime("%Y-%m-%d %H:%M")

                # 检查是否存在
                existing = conn.execute("SELECT id FROM ips WHERE ip=?", (ip,)).fetchone()
                if existing:
                    conn.execute("""UPDATE ips SET status=?, domain_id=?, hostname=?, user=?, owner=?, mac=?, subnet=?, vlan=?, note=?, updated=? WHERE id=?""",
                                 (status, domain_id, hostname, user, owner, mac, subnet, vlan, note, now, existing["id"]))
                    updated += 1
                else:
                    conn.execute("""INSERT INTO ips (ip,status,domain_id,hostname,user,owner,mac,subnet,vlan,note,updated) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                                 (ip, status, domain_id, hostname, user, owner, mac, subnet, vlan, note, now))
                    imported += 1
            conn.commit()
            conn.close()
            
            msg = f"导入完成！新增 <strong>{imported}</strong> 条，更新 <strong>{updated}</strong> 条。"
            return render_template_string(IMPORT_PAGE, result={"err": False, "msg": msg})
        except Exception as e:
            return render_template_string(IMPORT_PAGE, result={"err": True, "msg": f"导入失败：{str(e)}"})
            
    return render_template_string(IMPORT_PAGE, result=None)

@app.route("/import/template")
def import_template():
    buf = io.StringIO()
    buf.write("\ufeff")
    w = csv.writer(buf)
    w.writerow(["IP", "状态", "域", "主机名", "使用者", "负责人", "MAC", "网段", "VLAN", "备注"])
    w.writerow(["192.168.1.10", "已用", "xx局", "web01", "张三", "李四", "aa:bb:cc:dd:ee:ff", "192.168.1.0/24", "10", "Web服务器"])
    buf.seek(0)
    return send_file(io.BytesIO(buf.read().encode("utf-8")),
                     mimetype="text/csv", as_attachment=True,
                     download_name="ipam_import_template.csv")

@app.route("/export")
def export():
    conn = db()
    rows = conn.execute("""SELECT ips.ip, ips.status, domains.name AS domain_name,
                                  ips.hostname, ips.user, ips.owner, ips.mac,
                                  ips.subnet, ips.vlan, ips.note, ips.updated
                           FROM ips LEFT JOIN domains ON ips.domain_id = domains.id
                           ORDER BY ips.ip""").fetchall()
    conn.close()
    buf = io.StringIO()
    buf.write("\ufeff")
    w = csv.writer(buf)
    w.writerow(["IP", "状态", "域", "主机名", "使用者", "负责人", "MAC", "网段", "VLAN", "备注", "更新时间"])
    for r in rows:
        w.writerow([r["ip"], STATUS_LABEL.get(r["status"], r["status"]), r["domain_name"],
                    r["hostname"], r["user"], r["owner"], r["mac"], r["subnet"],
                    r["vlan"], r["note"], r["updated"]])
    buf.seek(0)
    return send_file(io.BytesIO(buf.read().encode("utf-8")),
                     mimetype="text/csv", as_attachment=True,
                     download_name=f"ipam_{datetime.now():%Y%m%d}.csv")

if __name__ == "__main__":
    init_db()
    print("IPAM 已启动: http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)