# 项目类设计总览

## 1. 类列表

1. **DatasetFetcher**: 数据抓取逻辑，支持 `waifuc` 和 `gallery-dl` 两种方式。
2. **DatasetProcessor**: 数据处理逻辑，用于对抓取的图像进行清洗、过滤和格式转换。
3. **DatasetExporter**: 数据导出逻辑，支持将处理后的数据保存为多种格式（如 JSON、CSV 等）。
4. **WebUIManager**: Web 界面管理类，提供用户友好的操作界面。

## 2. 设计文档

### 产品设计文档

- [DatasetFetcher](../product/dataset-fetcher.md): 数据抓取逻辑的产品设计文档。
- DatasetProcessor: 待补充。
- DatasetExporter: 待补充。
- WebUIManager: 待补充。

### 开发设计文档

- [DatasetFetcher](develop/dataset-fetcher.md): 数据抓取逻辑的开发设计文档。
- DatasetProcessor: 待补充。
- DatasetExporter: 待补充。
- WebUIManager: 待补充。
