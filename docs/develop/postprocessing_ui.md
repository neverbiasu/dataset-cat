# 数据后处理 UI 开发设计文档

## 1. 开发目标

-   在现有的 Gradio WebUI 中新增一个“数据后处理”标签页。
-   该模块专注于对用户提供的本地图像（通过目录指定或直接上传）应用一系列 `waifuc` Actions。
-   实现动态加载、选择和配置 `waifuc` Actions 的机制。
-   提供清晰的进度反馈和处理结果。
-   确保代码模块化，易于维护和扩展新的 Actions。

## 2. 技术栈

-   **UI 框架**: Gradio
-   **核心处理库**: `waifuc` (特别是 `waifuc.source.LocalSource`, `waifuc.action.BaseAction` 的子类, `waifuc.export.SaveExporter`)
-   **图像处理库**: Pillow (由 `waifuc` 间接使用)
-   **编程语言**: Python 3.x
-   **辅助库**: `os`, `inspect` (用于动态发现和解析 Actions)

## 3. 模块设计

### 3.1 UI 模块 (`postprocessing_tab.py` 或集成到现有 WebUI 主文件)

-   **功能**: 构建 Gradio 界面，处理用户输入和交互，调用后端处理逻辑。
-   **主要组件**:
    -   `gr.Tabs` 中的一个 `gr.TabItem(label="数据后处理")`。
    -   输入区: `gr.Radio` (选择目录或上传), `gr.Textbox` (输入目录), `gr.Files` (上传)。
    -   Action 选择区: `gr.CheckboxGroup` (列出 Actions)。
    -   Action 参数配置区: 动态生成的 `gr.Column` 或 `gr.Group`，包含针对每个选定 Action 的参数输入控件。
    -   输出区: `gr.Textbox` (输出目录)。
    -   控制与反馈区: `gr.Button` ("开始处理"), `gr.Progress`, `gr.Textbox` (日志)。

### 3.2 Action 管理模块 (`action_manager.py` - 可选，或逻辑内嵌)

-   **功能**:
    -   动态发现项目中所有可用的 `waifuc.action.BaseAction` 子类。
    -   提取每个 Action 的名称、描述 (来自 docstring) 及其构造函数参数 (名称、类型、默认值)。
-   **主要函数**:
    -   `get_available_actions() -> dict[str, dict]`: 返回一个字典，键为 Action 类名，值为包含其元信息（如描述、参数定义）的字典。
        ```python
        # 示例返回结构
        # {
        #     "ResizeAction": {
        #         "doc": "Resizes images to a target size.",
        #         "params": {
        #             "width": {"type": int, "default": 512, "required": True},
        #             "height": {"type": int, "default": 512, "required": True},
        #         }
        #     }, ...
        # }
        ```

### 3.3 后端处理逻辑模块 (`postprocessing_core.py` - 可选，或逻辑内嵌)

-   **功能**: 接收来自 UI 的配置，执行图像的后处理流程。
-   **主要函数**:
    -   `run_postprocessing(input_data: Union[str, list], actions_config: list[dict], output_dir: str, progress: gr.Progress) -> tuple[str, str]`:
        -   `input_data`: 若为字符串，则是输入目录路径；若为列表，则是 `gradio.Files` 返回的临时文件对象列表。
        -   `actions_config`: 用户选择的 Actions 及其参数配置列表，例如:
            ```python
            # [
            #  {'name': 'ResizeAction', 'params': {'width': 1024, 'height': 768}},
            #  {'name': 'GrayscaleAction', 'params': {}}
            # ]
            ```
        -   `output_dir`: 处理后图像的保存目录。
        -   `progress`: Gradio 进度条对象，用于更新进度。
        -   返回: `(success_message, error_message)`

## 4. 函数设计 (关键逻辑)

### 4.1 `get_available_actions()` (在 Action 管理模块)

-   使用 `importlib` 和 `inspect` 遍历 `waifuc.action` 模块（或其他预定义位置）。
-   查找所有继承自 `waifuc.action.BaseAction` 的类。
-   对每个找到的类：
    -   获取类名。
    -   获取 `__doc__` 作为描述。
    -   使用 `inspect.signature(ActionClass.__init__)` 获取构造函数参数。
    -   解析参数的名称、注解 (类型提示) 和默认值。

### 4.2 UI 更新函数 (在 UI 模块)

-   `update_action_params_ui(selected_action_names: list[str]) -> list[gr.components.IOComponent]`:
    -   当 `gr.CheckboxGroup` (Action 选择) 的值改变时触发。
    -   根据 `selected_action_names` 和 `get_available_actions()` 的结果，动态创建或更新 Gradio 参数输入组件。
    -   返回一个 Gradio 组件列表，用于更新参数配置区域的 UI。

### 4.3 `run_postprocessing()` (在后端处理逻辑模块)

1.  **初始化数据源**:
    -   如果 `input_data` 是目录路径: `source = LocalSource(input_data)`
    -   如果 `input_data` 是上传的文件列表:
        -   需要将 Gradio 的 `tempfile._TemporaryFileWrapper` 对象列表转换为 `PIL.Image` 对象列表，然后构建一个临时的 `waifuc.source.Source` 子类或直接迭代这些 `ImageItem`。一个简单的方式是先将上传的文件保存到临时目录，然后使用 `LocalSource`。或者，创建一个自定义的 `Source` 来直接处理内存中的 `PIL.Image` 对象列表。
        ```python
        # 伪代码 для处理上传文件:
        # image_items = []
        # for file_wrapper in uploaded_files:
        #     pil_img = Image.open(file_wrapper.name)
        #     # 注意：file_wrapper.name 是临时文件路径
        #     # 需要构建 ImageItem，可能需要模拟元数据
        #     image_items.append(ImageItem.load_from_image(pil_img, {'filename': os.path.basename(file_wrapper.name)})) 
        # source = FromListSource(image_items) # FromListSource 是一个假设的自定义Source
        ```
2.  **实例化并附加 Actions**:
    -   遍历 `actions_config`。
    -   对每个 Action 配置：
        -   动态找到对应的 Action 类 (例如，通过 `getattr(waifuc.action, action_name)` 或从预加载的字典中获取)。
        -   使用 `action_config['params']` 实例化 Action。
        -   `source = source.attach(action_instance)`。
3.  **执行导出**:
    -   确保 `output_dir` 存在: `os.makedirs(output_dir, exist_ok=True)`。
    -   `exporter = SaveExporter(output_dir)`。
    -   迭代 `source`，并通过 `exporter` 导出每个 `item`。
    -   在迭代过程中更新 `progress` 对象。
4.  **错误处理与日志记录**:
    -   使用 `try-except` 捕获处理过程中的异常。
    -   收集成功和失败的信息，返回给 UI。

## 5. 数据流

1.  **UI**: 用户选择输入源（目录/上传文件），选择 Actions，配置参数，指定输出目录，点击“开始处理”。
2.  **UI -> 后端**: 将输入路径/文件列表、Action 配置列表、输出目录路径传递给 `run_postprocessing` 函数。
3.  **后端 `run_postprocessing`**:
    a.  根据输入类型创建 `waifuc.source.Source` 实例。
    b.  根据 Action 配置列表，动态实例化选择的 Actions 并依次附加到 `Source` 上。
    c.  创建 `waifuc.export.SaveExporter` 实例，指向输出目录。
    d.  迭代处理后的 `Source`，每个 `ImageItem` 经过所有 Action 处理后，由 `SaveExporter` 保存。
    e.  处理过程中，通过 Gradio 的 `progress` 对象更新 UI 进度条。
4.  **后端 -> UI**: `run_postprocessing` 函数返回处理结果的摘要信息（成功、失败、错误），UI 将其显示在日志区域。

## 6. 开发计划

1.  **环境与基础 (0.5 天)**: 确认 `waifuc` 版本，搭建基础 Gradio 标签页结构。
2.  **Action 发现与展示 (1 天)**: 实现 `get_available_actions`，并在 UI 中通过 `gr.CheckboxGroup` 展示。
3.  **动态参数 UI (1.5 天)**: 实现 `update_action_params_ui`，根据选择的 Actions 动态生成参数输入界面。
4.  **核心处理逻辑 - 目录输入 (1.5 天)**: 实现 `run_postprocessing` 对目录输入的基本处理流程（加载、Action 应用、导出）。
5.  **核心处理逻辑 - 文件上传 (1 天)**: 扩展 `run_postprocessing` 以支持处理直接上传的文件。
6.  **集成与进度反馈 (1 天)**: 将 UI 与后端逻辑完全连接，实现进度条更新和日志输出。
7.  **测试与优化 (2 天)**: 对多种 Actions、参数组合、大量文件进行测试，进行错误处理优化和用户体验改进。

## 7. 预期成果

-   一个功能稳定、可扩展的 Gradio 标签页，用于图像数据集的后处理。
-   支持动态加载和配置 `waifuc` Actions。
-   提供清晰的用户交互和处理反馈。
-   代码结构清晰，遵循项目开发规范，易于后续维护和功能增强。
