# waifuc 项目介绍

## 1. 概述

[waifuc](https://github.com/deepghs/waifuc) 是一个用于从多个动漫相关数据源抓取图像和元数据的 Python 库。它提供了灵活的接口，支持多种数据源和导出方式，适用于动漫数据收集、处理和导出。

## 2. 核心功能

1. **多数据源支持**:  
   - 支持 Danbooru、Pixiv、Zerochan、Sankaku 等多个动漫相关数据源。
   - 提供统一的接口，便于用户切换数据源。
   - 支持通过标签、关键字、用户 ID 等方式抓取数据。

2. **数据处理与筛选**:  
   - 提供丰富的 `Action` 模块，用于数据清洗、过滤、裁剪、标注等操作。
   - 支持去除重复图像、过滤单色图像、按人脸数量筛选等功能。
   - 支持基于 CCIP 模型的角色过滤，确保抓取数据的高质量。

3. **数据导出**:  
   - 支持将抓取和处理后的数据保存为多种格式（如 JSON、图像文件、LoRA 数据集等）。
   - 提供灵活的导出器接口，支持自定义导出逻辑。

4. **灵活性与扩展性**:  
   - 支持用户自定义数据源、处理逻辑（Action）和导出器。
   - 提供模块化设计，便于集成到其他项目中。

## 3. 使用场景

1. **动漫数据收集**:  
   用户可以通过标签抓取特定角色或作品的图像和元数据，例如从 Danbooru 抓取某角色的图像。

2. **数据清洗与处理**:  
   使用内置的 `Action` 模块对抓取的数据进行清洗和筛选，例如去除低质量图像或裁剪多角色图像。

3. **机器学习数据集构建**:  
   将处理后的数据导出为适合训练 LoRA 或其他深度学习模型的数据集格式。

4. **视频帧提取**:  
   支持从视频中提取帧并处理为高质量的图像数据。

## 4. 在 DatasetFetcher 中的应用

`DatasetFetcher` 使用 `waifuc` 作为其数据抓取方式之一，主要用于以下场景：
- **基于标签抓取特定图像**: 通过 `waifuc` 的 `DanbooruSource` 或 `PixivSearchSource` 等数据源抓取特定角色的图像。
- **数据处理与清洗**: 使用 `waifuc` 的 `Action` 模块对抓取的数据进行清洗和筛选。
- **数据导出**: 使用 `waifuc` 的 `TextualInversionExporter` 或 `SaveExporter` 将数据保存为指定格式。

以下是一个简单的使用示例：

```python
from waifuc.source import DanbooruSource
from waifuc.action import NoMonochromeAction, FilterSimilarAction
from waifuc.export import SaveExporter

# 初始化数据源
source = DanbooruSource(tags=["surtr_(arknights)"], limit=50)

# 添加数据处理逻辑
source.attach(
    NoMonochromeAction(),  # 去除单色图像
    FilterSimilarAction()  # 去除重复图像
)

# 导出数据
exporter = SaveExporter(output_dir="output/surtr_dataset")
for item in source:
    exporter.export_item(item)
```

## 5. 相关链接

- GitHub 仓库: [waifuc](https://github.com/deepghs/waifuc)
- 文档与示例: 请参考仓库中的 `README.md` 和 [官方文档](https://deepghs.github.io/waifuc/main/index.html)

## 6. 支持的主流下载站

以下是 waifuc 当前支持的主流下载站及其对应的导入方式：

| 名称                                              | 网站链接                                      | 导入语句                                   |
|---------------------------------------------------|----------------------------------------------|-------------------------------------------|
| ATFBooruSource                                    | [ATFBooru](https://booru.allthefallen.moe)   | `from waifuc.source import ATFBooruSource` |
| AnimePicturesSource                               | [AnimePictures](https://anime-pictures.net)  | `from waifuc.source import AnimePicturesSource` |
| DanbooruSource                                    | [Danbooru](https://danbooru.donmai.us)       | `from waifuc.source import DanbooruSource` |
| DerpibooruSource                                  | [Derpibooru](https://derpibooru.org)         | `from waifuc.source import DerpibooruSource` |
| DuitangSource                                     | [堆糖](https://www.duitang.com)              | `from waifuc.source import DuitangSource` |
| E621Source                                        | [E621](https://e621.net)                     | `from waifuc.source import E621Source` |
| E926Source                                        | [E926](https://e926.net)                     | `from waifuc.source import E926Source` |
| FurbooruSource                                    | [Furbooru](https://furbooru.com)             | `from waifuc.source import FurbooruSource` |
| GelbooruSource                                    | [Gelbooru](https://gelbooru.com)             | `from waifuc.source import GelbooruSource` |
| Huashi6Source                                     | [触站](https://www.huashi6.com)              | `from waifuc.source import Huashi6Source` |
| HypnoHubSource                                    | [HypnoHub](https://hypnohub.net)             | `from waifuc.source import HypnoHubSource` |
| KonachanNetSource                                 | [Konachan.net](https://konachan.net)         | `from waifuc.source import KonachanNetSource` |
| KonachanSource                                    | [Konachan.com](https://konachan.com)         | `from waifuc.source import KonachanSource` |
| LolibooruSource                                   | [Lolibooru](https://lolibooru.moe)           | `from waifuc.source import LolibooruSource` |
| PahealSource                                      | [Paheal](https://rule34.paheal.net)          | `from waifuc.source import PahealSource` |
| PixivRankingSource                                | [Pixiv 排行榜](https://pixiv.net)            | `from waifuc.source import PixivRankingSource` |
| PixivSearchSource                                 | [Pixiv 搜索](https://pixiv.net)              | `from waifuc.source import PixivSearchSource` |
| PixivUserSource                                   | [Pixiv 用户](https://pixiv.net)              | `from waifuc.source import PixivUserSource` |
| Rule34Source                                      | [Rule34](https://rule34.xxx)                 | `from waifuc.source import Rule34Source` |
| SafebooruOrgSource                                | [Safebooru.org](https://safebooru.org)       | `from waifuc.source import SafebooruOrgSource` |
| SafebooruSource                                   | [Safebooru](https://safebooru.donmai.us)     | `from waifuc.source import SafebooruSource` |
| SankakuSource                                     | [Sankaku](https://chan.sankakucomplex.com)   | `from waifuc.source import SankakuSource` |
| TBIBSource                                        | [TBIB](https://tbib.org)                     | `from waifuc.source import TBIBSource` |
| WallHavenSource                                   | [WallHaven](https://wallhaven.cc)            | `from waifuc.source import WallHavenSource` |
| XbooruSource                                      | [Xbooru](https://xbooru.com)                 | `from waifuc.source import XbooruSource` |
| YandeSource                                       | [Yande.re](https://yande.re)                 | `from waifuc.source import YandeSource` |
| ZerochanSource                                    | [Zerochan](https://www.zerochan.net)         | `from waifuc.source import ZerochanSource` |

## 7. 抓取的高级用法

### 7.1 多站点联合抓取

waifuc 支持通过串联（`+`）和并联（`|`）操作对多个数据源进行联合抓取。例如：

```python
from waifuc.export import SaveExporter
from waifuc.source import DanbooruSource, ZerochanSource

# 初始化 Danbooru 和 Zerochan 数据源
s_db = DanbooruSource(['amiya_(arknights)', 'solo'], min_size=1000)
s_zerochan = ZerochanSource('Amiya', username='your_username', password='your_password', select='full', strict=True)

# 串联操作：先从 Danbooru 抓取 30 张，再从 Zerochan 抓取 30 张
s_concat = s_db[:30] + s_zerochan[:30]

# 并联操作：从两个站点随机抓取 60 张
s_union = (s_db | s_zerochan)[:60]

# 导出数据
s_concat.export(SaveExporter('/data/amiya_concat'))
s_union.export(SaveExporter('/data/amiya_union'))
```

### 7.2 数据源的复杂组合

支持对数据源进行复杂的嵌套组合。例如：

```python
from waifuc.export import SaveExporter
from waifuc.source import DanbooruSource, ZerochanSource, PixivSearchSource

# 初始化多个数据源
s_db = DanbooruSource(['amiya_(arknights)', 'solo'], min_size=1000)
s_zerochan = ZerochanSource('Amiya', username='your_username', password='your_password', select='full', strict=True)
s_pixiv = PixivSearchSource('アークナイツ (amiya OR アーミヤ OR 阿米娅)', refresh_token='your_pixiv_refresh_token')

# 复杂组合：从 Zerochan 抓取 50 张 + (Danbooru 和 Pixiv 随机抓取 50 张)
s_complex = s_zerochan[:50] + (s_db | s_pixiv)[:50]

# 导出数据
s_complex.export(SaveExporter('/data/amiya_complex'))
```

通过以上功能，用户可以灵活地从多个站点抓取数据并构建高质量的数据集。
