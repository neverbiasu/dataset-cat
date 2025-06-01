import gradio as gr
import os
import shutil
from typing import List, Optional, Any, Dict
import tempfile
from pathlib import Path

# waifuc相关导入
from waifuc.source import LocalSource
from waifuc.action import AlignMinSizeAction, AlignMaxSizeAction, MinSizeFilterAction, ModeConvertAction, ProcessAction
from waifuc.export import SaveExporter
from waifuc.model import ImageItem
from PIL import Image

# 自定义Action：将图像裁剪到可被指定因子整除的尺寸
class CropToDivisibleAction(ProcessAction):
    """
    自定义Action，将图像裁剪到可被指定因子整除的尺寸
    """
    def __init__(self, factor: int = 64):
        self.factor = factor
    
    def process(self, item: ImageItem) -> ImageItem:
        """处理单个图像项"""
        # 获取图像数据
        image = item.image
        
        # 计算新的尺寸
        width, height = image.size
        new_width = (width // self.factor) * self.factor
        new_height = (height // self.factor) * self.factor
        
        # 如果尺寸没有变化，直接返回
        if new_width == width and new_height == height:
            return item
        
        # 计算裁剪的起始位置（居中裁剪）
        left = (width - new_width) // 2
        top = (height - new_height) // 2
        right = left + new_width
        bottom = top + new_height
        
        # 裁剪图像
        cropped_image = image.crop((left, top, right, bottom))
        
        # 返回新的ImageItem
        return ImageItem(cropped_image, item.meta)

def create_postprocessing_tab_content():
    """
    创建数据后处理标签页的 UI 内容。
    此函数应在 gr.TabItem 上下文中调用。
    """
    gr.Markdown("## 数据后处理")
    gr.Markdown("对本地图像数据集进行批量后处理，应用各种 `waifuc` Actions。")

    with gr.Row(equal_height=False):
        with gr.Column(scale=2, min_width=300):
            gr.Markdown("### 1. 输入源")
            input_type_postprocess = gr.Radio(
                choices=["处理目录", "处理上传文件"],
                label="选择输入方式",
                value="处理目录",
                elem_id="postprocess_input_type"
            )
            input_dir_postprocess = gr.Textbox(
                label="输入目录路径",
                placeholder="例如: D:\\my_dataset\\raw_images",
                visible=True,
                interactive=True,
                elem_id="postprocess_input_dir"
            )
            uploaded_files_postprocess = gr.Files(
                label="上传图像文件 (支持多个)",
                file_count="multiple",
                visible=False,
                elem_id="postprocess_uploaded_files"
            )
            output_dir_postprocess = gr.Textbox(
                label="输出目录路径",
                placeholder="例如: D:\\my_dataset\\processed_images",
                visible=True,
                interactive=True,
                elem_id="postprocess_output_dir"            )
        
        with gr.Column(scale=3, min_width=400):
            gr.Markdown("### 2. 选择并配置 Actions")
            # 这些 Actions 将在后续步骤中通过 action_manager.py 动态加载
            # 目前使用我们讨论过的占位符列表
            initial_action_choices = [
                "AlignMinSizeAction",
                "AlignMaxSizeAction",
                "MinSizeFilterAction", 
                "ModeConvertAction",
                "ConvertCUDAction",
                "CropToDivisibleAction (自定义)"
            ]
            selected_actions_checkbox = gr.CheckboxGroup(
                label="选择要应用的 Actions (将按勾选顺序执行)",
                choices=initial_action_choices,
                value=[], 
                elem_id="postprocess_selected_actions"
            )
            
            # 参数配置区域
            with gr.Column() as action_params_area:
                gr.Markdown("### Action 参数配置")
                
                # 创建所有参数组件，但不放在容器中以避免可见性问题                # AlignMinSizeAction 参数
                align_min_size_target = gr.Number(
                    label="目标最小边长度 (AlignMinSizeAction)",
                    value=800,
                    minimum=256,
                    maximum=2048,
                    step=1,
                    info="调整图像尺寸，保持纵横比",
                    visible=False
                )
                
                # AlignMaxSizeAction 参数
                align_max_size_target = gr.Number(
                    label="目标最大边长度 (AlignMaxSizeAction)",
                    value=1024,
                    minimum=512,
                    maximum=4096,
                    step=1,
                    info="限制图像最大尺寸，保持纵横比",
                    visible=False
                )
                
                # MinSizeFilterAction 参数
                min_size_value = gr.Number(
                    label="最小尺寸 (MinSizeFilterAction)",
                    value=256,
                    minimum=64,
                    maximum=1024,
                    step=1,
                    info="低于此尺寸的图像将被过滤掉",
                    visible=False
                )
                
                # ModeConvertAction 参数
                mode_convert_value = gr.Dropdown(
                    label="目标图像模式 (ModeConvertAction)",
                    choices=["RGB", "RGBA", "L"],
                    value="RGB",
                    info="转换图像到指定的颜色模式",
                    visible=False
                )
                
                # ConvertCUDAction 参数
                cuda_acceleration = gr.Checkbox(
                    label="启用 CUDA 加速 (ConvertCUDAction)",
                    value=True,
                    info="使用GPU加速处理（需要CUDA支持）",
                    visible=False
                )
                
                # CropToDivisibleAction 参数
                crop_factor = gr.Number(
                    label="裁剪因子 (CropToDivisibleAction)",
                    value=64,
                    minimum=8,
                    maximum=128,
                    step=8,
                    info="图像尺寸将调整为此数的倍数",
                    visible=False
                )
                
                # 无参数提示
                no_params_message = gr.Markdown(
                    "选择上方的 Action 后，此处将显示其参数配置选项。",
                    visible=True
                )

    gr.Markdown("### 3. 执行与反馈")
    with gr.Row():
        start_postprocessing_button = gr.Button("开始后处理", variant="primary", elem_id="postprocess_start_button")
    
    postprocess_progress = gr.Progress()
    
    postprocess_status = gr.Textbox(
        label="处理日志与状态",
        lines=5,
        interactive=False,
        placeholder="处理信息将显示在此处...",
        elem_id="postprocess_status_log"
    )
      # --- 事件处理程序 ---
    def _update_input_visibility(choice):
        if choice == "处理目录":
            return gr.update(visible=True), gr.update(visible=False)
        else:  # "处理上传文件"
            return gr.update(visible=False), gr.update(visible=True)
        
    def update_action_params(selected_actions):
        """
        根据用户选择的 Actions 更新参数配置区域的可见性。
        """
        # 默认所有参数组件都不可见
        align_min_size_visible = False
        align_max_size_visible = False
        min_size_filter_visible = False
        mode_convert_visible = False
        convert_cud_visible = False
        crop_divisible_visible = False
        no_params_visible = True
        
        if selected_actions:
            no_params_visible = False
            # 根据选择的actions设置对应参数组件可见
            for action in selected_actions:
                if action == "AlignMinSizeAction":
                    align_min_size_visible = True
                elif action == "AlignMaxSizeAction":
                    align_max_size_visible = True
                elif action == "MinSizeFilterAction":
                    min_size_filter_visible = True
                elif action == "ModeConvertAction":
                    mode_convert_visible = True
                elif action == "ConvertCUDAction":
                    convert_cud_visible = True
                elif action == "CropToDivisibleAction (自定义)":
                    crop_divisible_visible = True
        return (
            gr.update(visible=align_min_size_visible),
            gr.update(visible=align_max_size_visible),
            gr.update(visible=min_size_filter_visible), 
            gr.update(visible=mode_convert_visible),
            gr.update(visible=convert_cud_visible),
            gr.update(visible=crop_divisible_visible),
            gr.update(visible=no_params_visible)
        )
        
    # 绑定事件处理程序
    input_type_postprocess.change(
        fn=_update_input_visibility,
        inputs=[input_type_postprocess],
        outputs=[input_dir_postprocess, uploaded_files_postprocess],
        show_progress=False
    )

    selected_actions_checkbox.change(
        fn=update_action_params,
        inputs=[selected_actions_checkbox],
        outputs=[
            align_min_size_target,
            align_max_size_target,
            min_size_value,
            mode_convert_value,
            cuda_acceleration,
            crop_factor,
            no_params_message        ],
        show_progress=False
    )    
    # 后处理核心函数
    def run_postprocessing(
        input_type, input_dir, uploaded_files, output_dir, selected_actions,
        align_min_size_target, align_max_size_target, min_size_value, mode_convert_value, cuda_acceleration, crop_factor,
        progress=gr.Progress()
    ):
        """
        执行图像后处理的核心函数
        """
        try:
            # 基本验证
            if not output_dir:
                return "错误：请指定输出目录"
            
            if not selected_actions:
                return "错误：请至少选择一个处理动作"
            
            # 验证输入源
            temp_dir = None
            source_path = None
            
            if input_type == "处理目录":
                if not input_dir:
                    return "错误：请指定输入目录"
                if not os.path.exists(input_dir):
                    return f"错误：输入目录不存在: {input_dir}"
                source_path = input_dir
            else:  # 处理上传文件
                if not uploaded_files:
                    return "错误：请上传至少一个文件"
                # 创建临时目录保存上传的文件
                temp_dir = tempfile.mkdtemp(prefix="postprocess_temp_")
                for i, uploaded_file in enumerate(uploaded_files):
                    temp_file_path = os.path.join(temp_dir, f"uploaded_{i}_{os.path.basename(uploaded_file.name)}")
                    os.rename(uploaded_file.name, temp_file_path)
                source_path = temp_dir
            
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)
            
            progress(0.1, desc="准备处理pipeline...")
              # 构建waifuc Actions pipeline
            actions = []
            action_names = []
            
            for action_name in selected_actions:
                if action_name == "AlignMinSizeAction":
                    actions.append(AlignMinSizeAction(align_min_size_target))
                    action_names.append(f"AlignMinSizeAction({align_min_size_target})")
                    
                elif action_name == "AlignMaxSizeAction":
                    actions.append(AlignMaxSizeAction(align_max_size_target))
                    action_names.append(f"AlignMaxSizeAction({align_max_size_target})")
                    
                elif action_name == "MinSizeFilterAction":
                    actions.append(MinSizeFilterAction(min_size_value))
                    action_names.append(f"MinSizeFilterAction({min_size_value})")
                    
                elif action_name == "ModeConvertAction":
                    actions.append(ModeConvertAction(mode=mode_convert_value, force_background='white'))
                    action_names.append(f"ModeConvertAction({mode_convert_value}, white)")
                    
                elif action_name == "ConvertCUDAction":
                    # 注意：ConvertCUDAction可能不存在或需要特殊处理
                    # 暂时跳过，只记录日志
                    action_names.append(f"ConvertCUDAction(跳过-未实现)")
                    
                elif action_name == "CropToDivisibleAction (自定义)":
                    actions.append(CropToDivisibleAction(crop_factor))
                    action_names.append(f"CropToDivisibleAction({crop_factor})")
            
            progress(0.2, desc="创建数据源...")
            
            result_msg = f"✅ 开始处理图像\n"
            result_msg += f"输入源: {source_path}\n"
            result_msg += f"输出目录: {output_dir}\n"
            result_msg += f"应用的Actions: {', '.join(action_names)}\n\n"
            
            processed_count = 0
            error_count = 0
            try:
                # 创建源并应用所有动作
                source = LocalSource(source_path)
                if actions:
                    source = source.attach(*actions)
                    progress(0.8, desc="保存处理后的图像...")
                
                # 创建导出器并执行导出
                # 使用 ignore_error_when_export=True 避免单个文件错误导致整个流程停止
                # 使用 save_params 强制 PNG 格式以避免 JPEG 格式问题
                exporter = SaveExporter(
                    output_dir, 
                    no_meta=True, 
                    ignore_error_when_export=True,
                    save_params={'format': 'PNG'}
                )
                source.export(exporter)
                
                # 计算处理的文件数量
                if os.path.exists(output_dir):
                    processed_files = [f for f in os.listdir(output_dir) 
                                     if os.path.isfile(os.path.join(output_dir, f)) and 
                                     f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'))]
                    processed_count = len(processed_files)
                        
            except Exception as pipeline_error:
                import traceback
                error_count += 1
                error_details = traceback.format_exc()
                result_msg += f"❌ Pipeline执行错误: {str(pipeline_error)}\n"
                result_msg += f"详细错误信息:\n{error_details}\n"
                return result_msg
            
            progress(0.95, desc="清理临时文件...")
            
            # 清理临时目录
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
            
            progress(1.0, desc="处理完成!")
            
            result_msg += f"\n🎉 处理完成!\n"
            result_msg += f"✅ 成功处理: {processed_count} 张图像\n"
            if error_count > 0:
                result_msg += f"⚠️ 处理失败: {error_count} 张图像\n"
            result_msg += f"📁 输出目录: {output_dir}\n"
            
            return result_msg
            
        except Exception as e:
            # 确保清理临时目录
            if 'temp_dir' in locals() and temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
            return f"❌ 处理过程中发生错误: {str(e)}"
            
    # 绑定开始处理按钮
    start_postprocessing_button.click(
        fn=run_postprocessing,        inputs=[
            input_type_postprocess, input_dir_postprocess, uploaded_files_postprocess, 
            output_dir_postprocess, selected_actions_checkbox,
            align_min_size_target, align_max_size_target, min_size_value, mode_convert_value, cuda_acceleration, crop_factor
        ],
        outputs=[postprocess_status],
        show_progress=True
    )
    
    # 返回所有可能需要从外部引用的重要组件
    return (
        input_type_postprocess, input_dir_postprocess, uploaded_files_postprocess, 
        output_dir_postprocess, selected_actions_checkbox, action_params_area,
        start_postprocessing_button, postprocess_progress, postprocess_status,
        align_min_size_target, align_max_size_target, min_size_value, mode_convert_value, cuda_acceleration, crop_factor
    )
