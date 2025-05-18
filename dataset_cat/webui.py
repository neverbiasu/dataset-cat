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


# 数据源选择函数
def get_sources():
    return [
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


# 爬取任务函数
def start_crawl(source_name, tags, limit, size, strict):
    source_mapping = {
        "Danbooru": lambda: DanbooruSource(tags=tags.split(","), min_size=size),
        "Zerochan": lambda: ZerochanSource(tags, select=size, strict=strict),
        "Safebooru": lambda: SafebooruSource(tags=tags.split(","), min_size=size),
        "Gelbooru": lambda: GelbooruSource(tags=tags.split(","), min_size=size),
        "WallHaven": lambda: WallHavenSource(query=tags, select=size),
        "Konachan": lambda: KonachanSource(tags=tags.split(","), min_size=size),
        "KonachanNet": lambda: KonachanNetSource(tags=tags.split(","), min_size=size),
        "Lolibooru": lambda: LolibooruSource(tags=tags.split(","), min_size=size),
        "Yande": lambda: YandeSource(tags=tags.split(","), min_size=size),
        "Rule34": lambda: Rule34Source(tags=tags.split(","), min_size=size),
        "HypnoHub": lambda: HypnoHubSource(tags=tags.split(","), min_size=size),
        "Paheal": lambda: PahealSource(tags=tags.split(",")),
        "AnimePictures": lambda: AnimePicturesSource(tags=tags.split(",")),
        "Duitang": lambda: DuitangSource(keyword=tags, strict=strict),
    }

    if source_name in source_mapping:
        source = source_mapping[source_name]()
        source = source[:limit]
        return source, "Crawl task initialized."
    else:
        return None, f"Unsupported source: {source_name}"


# 数据处理函数
def apply_actions(source, actions):
    if "NoMonochrome" in actions:
        source = source.attach(NoMonochromeAction())
    if "FilterSimilar" in actions:
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
        source, message = start_crawl(source_name, tags, limit, size, strict)
        if source is None:
            return message
        source = apply_actions(source, actions)
        result = export_data(
            source, output_dir, save_meta, exporter_type, hf_repo, hf_token
        )
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
