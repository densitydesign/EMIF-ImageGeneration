#this parameters are useful to upscale the img while keeping the general sense of the img

img2img_data = {
    "negative_prompt_for_image_prior":True,
    "motion_scale":127,
    "fps":5,
    "guidance_scale":5,

    "steps":30,

    "controls":[
        {
            "targetBlocks": None,
            "downSamplingRate":1,
            "file":"controlnet_tile_1.x_v1.1_f16.ckpt",
            "guidanceStart":0,
            "guidanceEnd":1,
            "noPrompt":False,
            "globalAveragePooling":True,
            "weight":0.5,
            "controlImportance":"balanced"
        }
    ],

    "guiding_frame_noise":0.019999,

    "strength":0.3, #to vary the fidelty of the output to the input img

    "init_images": "",

    "original_width":1024,
    "original_height":1024,
    

    "height": 2048,
    "width": 2048,

    "tiled_decoding":True,
    "decoding_tile_overlap":128,
    "decoding_tile_height":512,
    "decoding_tile_width":512,

    "tiled_diffusion":True,
    "diffusion_tile_width":512,
    "diffusion_tile_height":512,
    "diffusion_tile_overlap":128,

    "target_height":512,
    "target_width":512,

    "mask_blur_outset":0,
    "num_frames":14,
    
    "image_prior_steps":5,
    "stage_2_guidance":1,
    "aesthetic_score":6,
    "negative_original_height":512,
    "refiner_start":0.7,
    "zero_negative_prompt":False,
   
    
    "batch_count":1,

    "hires_fix_width":960,
    "hires_fix_height":960,

    "preserve_original_after_inpaint":False,
    
    
    "guidance_scale":1.5,
    
    "seed": -1,
    
    "loras":[
    {
    "weight":0.7,
    "file":"add_more_details__detail_enhancer___tweaker__lora_f16.ckpt"
    },
    {
    "weight":0.5,
    "file":"sdxl_render_v2.0_lora_f16.ckpt"
    },
    {
    "weight":0.7,
    "file":"tcd_sd_v1.5_lora_f16.ckpt"
    }
    ],
    "refiner_model":"sd_xl_refiner_1.0_f16.ckpt",
    "negative_original_width":512,
    "batch_size":1,
    
    "clip_weight":1,
    
    "sampler":"TCD",
    "negative_aesthetic_score":2.5,
    
    "upscaler_scale": 0,
    "upscaler": None,
    #"start_frame_guidance":1,
   
    "model":"juggernaut_reborn_q6p_q8p.ckpt",
    "hires_fix_strength":0.35,
    "stochastic_sampling_gamma":0.3,
    "sharpness":0,
    "mask_blur":1.5,
    "shift":1,

    "crop_left":20,
    "crop_top":20,
    "clip_skip":1,
    
    "seed_mode":"Scale Alike",
    "stage_2_shift":1,
    "hires_fix": False,

    "prompt": "quality photography, detailed photography, realism",
    "negative_prompt": "Too much contrast, (getty images watermark), (deformities),disfigured, (ugly faces), blurry face, fuzzy faces, (cartoon:2), (painting:2), painting, (from behind), black and white, text, watermark, synthetic image, (incomplete bodies), art, close up, deformed objects, aerial view, darkness"
    
}
