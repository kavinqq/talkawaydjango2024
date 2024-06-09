# 使用 Python 3.11.6 官方映像
FROM python:3.11.6

# 設定容器內的工作目錄
WORKDIR /app

# 複製 requirements.txt 到容器內
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式的其餘部分到容器內
COPY . .

# 複製 entrypoint.sh 並設定執行權限
COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

# 定義容器啟動後執行的命令
ENTRYPOINT ["entrypoint.sh"]