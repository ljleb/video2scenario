# Copyright (C) 2023 by Artem Khrapov (kabachuha)
# Read LICENSE for usage terms.

import requests, json
from video_chop import chop_video
from chops_to_folder_dataset import move_the_files
from video_blip2_preprocessor.preprocess import PreProcessVideos

# Setting up the LLM interactions

HOST = 'localhost:5000'
URI = f'http://{HOST}/api/v1/generate' #TODO: support multimodal interactions
API_KEY = "" # OpenAI or any other Auth key

with open('args.json', 'r') as cfg_file:
    args = json.loads(cfg_file.read())

def textgen(prompt):
    with open('config.json', 'r') as cfg_file:
        config = json.loads(cfg_file.read())

    assert config is not None
    config.pop('host')

    request = config
    request['prompt'] = prompt

    print(request)

    result = ''

    try:
        response = requests.post(URI, json=request, headers={'Content-Type':'application/json', 'Authorization': 'Bearer {}'.format(API_KEY)})
        if response.status_code == 200:
            result = response.json()['results'][0]['text']
            print(result)
        else:
            raise Exception(f'Request returned status {response.status_code}')
    except Exception as e:
            print(e)
            raise e
    return result

def process_video():
    #clear video
    #chop_video
    #caption video
    ...

def run():
    print("Hey!")

# Gradio interface setup if launching as an app

if __name__ == "__main__":
    import gradio as gr

    with gr.Blocks(analytics_enabled=False) as interface:
        with gr.Row().style(equal_height=False, variant='compact'):
            with gr.Column(scale=1, variant='panel'):
                with gr.Tabs():
                    with gr.Tab(label='Level selector'):
                        # Depth slider
                        # 0 - L max
                        with gr.Row(variant='compact'):
                            descr_depth = gr.Slider(label="Depth", value=0, minimum=0, maximum=12, step=1, interactive=True)
                        # Batch slider
                        with gr.Row(variant='compact'):
                            descr_subdiv = gr.Slider(label="Subdivision", value=0, minimum=0, maximum=144, step=1, interactive=True)
                        with gr.Row(variant='compact'):
                            # textbox with selected description
                            descr = gr.TextArea(label="Description", lines=4, interactive=True)
                        with gr.Row(variant='compact'):
                            descr_load = gr.Button('Refresh', variant='primary')
                            descr_regen_btn = gr.Button('Regenerate description')
                            descr_save_btn = gr.Button('Save description')
                    with gr.Tab(label='Textgen config'):
                        with gr.Row(variant='compact'):
                            # settings path
                            sttn_path = gr.Textbox(label="Settings path", interactive=True)
                            # load settings
                            sttn_load_btn = gr.Button('Load settings')
                            # save settings
                            sttn_save_btn = gr.Button('Save settings')
                        with gr.Tabs():
                            with gr.Tab(label='Sampling settings'):
                                gr.Markdown('Todo (see config.json)')
                                with gr.Row():
                                    textgen_url = gr.Textbox(label="Textgen URL", value="http://localhost:5000/api/v1/generate", interactive=True)
                                    textgen_key = gr.Textbox(label="API key, if private", value="", interactive=True)
                                with gr.Row():
                                    textgen_new_words = gr.Slider(label='Max new words', value=80, step=1, interactive=True, minimum=1, maximum=300)
                                    textgen_temperature = gr.Slider(label='Temperature (~creativity)', value=0.45, step=0.01, interactive=True, minimum=0, maximum=1.99)
                                with gr.Row():
                                    textgen_top_p = gr.Slider(label='Top P', value=1, step=0.01, interactive=True, minimum=0, maximum=1)
                                    textgen_typical_p = gr.Slider(label='Typical P', value=1, step=0.01, interactive=True, minimum=0, maximum=1)
                                    textgen_top_k = gr.Slider(label='Top K', value=0, step=1, interactive=True, minimum=0, maximum=100)
                                with gr.Row():
                                    textgen_repetition_penalty = gr.Slider(label='Repetition penalty', value=1.15, step=0.01, interactive=True, minimum=0, maximum=2)
                                    textgen_encoder_repetition_penalty = gr.Slider(label='Repetition penalty', value=1, step=0.01, interactive=True, minimum=0, maximum=2)
                                    textgen_length_penalty = gr.Slider(label='Length penalty', value=1, step=0.01, interactive=True, minimum=0, maximum=2)
                            with gr.Tab(label='Master prompts'):
                                with gr.Row(variant='compact'):
                                    master_scene = gr.TextArea(label="Scene", lines=5, interactive=True)
                                with gr.Row(variant='compact'):
                                    master_synopsis = gr.TextArea(label="Synopsis", lines=5, interactive=True)
                            with gr.Tab(label='Frame captioning'):
                                gr.Markdown('Frame autocaptioning (BLIP2) settings')
                                gr.Markdown('Uses bisection for more than 1 prompt/division')
                                with gr.Row(variant='compact'):
                                    autocap_frames = gr.Slider(label='Autocaptioned frames', value=2, step=1, interactive=True, minimum=1, maximum=12) # will be populater with L
                                    autocap_padding = gr.Radio(label='Padding', value='left', choices=["left", "right", "none"], interactive=True)
                                with gr.Row(variant='compact'):
                                    autocap_min_words = gr.Slider(label="Min words", minimum=1, maximum=15, value=15, step=1, interactive=True)
                                    autocap_max_words = gr.Slider(label="Max words", minimum=10, maximum=45, value=30, step=1, interactive=True)

                    with gr.Tab(label='Batch processing'):
                        gr.Markdown('Process a list of .json captioning config files:')
                        with gr.Row(variant='compact'):
                            cfgs_folder = gr.Textbox(label="Configs folder", interactive=True)
                            cfgs_start = gr.Button(value='Start', variant='primary')
                        gr.Markdown('Process a folder of videos using the current settings:')
                        with gr.Row(variant='compact'):
                            vids_folder = gr.Textbox(label="Videos folder", interactive=True)
                            vids_start = gr.Button(value='Start', variant='primary')
            with gr.Column(scale=1, variant='panel'):
                with gr.Tabs(selected=1):
                    with gr.Tab(label="Keyframes viewer"):
                        # list of keyframes at each selected layer
                        keyframes = gr.Gallery()
                        keyframes_vid64 = gr.HTML("") # placeholder for previewable Video Base64 HTML
                    with gr.Tab(id=1, label="Video splitter"):
                        with gr.Row(variant='compact'):
                            chop_skip_frames = gr.Slider(label='How many frames to drop from source', value=0, step=0.02, interactive=True, minimum=0, maximum=0.99)
                        # L / path to video
                            chop_L = gr.Number(label="L (each level division number)", value=12, precision=0, interactive=True)
                        with gr.Row(variant='compact'):
                            # splitted video folderpath
                            chop_whole_vid_path = gr.Textbox(label="Path to the whole video, if not splitted yet", interactive=True)
                            chop_split_path = gr.Textbox(label="Splitted video folderpath", interactive=True)
                            chop_trg_path = gr.Textbox(label="Target folder dataset path", interactive=True)
                            # will chop if not exist
                        with gr.Row(variant='compact'):
                            # chop video
                            do_chop = gr.Checkbox(label='(re)chop video', value=True, interactive=True)
                            # clear info checkbox
                            do_clear = gr.Checkbox(label='clear info', interactive=True)
                        with gr.Row(variant='compact'):
                            # caption keyframes checkbox
                            do_caption = gr.Checkbox(label='caption keyframes', value=True, interactive=True)
                            # textgen checkbox
                            do_textgen = gr.Checkbox(label='textgen scenes', value=True, interactive=True)
                        with gr.Row(variant='compact'):
                            # export checkbox
                            do_export = gr.Checkbox(label='export to dataset', interactive=True)
                            do_delete = gr.Checkbox(label='delete after export', interactive=True)
                        with gr.Row(variant='compact'):
                            with gr.Column(variant='compact'):
                                with gr.Row(variant='compact'):
                                    # apply to
                                    # whole
                                    # this level
                                    #
                                    do_apply_to = gr.Radio(label="Apply to:", value="Whole video", choices=["Whole video", "This level"], interactive=True)
                            with gr.Column(variant='compact'):
                                with gr.Row(variant='compact'):
                                    # generate button
                                    do_btn = gr.Button('Load/Process', variant="primary")

                    with gr.Tab(label="Video export settings"):
                        exp_overwrite_dims = gr.Checkbox(label="Override dims", value=True, interactive=True)
                        exp_w = gr.Slider(label="Width", value=768, minimum=64, maximum=1920, step=64, interactive=True)
                        exp_h = gr.Slider(label="Height", value=432, minimum=64, maximum=1920, step=64, interactive=True)
                        exp_overwrite_fps = gr.Checkbox(label="Override fps", value=False, interactive=True)
                        exp_fps = gr.Slider(label="FPS", value=12, minimum=1, maximum=144, step=1, interactive=True)

    interface.launch(share=args["share"], server_name=args['server_name'], server_port=args['server_port'])
