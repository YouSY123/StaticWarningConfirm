# c++静态分析告警确认
### 运行环境配置
python环境见`requirements.txt`

安装 codeql cli 并配置环境变量

### 使用方法
1. 填写`config.py`中的大模型api或者本地模型信息
2. 运行`process.py`测试agent框架(目前工具仅使用cmd)

    2.1 按照注释填写main里参数信息 

    2.2 运行命令：
    
    ```cmd
    python process.py
    ```
    
    2.3 client输出的所有信息默认在`log/log.txt`，可以在`config.py`修改


3. 运行tools.py进行工具测试(目前为CodeQL)

### TODO

1. 在数据集上测试，确定conditions和具体确认方式
2. 构建具体的CodeQL queries
3. 优化大模型prompt等内容