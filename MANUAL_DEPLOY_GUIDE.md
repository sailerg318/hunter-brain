# 手动部署到 Streamlit Cloud - 完整指南

## 方法 1：直接在 Streamlit Cloud 编辑（最简单）

### 步骤 1：登录 Streamlit Cloud
1. 访问 https://share.streamlit.io/
2. 使用你的 GitHub 账号登录

### 步骤 2：找到你的应用
1. 在仪表板中找到 `nexustalentpool` 应用
2. 点击应用名称进入详情页

### 步骤 3：编辑文件
1. 点击右上角的 "⋮" (三个点)
2. 选择 "Settings"
3. 在左侧菜单选择 "Secrets" 或直接编辑文件

### 步骤 4：更新 app.py
1. 打开本地的 `/Users/gaoyijun/Desktop/source_code/hunter-brain/app.py`
2. 全选复制（Cmd+A, Cmd+C）
3. 在 Streamlit Cloud 的编辑器中粘贴
4. 点击 "Save" 保存

### 步骤 5：重启应用
1. 点击 "Reboot app"
2. 等待 2-3 分钟重新部署
3. 访问应用验证效果

---

## 方法 2：通过 GitHub 网页上传（推荐）

### 步骤 1：找到你的 GitHub 仓库
1. 登录 https://github.com
2. 找到部署 Streamlit 应用的仓库
   - 如果不确定，在 Streamlit Cloud 的 Settings 中查看 "Repository" 字段

### 步骤 2：上传优化后的文件

#### 2.1 上传 app.py
1. 在 GitHub 仓库中，找到 `app.py` 文件
2. 点击文件名打开
3. 点击右上角的 "✏️ Edit this file"
4. 删除所有内容
5. 打开本地 `/Users/gaoyijun/Desktop/source_code/hunter-brain/app.py`
6. 全选复制并粘贴到 GitHub 编辑器
7. 滚动到页面底部，填写提交信息：`性能优化：简化CSS渲染`
8. 点击 "Commit changes"

#### 2.2 上传 requirements.txt
1. 在仓库根目录，点击 "Add file" → "Create new file"
2. 文件名输入：`requirements.txt`
3. 复制以下内容：
```
streamlit>=1.32.0
pandas>=2.0.0
PyMuPDF>=1.23.0
python-docx>=1.1.0
requests>=2.31.0
```
4. 点击 "Commit new file"

#### 2.3 创建 .streamlit/config.toml
1. 点击 "Add file" → "Create new file"
2. 文件名输入：`.streamlit/config.toml`
3. 复制以下内容：
```toml
[server]
fileWatcherType = "auto"
maxUploadSize = 200
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false

[client]
showErrorDetails = true
toolbarMode = "minimal"

[runner]
fastReruns = true
magicEnabled = true

[theme]
base = "dark"
```
4. 点击 "Commit new file"

### 步骤 3：等待自动部署
1. GitHub 提交后，Streamlit Cloud 会自动检测更新
2. 在 Streamlit Cloud 仪表板中查看部署状态
3. 等待 2-3 分钟完成部署

---

## 方法 3：使用 Git 命令行（完整流程）

### 步骤 1：初始化 Git 仓库
```bash
cd /Users/gaoyijun/Desktop/source_code/hunter-brain
git init
git branch -M main
```

### 步骤 2：添加文件
```bash
git add app.py
git add requirements.txt
git add .streamlit/config.toml
git add deploy.sh
git add *.md
```

### 步骤 3：提交更改
```bash
git commit -m "性能优化：懒加载+缓存+简化CSS渲染"
```

### 步骤 4：连接到 GitHub 仓库

#### 如果你已经有仓库：
```bash
# 替换为你的仓库地址
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

#### 如果你还没有仓库：
1. 访问 https://github.com/new
2. 创建新仓库（例如：`nexus-talent-pool`）
3. 不要勾选任何初始化选项
4. 创建后，复制仓库 URL
5. 运行：
```bash
git remote add origin https://github.com/YOUR_USERNAME/nexus-talent-pool.git
git push -u origin main
```

### 步骤 5：在 Streamlit Cloud 中配置

#### 如果是新仓库：
1. 访问 https://share.streamlit.io/
2. 点击 "New app"
3. 选择你的 GitHub 仓库
4. 主文件路径：`app.py`
5. 点击 "Deploy"

#### 如果是现有应用：
- Streamlit Cloud 会自动检测 GitHub 更新并重新部署

---

## 方法 4：使用 VSCode 图形界面

### 步骤 1：在 VSCode 中打开文件夹
1. 打开 VSCode
2. 点击 "文件" → "打开文件夹"
3. 选择 `/Users/gaoyijun/Desktop/source_code/hunter-brain`

### 步骤 2：初始化 Git
1. 点击左侧边栏的 "源代码管理" 图标（或按 Ctrl+Shift+G）
2. 点击 "初始化仓库" 按钮

### 步骤 3：暂存和提交
1. 在 "更改" 列表中，点击 "+" 暂存所有文件
2. 在顶部的消息框中输入：`性能优化：简化CSS渲染`
3. 点击 "✓ 提交" 按钮

### 步骤 4：推送到 GitHub
1. 点击 "..." → "远程" → "添加远程存储库"
2. 输入你的 GitHub 仓库 URL
3. 点击 "..." → "推送"
4. 选择 "origin" 和 "main" 分支

---

## 验证部署是否成功

### 1. 检查 Streamlit Cloud 状态
1. 登录 https://share.streamlit.io/
2. 找到你的应用
3. 查看状态是否为 "Running"（绿色）

### 2. 测试加载速度
1. 清除浏览器缓存（Cmd+Shift+Delete）
2. 访问你的应用 URL
3. 使用浏览器开发者工具（F12）查看加载时间
4. 应该看到明显的速度提升

### 3. 查看日志
1. 在 Streamlit Cloud 中点击 "Manage app"
2. 选择 "Logs" 标签
3. 检查是否有错误信息

---

## 常见问题

### Q: 找不到 GitHub 仓库地址
**A**: 在 Streamlit Cloud 中：
1. 找到你的应用
2. 点击 "Settings"
3. 查看 "Repository" 字段

### Q: 推送时要求输入用户名和密码
**A**: GitHub 已不支持密码认证，需要使用 Personal Access Token：
1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 勾选 "repo" 权限
4. 生成后复制 token
5. 在命令行中使用 token 作为密码

### Q: 部署后应用报错
**A**: 检查以下几点：
1. `requirements.txt` 是否正确
2. `.streamlit/config.toml` 是否存在
3. 查看 Streamlit Cloud 的日志

---

## 推荐方案

**最简单**：方法 1（直接在 Streamlit Cloud 编辑）  
**最可靠**：方法 2（通过 GitHub 网页上传）  
**最专业**：方法 3（使用 Git 命令行）  
**最友好**：方法 4（使用 VSCode 图形界面）

选择最适合你的方法即可！
