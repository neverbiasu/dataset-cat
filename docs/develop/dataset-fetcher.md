# 数据抓取逻辑设计文档

## 1. 概述

本设计文档描述了 `dataset-creator` 中数据抓取逻辑的核心实现。抓取逻辑将封装为一个类，支持以下功能：

1. **基于 `waifuc` 的数据抓取**: 使用 `waifuc` 提供的 `Source` 类从支持的网站抓取图像。
2. **基于 `gallery-dl` 的数据抓取**: 使用 `gallery-dl` 工具从其他网站抓取图像。
3. **统一接口**: 提供一个统一的接口，用户可以通过简单的参数调用抓取逻辑，而无需关心底层实现细节。
4. **灵活性**: 支持通过标签、数量等参数自定义抓取逻辑。

## 2. 类设计

### 2.1 类名

`DatasetFetcher`

### 2.2 属性

| 属性名            | 类型          | 描述                                                                 |
|-------------------|---------------|----------------------------------------------------------------------|
| `source_type`     | `str`         | 数据抓取的方式，支持 `waifuc` 或 `gallery-dl`。                      |
| `tags`            | `list[str]`   | 用于抓取的标签列表（适用于 `waifuc`）。                              |
| `url`             | `str`         | 目标网站的 URL（适用于 `gallery-dl`）。                              |
| `output_dir`      | `str`         | 抓取结果保存的目录。                                                 |
| `quantity`        | `int`         | 要抓取的图像数量（适用于 `waifuc`）。                                |

### 2.3 方法

| 方法名            | 参数                          | 返回值       | 描述                                                                 |
|-------------------|-------------------------------|--------------|----------------------------------------------------------------------|
| `__init__`        | `source_type, tags, url, output_dir, quantity` | `None`       | 初始化抓取器实例。                                                  |
| `fetch`           | `None`                       | `None`       | 根据 `source_type` 执行抓取逻辑。                                    |

## 3. 使用示例

### 3.1 使用 `waifuc` 抓取数据

```python
fetcher = DatasetFetcher(
    source_type="waifuc",
    tags=["character_name", "game_name"],
    output_dir="output/waifuc",
    quantity=20
)
fetcher.fetch()
```

### 3.2 使用 `gallery-dl` 抓取数据

```python
fetcher = DatasetFetcher(
    source_type="gallery-dl",
    url="https://example.com/gallery",
    output_dir="output/gallery-dl"
)
fetcher.fetch()
```

## 4. 未来扩展

1. **支持更多数据源**: 可以扩展 `waifuc` 的数据源，或添加对其他工具的支持。
2. **错误处理与日志记录**: 增强错误处理逻辑，并添加日志记录功能。
3. **WebUI 集成**: 将该类集成到 Gradio WebUI 中，提供用户友好的界面。
4. **多线程支持**: 对于大规模抓取任务，可以添加多线程或异步支持以提高效率。

## 5. 相关文档

请参考 [index.md](../index.md) 获取更多类的设计信息。