import gradio as gr
from waifuc.action import NoMonochromeAction, FilterSimilarAction
from waifuc.export import SaveExporter, TextualInversionExporter, HuggingFaceExporter
from dataset_cat.crawler import Crawler
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define size options for each data source
# These are example values and might need adjustment based on actual source capabilities
SIZE_OPTIONS_MAP = {
    "Danbooru": ["Original", "Large (2000px+)", "Medium (1000-1999px)", "Small (<1000px)"],
    "Zerochan": ["Original", "Large", "Medium", "Small"],  # Zerochan sizes are often by tags like 'Wallpaper'
    "Safebooru": ["Original", "Large", "Medium", "Small"],
    "Gelbooru": ["Original", "Large", "Medium", "Small"],
    "WallHaven": ["Original", "1920x1080", "2560x1440", "3840x2160", "Custom"], # Wallhaven supports various resolutions
    "Konachan": ["Original", "Large", "Medium", "Small"],
    "KonachanNet": ["Original", "Large", "Medium", "Small"],
    "Lolibooru": ["Original", "Large", "Medium", "Small"],
    "Yande": ["Original", "Large", "Medium", "Small"],
    "Rule34": ["Original", "Large", "Medium", "Small"],
    "HypnoHub": ["Original", "Large", "Medium", "Small"],
    "Paheal": ["Original", "Large", "Medium", "Small"],
    "AnimePictures (Broken)": [], # No options for broken source
    "Duitang": ["Original", "Large", "Medium", "Small"], # Duitang is more about collections
    "Pixiv": ["original", "large", "medium", "square_medium"],
    "Derpibooru": ["full", "large", "medium", "small", "thumb"],
}

DEFAULT_SIZE_MAP = {
    "Danbooru": "Original",
    "Zerochan": "Original",
    "Safebooru": "Original",
    "Gelbooru": "Original",
    "WallHaven": "Original",
    "Konachan": "Original",
    "KonachanNet": "Original",
    "Lolibooru": "Original",
    "Yande": "Original",
    "Rule34": "Original",
    "HypnoHub": "Original",
    "Paheal": "Original",
    "AnimePictures (Broken)": None,
    "Duitang": "Original",
    "Pixiv": "large",
    "Derpibooru": "large",
}

# 数据源列表
SOURCE_LIST = [
    "Danbooru",
    "Zerochan",
    "Safebooru",
    "Gelbooru",
    "WallHaven",
    "Konachan",
    "KonachanNet",
    "Lolibooru",
    "Yande",
    "Rule34",
    "HypnoHub",
    "Paheal",
    "AnimePictures (Broken)",  # Marked as broken
    "Duitang",
    "Pixiv",
    "Derpibooru"
]

# 更新数据源选择函数
def get_sources():
    return Crawler.get_sources()


# 更新爬取任务函数
def start_crawl(source_name, tags, limit, size, strict):
    return Crawler.start_crawl(source_name, tags, limit, size, strict)


# 数据处理函数
def apply_actions(source, actions):
    if "NoMonochrome" in actions and hasattr(source, "attach"):
        source = source.attach(NoMonochromeAction())
    if "FilterSimilar" in actions and hasattr(source, "attach"):
        source = source.attach(FilterSimilarAction())
    return source


# 导出函数
def export_data(
    source, output_dir, save_meta, exporter_type, hf_repo=None, hf_token=None
):
    if exporter_type == "SaveExporter":
        exporter = SaveExporter(
            output_dir=output_dir,
            no_meta=not save_meta,
            save_params={"format": "PNG"},  # 确保图像格式为 PNG
        )
    elif exporter_type == "TextualInversionExporter":
        exporter = TextualInversionExporter(
            output_dir=output_dir,
            clear=True,
        )
    elif exporter_type == "HuggingFaceExporter":
        if not hf_repo or not hf_token:
            return "HuggingFaceExporter requires 'hf_repo' and 'hf_token'."
        exporter = HuggingFaceExporter(
            repository=hf_repo,
            hf_token=hf_token,
            repo_type="dataset",
        )
    else:
        return f"Unsupported exporter type: {exporter_type}"

    for item in source:
        exporter.export_item(item)
        if save_meta:
            # 保存作者信息到与图片同名的文本文件
            author = item.meta.get("author", "Unknown")
            image_name = item.meta.get("filename", "unknown").rsplit(".", 1)[0]
            with open(
                f"{output_dir}/{image_name}.txt", "w", encoding="utf-8"
            ) as meta_file:
                meta_file.write(f"Author: {author}\n")

    return "Data exported successfully."


# WebUI 启动函数
def launch_webui():
    def process(
        source_name,
        tags,
        limit,
        size,
        strict,
        actions,
        output_dir,
        save_meta,
        exporter_type,
        hf_repo,
        hf_token,
    ):
        logger.info(f"Starting crawl with source: {source_name}, tags: {tags}")
        source, message = start_crawl(source_name, tags, limit, size, strict)
        if source is None:
            logger.error(f"Crawl failed: {message}")
            return message

        logger.info(f"Crawl succeeded. Number of items: {len(source)}")
        logger.info(f"Exporting data to: {output_dir}")

        source = apply_actions(source, actions)
        result = export_data(
            source, output_dir, save_meta, exporter_type, hf_repo, hf_token
        )

        logger.info(f"Export result: {result}")
        return result

    with gr.Blocks() as demo:
        gr.Markdown("# Dataset Cat WebUI")

        available_sources = get_sources()
        initial_source = available_sources[0] if available_sources else None

        with gr.Row():
            source_name = gr.Dropdown(
                choices=available_sources,
                value=initial_source,
                label="Data Source"
            )
            tags = gr.Textbox(label="Tags (comma-separated)")

        initial_sizes_for_dropdown = []
        initial_value_for_size_dropdown = None
        if initial_source:
            initial_sizes_for_dropdown = SIZE_OPTIONS_MAP.get(initial_source, [])
            if initial_sizes_for_dropdown: # If there are size options for the initial source
                desired_initial_default_size = DEFAULT_SIZE_MAP.get(initial_source)
                if desired_initial_default_size in initial_sizes_for_dropdown:
                    initial_value_for_size_dropdown = desired_initial_default_size
                else:
                    initial_value_for_size_dropdown = initial_sizes_for_dropdown[0] # Fallback to first
            # If initial_sizes_for_dropdown is empty, initial_value_for_size_dropdown remains None

        with gr.Row():
            limit = gr.Slider(1, 100, value=10, step=1, label="Limit")
            size = gr.Dropdown(
                choices=initial_sizes_for_dropdown,
                value=initial_value_for_size_dropdown,
                label="Image Size"
            )
            strict = gr.Checkbox(label="Strict Mode (Zerochan only)")
        actions = gr.CheckboxGroup(["NoMonochrome", "FilterSimilar"], label="Actions")
        output_dir = gr.Textbox(label="Output Directory")
        save_meta = gr.Checkbox(label="Save Metadata")
        exporter_type = gr.Dropdown(
            ["SaveExporter", "TextualInversionExporter", "HuggingFaceExporter"],
            label="Exporter Type",
        )
        hf_repo = gr.Textbox(label="HuggingFace Repo (optional)")
        hf_token = gr.Textbox(label="HuggingFace Token (optional)", type="password")
        result = gr.Textbox(label="Result", interactive=False)

        # Update size options based on the selected source
        def update_size_options(selected_source_name):
            sizes = SIZE_OPTIONS_MAP.get(selected_source_name, []) # Default to [] if source not in map
            
            actual_value_for_dropdown = None
            if sizes: # If there are any choices for this source
                desired_default_from_map = DEFAULT_SIZE_MAP.get(selected_source_name) # Might be None
                if desired_default_from_map in sizes:
                    actual_value_for_dropdown = desired_default_from_map
                else:
                    # If desired default is not in sizes (or is None), pick the first available size
                    actual_value_for_dropdown = sizes[0] 
            # If sizes is empty, actual_value_for_dropdown remains None

            return gr.update(choices=sizes, value=actual_value_for_dropdown)

        # Bind the function to the source_name change event
        source_name.change(
            update_size_options,
            inputs=[source_name],
            outputs=[size],
        )

        submit = gr.Button("Start")
        submit.click(
            process,
            inputs=[
                source_name,
                tags,
                limit,
                size,
                strict,
                actions,
                output_dir,
                save_meta,
                exporter_type,
                hf_repo,
                hf_token,
            ],
            outputs=result,
        )

    demo.launch()
