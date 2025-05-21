# 基础爬取功能 WebUI 开发设计文档

## 1. 开发目标

实现一个基于 Gradio 的 WebUI，支持用户通过图形化操作完成动漫图像数据的爬取、处理和导出。目标是提供一个简单易用的界面，满足以下需求：
- 数据源选择。
- 爬取配置。
- 数据处理。
- 导出设置。
- **作者信息提取与存储**。
- 任务状态显示。

## 2. 技术栈

### 2.1 前端
- **框架**：Gradio
- **特点**：
  - 快速构建交互式 Web 界面。
  - 支持 Python 原生开发，无需额外的前端代码。

### 2.2 后端
- **实现方式**：直接在 Gradio 中封装功能为 Python 函数。
- **特点**：
  - 简化开发流程，无需额外的后端框架。
  - 函数直接调用 waifuc 提供的功能模块。

### 2.3 数据存储
- **文件存储**：本地文件系统
- **任务状态存储**：内存存储（仅限当前会话）
- **作者信息存储**：将作者信息存储在每个爬取项的 `meta` 字段中，并在导出时保存到元数据文件（如 JSON 或文本文件）。

## 3. 模块设计

### 3.1 数据源选择模块
- **功能**：
  - 列出支持的数据源（如 Danbooru、Pixiv、Zerochan）。
  - 提供单选按钮或下拉菜单供用户选择。
- **实现**：
  - 使用 Gradio 的 `Dropdown` 组件。
  - 数据源列表通过 waifuc 的 `source` 模块动态加载。

### 3.2 爬取配置模块
- **功能**：
  - 输入关键词或标签。
  - 设置爬取数量。
  - 选择图像尺寸（如 `full`、`large`）。
  - 开启/关闭严格模式。
- **实现**：
  - 使用 Gradio 的 `Textbox`、`Slider` 和 `Checkbox` 组件。
  - 调用封装的爬取函数，直接使用 waifuc 的数据源模块。

### 3.3 数据处理模块
- **功能**：
  - 列出 waifuc 提供的 `Action` 模块。
  - 提供模块的启用/禁用开关。
- **实现**：
  - 使用 Gradio 的 `CheckboxGroup` 组件。
  - 动态加载 waifuc 的 `Action` 模块，并将用户选择的模块传递给爬取流程。

### 3.4 作者信息提取模块
- **功能**：
  - 自动从支持的数据源中提取作者信息。
  - 支持不登录提取作者信息的数据源包括：
    - Danbooru
    - Zerochan
    - Safebooru
    - Gelbooru
  - 将作者信息存储在每个爬取项的 `meta` 字段中。
- **实现**：
  - 在 `start_crawl` 函数中扩展逻辑，提取作者信息并打印到控制台。
  - 在导出时，将作者信息保存到元数据文件（如 JSON 或文本文件）。

### 3.5 导出设置模块
- **功能**：
  - 设置导出路径。
  - 选择是否保存元数据。
  - 支持多种导出格式（如 `SaveExporter`、`TextualInversionExporter`）。
  - **保存作者信息到元数据文件**。
- **实现**：
  - 使用 Gradio 的 `Textbox` 和 `Dropdown` 组件。
  - 调用封装的导出函数，直接使用 waifuc 的导出模块。

### 3.6 任务状态模块
- **功能**：
  - 显示当前任务的进度和状态。
- **实现**：
  - 使用 Gradio 的 `Label` 和 `Progress` 组件。
  - 通过全局变量或内存存储更新任务状态。

## 4. 函数设计

### 4.1 数据源选择函数
- **函数名**：`get_sources`
- **功能**：返回支持的数据源列表。
- **实现**：
  ```python
  from waifuc.source import DanbooruSource, PixivSearchSource, ZerochanSource

  def get_sources():
      return ["Danbooru", "Pixiv", "Zerochan"]
  ```

### 4.2 爬取任务函数
- **函数名**：`start_crawl`
- **功能**：根据用户配置启动爬取任务，并提取作者信息。
- **实现**：
  ```python
  from waifuc.source import DanbooruSource, ZerochanSource

  def start_crawl(source_name, tags, limit, size, strict):
      if source_name == "Danbooru":
          source = DanbooruSource(tags=tags, limit=limit, min_size=size)
      elif source_name == "Zerochan":
          source = ZerochanSource(tags, select=size, strict=strict)
      else:
          raise ValueError("Unsupported source")
      
      # 提取作者信息
      for item in source:
          author = item.meta.get("author", "Unknown")
          print(f"Image URL: {item.url}, Author: {author}")
      
      return source
  ```

### 4.3 数据处理函数
- **函数名**：`apply_actions`
- **功能**：根据用户选择的 `Action` 模块处理数据。
- **实现**：
  ```python
  from waifuc.action import NoMonochromeAction, FilterSimilarAction

  def apply_actions(source, actions):
      if "NoMonochrome" in actions:
          source = source.attach(NoMonochromeAction())
      if "FilterSimilar" in actions:
          source = source.attach(FilterSimilarAction())
      return source
  ```

### 4.4 导出函数
- **函数名**：`export_data`
- **功能**：导出处理后的数据，并保存作者信息。
- **实现**：
  ```python
  from waifuc.export import SaveExporter

  def export_data(source, output_dir, save_meta):
      exporter = SaveExporter(output_dir=output_dir, save_meta=save_meta)
      for item in source:
          exporter.export_item(item)
          if save_meta:
              # 保存作者信息到元数据文件
              with open(f"{output_dir}/metadata.json", "a") as meta_file:
                  meta_file.write(
                      f"{item.url}: Author: {item.meta.get('author', 'Unknown')}\n"
                  )
  ```

## 5. 开发计划

### 5.1 时间表
| 时间节点       | 任务内容                          |
|----------------|-----------------------------------|
| 第 1 周        | 完成 Gradio 界面搭建和基本页面布局。 |
| 第 2 周        | 实现数据源选择和爬取配置功能。    |
| 第 3 周        | 实现数据处理和导出设置功能。      |
| 第 4 周        | 实现任务状态模块，测试与优化。    |
| 第 5 周        | 添加作者信息提取与存储功能。      |

### 5.2 任务分解
1. **前端开发**：
   - 使用 Gradio 构建界面。
   - 实现各模块的交互逻辑。

2. **功能封装**：
   - 将 waifuc 的功能模块封装为独立函数。
   - 集成到 Gradio 界面中。

3. **测试与优化**：
   - 编写单元测试和集成测试。
   - 优化界面交互和性能。

## 6. 预期成果

- 一个基于 Gradio 的 WebUI，支持用户通过图形化界面完成动漫图像数据的爬取、处理和导出。
- 提供详细的用户手册和开发文档，便于用户和开发者使用和扩展。
- **支持作者信息的提取与存储，方便用户管理数据来源信息**。
