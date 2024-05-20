txt2img_data = {
    
    "negative_prompt": "(GettyImages watermark),(deformities), disfigured, (ugly faces), blurry face, fuzzy faces, cartoon, paint, painting, (from behind), black and white, text, watermark, (incomplete bodies), art, split-view, close up, deformed objects, aerial view, darkness",
    "seed": -1,
    "strength": 1,

    "steps": 30, #How accurate the img generation (don't go beyond 70 or below 30)
    "batch_count": 1, #How many images to generate
    "batch_size": 1, #How many images to generate consequentially
    "controls": [],
    "loras": [],
    "fps": 5,
    "num_frames": 14,
    "image_prior_steps": 5,
    "image_guidance": 1.5,
    "stochastic_sampling_gamma": 0.3,
    "clip_weight": 1,
    "clip_skip": 1,
    "preserve_original_after_inpaint": False,
    "zero_negative_prompt": False,
    "negative_prompt_for_image_prior": True,

    "hires_fix": True,
    "hires_fix_width": 960,
    "hires_fix_height": 960,
    "hires_fix_strength": 0.3500000, #HIRES %

    "width": 1024,
    "height":1024,

    "original_width": 1024,
    "original_height": 1024,

    "target_width": 1024,
    "target_height": 1024,

    "tiled_decoding": False,
    "tiled_diffusion": False,

    "decoding_tile_width": 640,
    "decoding_tile_height": 640,
    "decoding_tile_overlap": 128,
    "diffusion_tile_width": 1024,
    "diffusion_tile_height": 1024,
    "diffusion_tile_overlap": 128,

    "mask_blur": 1.5,
    "mask_blur_outset": 0,
    
    "guiding_frame_noise": 0.019999,
    "guidance_scale": 5,
    "shift": 1,
    "stage_2_shift": 1,
    "stage_2_guidance": 1,
    "motion_scale": 127,
    "sharpness": 0,

    #integrating the upscaler directly here skips a step
    "upscaler_scale": 2,
    "upscaler": "4x_ultrasharp_f16.ckpt",

    "sampler": "DPM++ 2M Karras",
    "model": "sd_xl_base_1.0_f16.ckpt",
    "refiner_model": "sd_xl_refiner_1.0_f16.ckpt",
    "refiner_start": 0.70, #refiner%

    "aesthetic_score": 6,
    "negative_aesthetic_score": 2.5,
    "seed_mode": "Scale Alike",

    "start_frame_guidance": 1,
    "crop_top": 20,
    "crop_left": 20,
}
