# 中文到英文标签转换模块设计文档

## 1. 概述

中文到英文标签转换模块旨在通过用户输入的中文描述，自动生成与之对应的英文标签，并根据数据源类型格式化为适合的标签形式（如 Booru Tag 或普通英文标签）。

## 2. 产品功能

1. **中文描述翻译**：支持用户输入中文描述，并自动翻译成英文。
2. **数据源类型判断**：根据用户选择的数据源类型，决定是否将翻译结果格式化为 Booru Tag。
3. **结果输出**：显示翻译和格式化后的结果，供用户复制或传递到其他模块。

## 3. 信息结构

### 输入

| 字段名       | 类型          | 描述                                   |
|--------------|---------------|----------------------------------------|
| `description`| `str`         | 中文描述，例如“初音未来”。            |
| `source_type`| `str`         | 数据源类型，例如“Danbooru”或“Zerochan”。|

### 输出

| 字段名       | 类型          | 描述                                   |
|--------------|---------------|----------------------------------------|
| `formatted_tag`| `str`       | 格式化后的标签，例如 `hatsune_miku` 或 `Hatsune Miku`。 |

## 4. 用户场景

1. **场景 1: Booru 数据源**  
   用户输入“初音未来”，选择数据源为“Danbooru”，系统返回 `hatsune_miku`。  
   - **Booru 数据源说明**: Booru 数据源是一类以标签为基础的图像存储平台，例如 Danbooru、Gelbooru 和 Safebooru。这些平台使用下划线连接的英文标签来标识图像内容。
   - **示例**: 用户输入“初音未来”，系统调用翻译接口返回 `Hatsune Miku`，并根据 Booru 数据源格式化为 `hatsune_miku`。

2. **场景 2: 非 Booru 数据源**  
   用户输入“初音未来”，选择数据源为“Zerochan”，系统返回 `Hatsune Miku`。  
   - **示例**: 用户输入“初音未来”，系统调用翻译接口返回 `Hatsune Miku`，保留空格格式。

## 5. 实现方式

1. **翻译接口**：使用 Google Translate API 或其他翻译服务，将中文描述翻译成英文。
2. **格式化逻辑**：
   - 如果数据源为 Booru 类型，将翻译结果中的空格替换为下划线。
   - 如果数据源为非 Booru 类型，保留空格。
3. **接口设计**：提供 API 接口或 CLI 工具供用户调用。

## 6. 未来扩展

1. 支持更多数据源类型的格式化规则。
2. 提供 WebUI 界面，实时显示翻译和格式化结果。
3. 增强翻译接口的准确性，支持更复杂的描述解析。
