# 基础爬取功能 WebUI 设计文档

## 1. 产品目标

提供一个简单直观的 Web 界面，用户可以通过图形化操作完成动漫图像数据的爬取、处理和导出。目标用户包括：
- 动漫爱好者：快速收集角色图像。
- 数据科学家：构建小规模训练数据集。

## 2. 功能需求

### 2.1 核心功能
1. **数据源选择**：
   - 支持选择单一数据源（如 Danbooru、Pixiv、Zerochan）。
   - 不需要登录功能（如 waifuc 的部分数据源支持匿名访问）。

2. **爬取配置**：
   - 输入关键词或标签。
   - 设置爬取数量。
   - 选择图像尺寸（如 `full`、`large`）。
   - 支持严格模式（如 Zerochan 的 `strict` 参数）。

3. **数据处理**：
   - 提供可选的图像处理操作（如去单色、去重复、裁剪）。
   - 动态加载 waifuc 的 `Action` 模块（如 `NoMonochromeAction`、`FilterSimilarAction` 等）。

4. **导出设置**：
   - 设置导出路径。
   - 选择是否保存元数据（如 JSON 文件）。
   - 支持多种导出格式（如 `SaveExporter`、`TextualInversionExporter`）。

5. **任务状态**：
   - 显示当前任务的进度和状态。

## 3. 界面设计

### 3.1 主界面布局
- **顶部区域**：
  - 包含标题和简单的说明文字。
- **主内容区域**：
  - 分为四个部分：
    1. 数据源选择。
    2. 爬取配置。
    3. 数据处理。
    4. 导出设置和任务状态。

### 3.2 界面原型

#### 数据源选择界面
- **功能**：
  - 列出支持的数据源（如 Danbooru、Pixiv、Zerochan）。
- **布局**：
  - 单选按钮或下拉菜单，供用户选择数据源。

#### 爬取配置界面
- **功能**：
  - 输入关键词或标签。
  - 设置爬取数量和图像尺寸。
  - 开启/关闭严格模式。
- **布局**：
  - 表单式布局，包含输入框、下拉菜单和开关按钮。

#### 数据处理界面
- **功能**：
  - 列出 waifuc 提供的 `Action` 模块。
  - 提供模块的启用/禁用开关。
- **布局**：
  - 模块列表，每个模块对应一个复选框。

#### 导出设置和任务状态界面
- **功能**：
  - 设置导出路径。
  - 选择是否保存元数据。
  - 显示任务的进度条和状态信息。
- **布局**：
  - 表单式布局，包含路径输入框和复选框。
  - 简单的进度条和状态文本。

## 4. 用户数据收集

### 4.1 必要数据
1. **数据源信息**：
   - 用户选择的数据源。

2. **爬取配置**：
   - 关键词或标签。
   - 爬取数量。
   - 图像尺寸。
   - 严格模式开关。

3. **数据处理**：
   - 启用的 `Action` 模块及其配置。

4. **导出设置**：
   - 导出路径。
   - 是否保存元数据。

### 4.2 数据存储
- **临时存储**：
  - 用户的爬取配置和任务状态仅在当前会话中保存。
- **永久存储**：
  - 不保存用户的历史记录。

## 5. 技术设计

### 5.1 前端技术栈
- **框架**：Gradio

### 5.2 后端技术栈
- **框架**：FastAPI
- **文件存储**：本地文件系统

### 5.3 API 设计
- **数据源管理**：
  - `GET /api/sources`：获取支持的数据源列表。
- **爬取任务**：
  - `POST /api/tasks`：创建爬取任务。
  - `GET /api/tasks/status`：获取任务状态。
- **数据处理**：
  - `GET /api/actions`：获取可用的 `Action` 模块。
  - `POST /api/actions`：配置 `Action` 模块。
- **导出设置**：
  - `POST /api/export`：导出数据。

## 6. 开发计划

### 6.1 时间表
| 时间节点       | 任务内容                          |
|----------------|-----------------------------------|
| 第 1 周        | 完成 Gradio 界面搭建和基本页面布局。 |
| 第 2 周        | 实现数据源选择和爬取配置功能。    |
| 第 3 周        | 实现数据处理和导出设置功能。      |
| 第 4 周        | 测试与优化，发布初版。           |

## 7. 预期成果

- 一个基于 Gradio 的简洁 WebUI，支持用户通过图形化界面完成动漫图像数据的爬取、处理和导出。
