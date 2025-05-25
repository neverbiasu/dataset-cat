import gradio as gr
from waifuc.source import (
    DanbooruSource,
    ZerochanSource,
    SafebooruSource,
    GelbooruSource,
    WallHavenSource,
    KonachanSource,
    KonachanNetSource,
    LolibooruSource,
    YandeSource,
    Rule34Source,
    HypnoHubSource,
    PahealSource,
    AnimePicturesSource,
    DuitangSource,
)
from waifuc.action import NoMonochromeAction, FilterSimilarAction
from waifuc.export import SaveExporter, TextualInversionExporter, HuggingFaceExporter
from dataset_cat.crawler import Crawler
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
    "AnimePictures",
    "Duitang",
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
        with gr.Row():
            source_name = gr.Dropdown(get_sources(), label="Data Source")
            tags = gr.Textbox(label="Tags (comma-separated)")
        with gr.Row():
            limit = gr.Slider(1, 100, value=10, step=1, label="Limit")
            size = gr.Dropdown(["full", "large"], label="Image Size")
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
