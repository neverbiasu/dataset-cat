# 中文到英文标签转换模块开发文档

## 1. 概述

本开发文档旨在指导开发者实现中文到英文标签转换模块。模块的主要功能包括：
- 中文描述翻译
- 数据源类型判断与标签格式化
- 结果输出

## 2. 技术栈

- **编程语言**: Python
- **依赖库**:
  - `googletrans`: 用于翻译中文描述

## 3. 模块结构

```
dataset_cat/
├── __init__.py
├── translator.py  # 翻译与格式化逻辑
├── api.py         # 提供 API 接口
```

## 4. 实现步骤

### 4.1 翻译功能

1. 安装 `googletrans` 库：
   ```cmd
   pip install googletrans==4.0.0-rc1
   ```
2. 在 `translator.py` 中实现翻译功能：

   ```python
   from googletrans import Translator

   def translate_to_english(description: str) -> str:
       """
       Translate Chinese description to English.

       Args:
           description (str): Chinese description.

       Returns:
           str: Translated English text.
       """
       translator = Translator()
       result = translator.translate(description, src="zh-cn", dest="en")
       return result.text
   ```

### 4.2 标签格式化

1. 在 `translator.py` 中添加格式化逻辑：

   ```python
   def format_tag(tag: str, source_type: str) -> str:
       """
       Format tag based on source type.

       Args:
           tag (str): Translated tag.
           source_type (str): Data source type (e.g., "Danbooru").

       Returns:
           str: Formatted tag.
       """
       if source_type.lower() in ["danbooru", "gelbooru", "safebooru"]:
           return tag.replace(" ", "_").lower()
       return tag
   ```

### 4.3 API 接口

1. 在 `api.py` 中设计接口：

   - **接口名称**: `get_formatted_tag`
   - **输入参数**:
     - `description` (str): 中文描述。
     - `source_type` (str): 数据源类型。
   - **返回值**:
     - `formatted_tag` (str): 格式化后的英文标签。
   - **接口逻辑**:
     - 接收用户输入的中文描述和数据源类型。
     - 调用翻译服务将中文描述翻译为英文。
     - 根据数据源类型格式化翻译结果。
     - 返回格式化后的标签。

2. 数据结构设计：

   - **输入数据结构**:
     ```json
     {
       "description": "初音未来",
       "source_type": "Danbooru"
     }
     ```

   - **输出数据结构**:
     ```json
     {
       "formatted_tag": "hatsune_miku"
     }
     ```

### 4.4 单元测试

1. 安装 `pytest`：
   ```cmd
   pip install pytest
   ```
2. 在 `tests/test_translator.py` 中编写测试用例：

   ```python
   import pytest
   from translator import translate_to_english, format_tag

   def test_translate_to_english():
       assert translate_to_english("初音未来") == "Hatsune Miku"

   def test_format_tag():
       assert format_tag("Hatsune Miku", "Danbooru") == "hatsune_miku"
       assert format_tag("Hatsune Miku", "Zerochan") == "Hatsune Miku"
   ```

## 5. 注意事项

1. 确保网络连接稳定以调用翻译服务。
2. 针对不同数据源类型，扩展 `format_tag` 函数以支持更多规则。
3. 在提交代码前运行所有单元测试，确保功能正常。

## 6. 未来扩展

1. 支持更多翻译服务以提高准确性。
2. 提供 CLI 工具或 WebUI 界面，方便用户使用。
3. 增强对复杂描述的解析能力。
