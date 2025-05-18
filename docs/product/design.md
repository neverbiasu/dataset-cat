# Dataset Creator - 设计文档

## 1. 项目概述

`dataset-creator` 是一个 Python 包工具，旨在简化从各种在线资源（如图像板、艺术作品网站）创建图像数据集的过程。用户可以通过命令行界面指定角色名、游戏名、作者名、网站来源、数量等参数来抓取、处理和组织图像。该工具的核心是利用 `waifuc` 库的强大功能，并提供易于使用的接口。

## 2. 核心目标

*   **易用性**: 提供简单的命令行界面，方便用户快速上手。
*   **可扩展性**: 方便添加新的图像来源和图像处理步骤。
*   **灵活性**: 支持通过标签、数量等多种参数自定义数据集的创建过程。
*   **集成性**: 基于现有成熟的 Python 库，特别是 `waifuc`。

## 3. 核心 Python 库及用途

### 3.1. 数据集下载 (抓取)

*   **核心库**: `waifuc`
    *   **用途**: `waifuc` 是本项目下载图像的核心库。它提供了对多种流行图像网站的抽象数据源 (Sources)，例如 Danbooru, Pixiv, Gelbooru, Zerochan 等，特别适合动漫风格图像。
    *   **用法**:
        *   通过 `waifuc.source` 模块中的具体类 (如 `DanbooruSource`, `PixivSearchSource`) 来实例化数据源。
        *   数据源通常接收标签列表 (tags) 作为参数，用于搜索特定图像。
        *   支持配置特定于源的参数，如最低分数、评级等。
        *   示例: `source = DanbooruSource(['character_name', 'game_name', 'score:>=20', 'rating:s'])`

*   **补充抓取工具**:
    *   **库**: `gallery-dl`
        *   **用途**: 一个非常强大的命令行图像下载工具，支持数百个图像和视频网站。当 `waifuc` 没有特定网站的 Source 时，`gallery-dl` 是一个极佳的替代方案。
        *   **用法**: 通常作为命令行工具使用 (`gallery-dl <url>`)。在 Python 中可以通过 `subprocess` 模块调用。下载后的文件可以被后续的 `waifuc` Actions 或其他处理脚本处理。
        *   **整合策略**: 可以编写一个 `waifuc` Source 或辅助脚本来包装 `gallery-dl` 的调用，使其能够融入 `dataset-creator` 的工作流。
    *   **库**: `Requests`
        *   **用途**: 用于发送 HTTP 请求，从任意 URL 下载原始网页内容或文件。是构建自定义网络爬虫的基础。
        *   **用法**: `response = requests.get(url)` 获取页面，`response.content` 获取图片等二进制内容。
    *   **库**: `Beautiful Soup 4 (bs4)` 或 `lxml`
        *   **用途**: 用于解析 HTML 和 XML 文档，从中提取所需信息，如图片链接、元数据等。通常与 `Requests` 配合使用。
        *   **用法**: `soup = BeautifulSoup(html_content, 'html.parser')`，然后使用 `soup.find_all('img')` 等方法查找元素。
    *   **库**: `Scrapy`
        *   **用途**: 一个功能强大的 Python 爬虫框架，用于构建可扩展的网络爬虫。适用于需要抓取大量数据、处理复杂网站结构或需要异步操作的场景。
        *   **用法**: 定义 Scrapy Spiders 来指定如何爬取特定网站和提取数据。

    **整合策略 (通用)**: 对于 `waifuc` 不支持的网站，可以使用 `gallery-dl`、`Requests` + `Beautiful Soup` 或 `Scrapy` 编写自定义爬虫脚本。下载的图片可以作为本地文件源输入到后续的处理流程中，或者将自定义爬虫逻辑封装成新的 `waifuc` Source。

### 3.2. 数据集处理

*   **核心框架**: `waifuc` (Actions)
    *   **用途**: `waifuc` 的 Actions 系统用于在图像下载后、导出前对图像进行各种处理，形成处理流水线。
    *   **用法**:
        *   **裁剪**: 使用 `waifuc.action.ThreeStageSplitAction` 可以将图像裁剪为头部、半身和全身等部分。
        *   **标签过滤/修改**: `waifuc.action.TagFilterAction`, `ModeConvertAction` 等。
        *   **自定义处理**: 可以通过继承 `waifuc.action.BaseAction` 或 `waifuc.action.ProcessAction` 来创建自定义处理步骤，集成下述图像处理库的功能。

*   **通用图像处理库**:
    *   **库**: `Pillow` (PIL Fork)
        *   **用途**: Python 平台事实上的图像处理标准库。
        *   **用法**: `from PIL import Image; img = Image.open('image.jpg'); img_resized = img.resize((width, height))`。
    *   **库**: `OpenCV (cv2)`
        *   **用途**: 流行的计算机视觉和图像处理库，功能广泛。
        *   **用法**: `import cv2; img = cv2.imread('image.jpg'); gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)`。
    *   **库**: `scikit-image`
        *   **用途**: 专注于科学图像分析的 Python 库。
        *   **用法**: `from skimage import io, color; img = io.imread('image.jpg'); gray_img = color.rgb2gray(img)`。

*   **自动打标与描述生成 (Tagging and Captioning)**:
    *   **库/工具**: `TorchDeepDanbooru` (或类似的基于深度学习的 Danbooru 风格标签器)
        *   **用途**: 自动为动漫风格图像生成 Danbooru 标签。这对于后续的图像检索、筛选或作为模型训练的辅助信息非常有用。
        *   **用法**: 通常需要加载预训练模型，然后对图像进行推理。可以封装为自定义 `waifuc` Action。
        *   **示例**: `AUTOMATIC1111/TorchDeepDanbooru` 是一个流行的实现。
    *   **库/工具**: `joycaption` (或类似的图像描述生成工具)
        *   **用途**: 为图像生成自然语言描述 (captions)。这对于训练需要文本描述的图像模型（如 Stable Diffusion 的 prompt 理解）至关重要。
        *   **用法**: 通常也涉及预训练模型。可以封装为自定义 `waifuc` Action。
    *   **库/工具**: `BLIP`, `CLIP Interrogator` (概念)
        *   **用途**: 更高级的图像理解工具，`BLIP` 可以生成详细描述，`CLIP Interrogator` (常用于 Stable Diffusion WebUI) 可以根据图像内容反推可能的提示词/标签。
        *   **用法**: 这些通常是更复杂的模型，但其核心思想（图像到文本/标签）可以指导自定义 Action 的开发。

    **整合策略**: 将这些打标和描述工具封装成 `waifuc.action.ProcessAction` 的子类。Action 接收图像数据，调用相应的打标/描述模型，并将结果（标签、描述文本）添加到图像的元数据 (`item.meta`) 中，以便后续使用或导出。

*   **专用或高级图像处理与后期处理**:
    *   **(可选) 库**: `imgutils`
        *   **用途**: 提供了许多预封装的、针对动漫等特定风格图像的深度学习工具，如超分辨率、人脸检测、背景去除等。
    *   **(可选) 库**: `onnxruntime`
        *   **用途**: ONNX 模型推理引擎。
    *   **概念/工具集**: `Stable Diffusion WebUI Postprocessing for Training` (来自 `stable-diffusion-webui/extensions-builtin/postprocessing-for-training/`)
        *   **用途**: 这类工具集通常包含一系列用于训练数据准备的脚本，例如图像的批量缩放、裁剪、格式转换、生成文本-图像对的元数据文件等。
        *   **整合策略**: 可以借鉴这些工具集中的具体处理逻辑，并将其实现为 `dataset-creator` 中的自定义 `waifuc` Actions，或者作为独立的后处理脚本在 `waifuc` 流水线完成后运行。

### 3.3. 数据集发布 (本地保存与组织)

*   **库**: `waifuc` (Exporters)
    *   **用途**: `waifuc` 的 Exporters 负责将处理流水线中的最终图像数据保存到指定位置。
    *   **用法**:
        *   **本地保存**: `waifuc.export.SaveExporter` 是最常用的导出器，它将图像保存到本地文件系统，并可以根据元数据生成文件名和目录结构。
            *   示例: `exporter = SaveExporter('output_directory/subdir_{tag_type}_{tag}')`
        *   `SaveExporter` 可以配置输出路径、文件名模板等。

*   **库**: `os`, `shutil` (Python 标准库)
    *   **用途**: 用于创建输出目录、管理文件路径等辅助文件系统操作。
    *   **用法**: `os.makedirs()`, `os.path.join()` 等。

### 3.4. 命令行界面与配置

*   **库**: `argparse` (Python 标准库)
    *   **用途**: 用于创建用户友好的命令行界面，解析用户输入的参数。
    *   **用法**: 定义各种命令行参数，如 `--website`, `--character_name`, `--quantity`, `--output_dir` 等。

*   **库**: `logging` (Python 标准库)
    *   **用途**: 提供日志记录功能，方便用户了解程序运行状态和调试错误。
    *   **用法**: 配置日志级别、格式，输出到控制台或文件。

## 4. 工作流程

1.  **参数解析**: `dataset_creator.cli.main()` 函数使用 `argparse` 解析用户通过命令行传入的参数（如网站、标签、数量、输出目录等）。
2.  **数据源选择与实例化**: 根据用户指定的 `--website` 参数，从 `AVAILABLE_SOURCES` 映射中选择并实例化对应的 `waifuc` Source 类。将用户提供的角色名、游戏名、作者名及其他标签传递给 Source。
3.  **附加处理动作**: 根据用户参数（如 `--crop`），将相应的 `waifuc` Action (如 `ThreeStageSplitAction`) 附加到数据源实例上，形成处理流水线。
4.  **导出器配置**: 实例化 `SaveExporter`，并指定输出目录。
5.  **数据抓取与处理循环**:
    *   程序迭代 `waifuc` Source 实例。在每次迭代中，`waifuc` 会：
        *   从源网站抓取原始图像数据和元数据。
        *   依次执行附加的 Actions（例如，裁剪）。
    *   对于每个处理后的图像项 (item)，调用 `SaveExporter.export_item(item)` 进行保存。
    *   循环直到达到用户指定的 `--quantity` 或源中没有更多图像。
6.  **日志与反馈**: 在整个过程中，使用 `logging` 模块向用户提供进度信息、警告和错误。

## 5. 数据集输出结构

默认情况下，`SaveExporter` 会将图像保存在指定的输出目录中。可以考虑通过 `SaveExporter` 的参数或自定义导出逻辑来组织输出，例如：

```
<output_dir>/
├── <website_name>/
│   ├── <character_name_or_primary_tag>/
│   │   ├── image_001.png
│   │   ├── image_001_head.png  (如果裁剪)
│   │   ├── image_001_body.png  (如果裁剪)
│   │   ├── image_002.png
│   │   └── ...
│   └── <another_character_or_tag>/
│       └── ...
└── ...
```
文件名和目录结构可以通过 `SaveExporter` 的 `output_path` 和 `filename_formatter` 参数进行定制。

## 6. 未来可能的扩展 ("发布" 的进一步含义)

虽然当前“发布”主要指本地保存，但未来可以考虑：

*   **打包为标准数据集格式**: 例如，生成符合 COCO, Pascal VOC 格式的标注文件（如果集成了打标功能）。
*   **上传到云存储**: 集成 `boto3` (AWS S3), `google-cloud-storage` 等库，将数据集上传到云端。
*   **上传到数据集平台**:
    *   **Hugging Face Datasets**: 使用 `huggingface_hub` 和 `datasets` 库将数据集推送到 Hugging Face Hub。
    *   **Kaggle**: 使用 Kaggle API (通过 `kaggle` Python 包) 创建和上传数据集。

这些扩展将需要引入新的依赖库和更复杂的逻辑。

## 7. 总结

`dataset-creator` 将围绕 `waifuc` 构建，利用其强大的数据源和处理能力，并通过 `argparse` 提供简洁的命令行接口。通过 `Pillow` 和可选的 `imgutils`，可以实现灵活的图像处理。数据集的输出主要通过 `waifuc` 的 `SaveExporter` 完成，确保图像被妥善保存在本地。