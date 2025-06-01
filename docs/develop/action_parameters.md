# Action 参数介绍

以下是 `waifuc` 提供的常见 `Action` 及其参数说明：

| Action 名称               | 参数名称              | 参数类型       | 参数说明                     |
|---------------------------|-----------------------|----------------|------------------------------|
| AlignMinSizeAction        | min_size             | int            | 图像短边的目标长度           |
| HeadCutOutAction          | kp_threshold         | float          | 关键点阈值                   |
|                           | level                | str            | 检测级别                     |
|                           | version              | str            | 模型版本                     |
|                           | max_infer_size       | int            | 最大推理尺寸                 |
|                           | conf_threshold       | float          | 置信度阈值                   |
|                           | iou_threshold        | float          | IoU 阈值                     |
| CharacterEnhanceAction    | repeats              | int            | 重复次数                     |
|                           | modes                | List[str]      | 增强模式，例如 `head`         |
|                           | head_ratio           | float          | 头部比例                     |
|                           | body_ratio           | float          | 身体比例                     |
|                           | halfbody_ratio       | float          | 半身比例                     |
|                           | degree_range         | Tuple[float]   | 旋转角度范围                 |
| FilterSimilarAction       | mode                 | str            | 过滤模式，例如 `all`          |
|                           | threshold            | float          | 相似度阈值                   |
|                           | capacity             | int            | 容量                         |
|                           | rtol                 | float          | 相对容差                     |
|                           | atol                 | float          | 绝对容差                     |
| TaggingAction             | method               | str            | 标记方法，例如 `wd14_v3_swinv2` |
|                           | force                | bool           | 是否强制重新标记             |

此表格将随着 `waifuc` 的更新而扩展。
