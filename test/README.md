# MCPlanManager 测试套件

这个目录包含了 MCPlanManager 项目的完整测试套件，用于验证所有 MCP 工具的功能。

## 测试文件说明

### 1. `test_complete_suite.py` - 完整功能测试
测试所有 MCP 工具的基本功能，包括：
- 计划管理（初始化、状态查询）
- 任务管理（创建、启动、完成、跳过、失败）
- 依赖关系管理
- 可视化功能
- 上下文生成

### 2. `test_edge_cases.py` - 边界情况测试
测试系统的错误处理和边界条件，包括：
- 无效任务ID处理
- 空计划初始化
- 循环依赖检测
- 无效依赖处理
- 超长任务名称
- 特殊字符处理
- 状态一致性

### 3. `run_all_tests.py` - 测试运行器
自动运行所有测试套件并生成综合报告。

## 使用方法

### 前提条件
确保已安装必要的依赖：
```bash
pip install fastmcp
```

### 运行单个测试套件

#### 1. 运行完整功能测试
```bash
# SSE 模式（Docker）
python test/test_complete_suite.py --mode sse

# UVX 模式（本地）
python test/test_complete_suite.py --mode uvx
```

#### 2. 运行边界情况测试
```bash
# SSE 模式（Docker）
python test/test_edge_cases.py --mode sse

# UVX 模式（本地）
python test/test_edge_cases.py --mode uvx
```

### 运行所有测试

使用测试运行器一次性运行所有测试：
```bash
# SSE 模式（Docker）
python test/run_all_tests.py --mode sse

# UVX 模式（本地）
python test/run_all_tests.py --mode uvx
```

## 测试模式说明

### SSE 模式（推荐）
- 使用 Docker 容器运行 MCP 服务
- 通过 HTTP SSE 端点连接
- 需要先启动 Docker 服务：`docker-compose up -d`
- 测试地址：`http://localhost:8080/sse`

### UVX 模式
- 直接在本地运行 MCP 服务
- 通过 stdio 传输连接
- 使用 uvx 工具启动服务

## 测试报告

每个测试套件都会生成详细的测试报告，包括：
- 测试执行状态
- 成功/失败统计
- 详细的错误信息
- 性能指标（响应时间等）

## 故障排除

### 常见问题

1. **Docker 服务未启动**
   ```bash
   docker-compose up -d
   # 等待几秒钟让服务完全启动
   ```

2. **端口冲突**
   检查 8080 端口是否被占用：
   ```bash
   lsof -i :8080
   ```

3. **依赖缺失**
   确保安装了所有必要的依赖：
   ```bash
   pip install -r requirements.txt
   ```

4. **权限问题**
   确保测试文件有执行权限：
   ```bash
   chmod +x test/*.py
   ```

## 测试覆盖范围

### 已测试的工具
- ✅ `getPlanStatus` - 获取计划状态
- ✅ `initializePlan` - 初始化计划
- ✅ `getTaskList` - 获取任务列表
- ✅ `getExecutableTaskList` - 获取可执行任务
- ✅ `startNextTask` - 启动下一个任务
- ✅ `getCurrentTask` - 获取当前任务
- ✅ `completeTask` - 完成任务
- ✅ `addTask` - 添加任务
- ✅ `skipTask` - 跳过任务
- ✅ `failTask` - 标记任务失败
- ✅ `editDependencies` - 编辑依赖关系
- ✅ `visualizeDependencies` - 可视化依赖关系
- ✅ `generateContextPrompt` - 生成上下文提示

### 测试场景
- ✅ 正常功能流程
- ✅ 错误处理
- ✅ 边界条件
- ✅ 数据验证
- ✅ 状态一致性
- ✅ 特殊字符处理
- ✅ 依赖关系验证

## 贡献指南

如果需要添加新的测试：

1. 在相应的测试文件中添加测试方法
2. 确保测试方法有清晰的文档说明
3. 测试应该包含正面和负面测试用例
4. 更新此 README 文件的测试覆盖范围

## 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。 