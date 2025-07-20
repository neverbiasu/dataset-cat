# dataset_cat/postprocessing_ui.py
import io
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

import gradio as gr
from PIL import Image

from waifuc.action import (
    AlignMaxSizeAction,
    AlignMinSizeAction,
    FilterAction,
    MinSizeFilterAction,
    ModeConvertAction,
    ProcessAction,
)
from waifuc.export import SaveExporter
from waifuc.model import ImageItem
from dataset_cat.core.actions import CropToDivisibleAction, FileSizeFilterAction, ImageCompressionAction

def create_postprocessing_tab_content(locale: Optional[Dict[str, Any]] = None) -> Dict[str, gr.Component]:
    """
    创建数据后处理标签页内容，支持国际化。

    Args:
        locale: 本地化数据字典，包含 UI 标签的翻译

    Returns:
        Dict[str, gr.Component]: 包含所有后处理组件的字典，便于后续更新
    """
    if locale is None:
        locale = {}

    def _get_localized(key: str, default: str) -> str:
        return locale.get(key, default)

    def _get_actions_localized(key: str, default: str) -> str:
        return locale.get("actions_list", {}).get(key, default)

    components: Dict[str, gr.Component] = {}

    actions_mapping = {
        "resize_min": _get_actions_localized("resize_min", "调整大小（最小尺寸）"),
        "resize_max": _get_actions_localized("resize_max", "调整大小（最大尺寸）"),
        "mode_convert": _get_actions_localized("mode_convert", "转换模式（RGB/RGBA）"),
        "compress_image": _get_actions_localized("compress_image", "压缩图片"),
        "crop_to_divisible": _get_actions_localized("crop_to_divisible", "裁剪为可整除尺寸"),
        "filter_filesize": _get_actions_localized("filter_filesize", "按文件大小筛选"),
    }

    with gr.Column():
        with gr.Row():
            input_dir = gr.Textbox(label=_get_localized("input_dir_label", "输入目录"), interactive=True)
            output_dir = gr.Textbox(label=_get_localized("output_dir_post_label", "输出目录"), interactive=True)
            components["input_dir"] = input_dir
            components["output_dir"] = output_dir

        with gr.Row():
            preview_btn = gr.Button(_get_localized("preview_images_button", "预览图片"))
            process_btn = gr.Button(_get_localized("process_images_button", "处理图片"))
            components["preview_btn"] = preview_btn
            components["process_btn"] = process_btn

        result = gr.Textbox(label=_get_localized("result_label", "结果"), interactive=False)
        components["result"] = result

        actions = gr.CheckboxGroup(
            choices=list(actions_mapping.values()),
            label=_get_localized("actions_post_label", "后处理操作"),
        )
        components["actions"] = actions

        with gr.Column(visible=False) as resize_min_params:
            min_size = gr.Number(value=512, label=_get_localized("min_size_label", "最小尺寸（像素）"))
            components["min_size"] = min_size
            components["resize_min_params"] = resize_min_params

        with gr.Column(visible=False) as resize_max_params:
            max_size = gr.Number(value=1024, label=_get_localized("max_size_label", "最大尺寸（像素）"))
            components["max_size"] = max_size
            components["resize_max_params"] = resize_max_params

        with gr.Column(visible=False) as mode_convert_params:
            mode = gr.Dropdown(choices=["RGB", "RGBA"], value="RGB", label=_get_localized("mode_label", "模式"))
            components["mode"] = mode
            components["mode_convert_params"] = mode_convert_params

        with gr.Column(visible=False) as compress_params:
            quality = gr.Slider(minimum=1, maximum=100, value=85, step=1, label=_get_localized("quality_label", "质量（%）"))
            components["quality"] = quality
            components["compress_params"] = compress_params

        with gr.Column(visible=False) as crop_divisible_params:
            divisible_by = gr.Number(value=32, label=_get_localized("divisible_by_label", "整除值"))
            components["divisible_by"] = divisible_by
            components["crop_divisible_params"] = crop_divisible_params

        with gr.Column(visible=False) as filesize_filter_params:
            min_filesize = gr.Number(value=0, label=_get_localized("min_filesize_label", "最小文件大小（KB）"))
            max_filesize = gr.Number(value=10000, label=_get_localized("max_filesize_label", "最大文件大小（KB）"))
            components["min_filesize"] = min_filesize
            components["max_filesize"] = max_filesize
            components["filesize_filter_params"] = filesize_filter_params

        param_groups = {
            actions_mapping["resize_min"]: resize_min_params,
            actions_mapping["resize_max"]: resize_max_params,
            actions_mapping["mode_convert"]: mode_convert_params,
            actions_mapping["compress_image"]: compress_params,
            actions_mapping["crop_to_divisible"]: crop_divisible_params,
            actions_mapping["filter_filesize"]: filesize_filter_params,
        }

        def update_visibility(selected_actions: List[str]) -> List[Any]:
            return [gr.update(visible=(action in selected_actions)) for action, grp in param_groups.items()]

        actions.change(update_visibility, inputs=[actions], outputs=list(param_groups.values()))

        def preview_images(input_directory: str) -> str:
            if not os.path.exists(input_directory):
                return _get_localized("no_images_found", "在目录中未找到图片")
            files = []
            for ext in ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif']:
                files.extend(Path(input_directory).glob(f"**/*{ext}"))
                files.extend(Path(input_directory).glob(f"**/*{ext.upper()}"))
            if not files:
                return _get_localized("no_images_found", "在目录中未找到图片")
            return _get_localized("preview_result", "预览：在目录中找到 {count} 张图片").format(count=len(files))

        def process_images(
            input_directory: str,
            output_directory: str,
            selected_actions: List[str],
            min_size_val: Optional[int] = None,
            max_size_val: Optional[int] = None,
            mode_val: Optional[str] = None,
            quality_val: Optional[int] = None,
            divisible_by_val: Optional[int] = None,
            min_filesize_val: Optional[int] = None,
            max_filesize_val: Optional[int] = None,
            *args, **kwargs
        ) -> str:
            """
            Process images in the input directory, applying selected actions and saving to output directory.

            Args:
                input_directory: Path to source images.
                output_directory: Path to save processed images.
                selected_actions: List of action names (localized labels) to apply.
                min_size_val: Minimum dimension for resize min.
                max_size_val: Maximum dimension for resize max.
                mode_val: Color mode to convert ("RGB"/"RGBA").
                quality_val: JPEG quality for compression.
                divisible_by_val: Value to crop dimensions by.
                min_filesize_val: Minimum file size in KB.
                max_filesize_val: Maximum file size in KB.

            Returns:
                Summary message of processed image count.
            """
            # Ensure output directory exists
            os.makedirs(output_directory, exist_ok=True)
            # Find all image files in input directory
            exts = ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif']
            # Only collect unique files (avoid duplicates from upper/lower case)
            file_set = set()
            for ext in exts:
                file_set.update(Path(input_directory).glob(f"**/*{ext}"))
                file_set.update(Path(input_directory).glob(f"**/*{ext.upper()}"))
            files = list(file_set)
            print("Found files:", files)
            processed_count = 0

            # Map localized labels back to action keys
            inverse_map = {v: k for k, v in actions_mapping.items()}
            # Build processing pipeline
            pipeline: List[Any] = []
            for label in selected_actions:
                key = inverse_map.get(label)
                if key == 'resize_min' and min_size_val:
                    pipeline.append(AlignMinSizeAction(min_size_val))
                elif key == 'resize_max' and max_size_val:
                    pipeline.append(AlignMaxSizeAction(max_size_val))
                elif key == 'mode_convert' and mode_val:
                    pipeline.append(ModeConvertAction(mode_val))
                elif key == 'compress_image' and quality_val:
                    pipeline.append(ImageCompressionAction(quality_val))
                elif key == 'crop_to_divisible' and divisible_by_val:
                    # Fix: CropToDivisibleAction 需要传递 Image 对象，且部分实现可能会返回 None
                    pipeline.append(CropToDivisibleAction(int(divisible_by_val)))
                elif key == 'filter_filesize' and (min_filesize_val is not None or max_filesize_val is not None):
                    pipeline.append(FileSizeFilterAction(int(min_filesize_val or 0), int(max_filesize_val or 0)))

            # Process each file
            for path in files:
                try:
                    img = Image.open(path)
                    filtered = False
                    for action in pipeline:
                        try:
                            # Special handling for CropToDivisibleAction: expects ImageItem, returns ImageItem
                            if isinstance(action, CropToDivisibleAction):
                                img_item = ImageItem(img)
                                img_item = action(img_item)
                                img = img_item.image if img_item is not None else None
                            else:
                                img = action.apply(img) if hasattr(action, 'apply') else action(img)
                        except Exception as e:
                            print(f"Action {action} failed on {path}: {e}")
                            filtered = True
                            break
                        if img is None:
                            filtered = True
                            break
                    if filtered:
                        continue
                    # Save processed image
                    save_name = Path(path).name
                    img.save(Path(output_directory) / save_name)
                    processed_count += 1
                except Exception as e:
                    print(f"Failed to process {path}: {e}")
                    continue

            # Return summary message
            return _get_localized("processing_completed", "处理完成。{count} 张图片处理完毕。").format(count=processed_count)
    preview_btn.click(
        preview_images,
        inputs=[input_dir],
        outputs=result,
        show_progress=True,
    )
    process_btn.click(
        process_images,
        inputs=[
            input_dir,
            output_dir,
            actions,
            min_size,
            max_size,
            mode,
            quality,
            divisible_by,
            min_filesize,
            max_filesize,
        ],
        outputs=result,
    )
    return components


def update_postprocessing_ui_language(components: Dict[str, gr.Component], locale_data: Dict[str, Any]) -> List[Any]:
    """
    Update postprocessing UI component labels and choices based on new locale data.
    
    Args:
        components: Dictionary of component names to Gradio components
        locale_data: Dictionary containing localized text
        
    Returns:
        List of gr.update() objects in the same order as components.values()
    """
    # Helper to get localized text with fallback
    def _loc(key: str, default: str) -> str:
        return locale_data.get(key, default)

    # Create updates in the same order as components are stored in the dictionary
    # This must match the order in which components are added to the dictionary in create_postprocessing_tab_content
    updates = []
    
    # Based on the component creation order:
    # 1. input_dir
    updates.append(gr.update(label=_loc("input_dir_label", "输入目录")))
    # 2. output_dir  
    updates.append(gr.update(label=_loc("output_dir_post_label", "输出目录")))
    # 3. preview_btn
    updates.append(gr.update(value=_loc("preview_images_button", "预览图片")))
    # 4. process_btn
    updates.append(gr.update(value=_loc("process_images_button", "处理图片")))
    # 5. result
    updates.append(gr.update(label=_loc("result_label", "结果")))
    # 6. actions - update both choices and label
    action_list = locale_data.get("actions_list", {})
    action_choices = [
        action_list.get("resize_min", "调整大小（最小尺寸）"),
        action_list.get("resize_max", "调整大小（最大尺寸）"), 
        action_list.get("mode_convert", "转换模式（RGB/RGBA）"),
        action_list.get("compress_image", "压缩图片"),
        action_list.get("crop_to_divisible", "裁剪为可整除尺寸"),
        action_list.get("filter_filesize", "按文件大小筛选"),
    ]
    updates.append(gr.update(choices=action_choices, label=_loc("actions_post_label", "后处理操作")))
    # 7. min_size
    updates.append(gr.update(label=_loc("min_size_label", "最小尺寸（像素）")))
    # 8. resize_min_params - no update needed for Column visibility
    updates.append(gr.update())
    # 9. max_size
    updates.append(gr.update(label=_loc("max_size_label", "最大尺寸（像素）")))
    # 10. resize_max_params - no update needed for Column visibility
    updates.append(gr.update())
    # 11. mode
    updates.append(gr.update(label=_loc("mode_label", "模式")))
    # 12. mode_convert_params - no update needed for Column visibility
    updates.append(gr.update())
    # 13. quality
    updates.append(gr.update(label=_loc("quality_label", "质量（%）")))
    # 14. compress_params - no update needed for Column visibility
    updates.append(gr.update())
    # 15. divisible_by
    updates.append(gr.update(label=_loc("divisible_by_label", "整除值")))
    # 16. crop_divisible_params - no update needed for Column visibility
    updates.append(gr.update())
    # 17. min_filesize
    updates.append(gr.update(label=_loc("min_filesize_label", "最小文件大小（KB）")))
    # 18. max_filesize
    updates.append(gr.update(label=_loc("max_filesize_label", "最大文件大小（KB）")))
    # 19. filesize_filter_params - no update needed for Column visibility
    updates.append(gr.update())
    
    return updates
