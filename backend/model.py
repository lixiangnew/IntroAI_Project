import torch
import os
import gc
import time
import base64
import io
import re
from diffusers import FluxPipeline, BitsAndBytesConfig, FluxTransformer2DModel
from transformers import T5EncoderModel

# ================= 配置区域=================
# 请确保服务器环境能访问这些路径，或者根据实际情况修改
MODEL_ROOT = "D:/Flux_Project/models/FLUX.1-dev"
LORA_PATH = "D:/Flux_Project/models/lora/v2/flux_shanshui_v2_rank64-12.safetensors"
USE_LORA = True
LORA_SCALE = 0.8
# SEED = 8888 # 在API中通常不固定种子，以便每次生成不同结果，若需固定可取消注释

# 设置环境变量
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

# ================= 模型初始化 (全局加载一次) =================
print(">>> [System] 正在初始化模型，请稍候...")

try:
    # 1. 加载 T5 Encoder
    quant_config = BitsAndBytesConfig(
        load_in_8bit=True,
        llm_int8_threshold=6.0
    )
    t5_path = os.path.join(MODEL_ROOT, "text_encoder_2")
    t5_encoder = T5EncoderModel.from_pretrained(
        t5_path,
        quantization_config=quant_config,
        torch_dtype=torch.bfloat16
    )

    # 2. 加载 Pipeline 外壳
    pipe = FluxPipeline.from_pretrained(
        MODEL_ROOT,
        text_encoder_2=t5_encoder,
        transformer=None,
        torch_dtype=torch.bfloat16
    )

    # 3. 加载主 Transformer
    transformer = FluxTransformer2DModel.from_pretrained(
        os.path.join(MODEL_ROOT, "transformer"),
        torch_dtype=torch.bfloat16
    )
    pipe.transformer = transformer

    # 4. 加载 LoRA
    if USE_LORA:
        print(f">>> [System] 加载 LoRA: {LORA_PATH}")
        pipe.load_lora_weights(LORA_PATH)

    # 5. 显存优化
    print(">>> [System] 启用显存优化...")
    pipe.enable_sequential_cpu_offload()
    pipe.vae.enable_slicing()
    pipe.vae.enable_tiling()

    print(">>> [System] 模型初始化完成！")

except Exception as e:
    print(f"❌ 模型加载失败: {e}")
    # 这里可以抛出异常或者设置 pipe 为 None，在 generate 时处理
    pipe = None


# ================= 辅助函数 =================

def extract_clip_prompt(text):
    """
    从 test_lora.py 移植的 Prompt 处理函数
    """
    stop_words = {
        "a", "an", "the", "in", "on", "at", "with", "by", "of", "to", "from",
        "is", "are", "featuring", "composition", "rendered", "style", "into",
        "down", "for", "define", "structure", "and", "one", "two", "three", "four",
        "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen",
        "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty",
        "fifty", "sixty", "seventy", "eighty", "ninety"
    }

    text_clean = re.sub(r'[^\w\s,]', '', text.lower())
    words = text_clean.replace(',', ' ').split()
    keywords = [w for w in words if w not in stop_words]
    clip_prompt = ", ".join(keywords[:30])
    return clip_prompt


# ================= 核心生成函数 =================

def generate_painting(prompt_text):
    if pipe is None:
        print("Error: Model not initialized.")
        return None

    print(f"\n--- 收到生成请求 ---")
    print(f"Prompt: {prompt_text[:100]}...")

    # 1. 准备 Prompt
    short_prompt = extract_clip_prompt(prompt_text)

    # 2. 清理显存
    gc.collect()
    torch.cuda.empty_cache()

    # 3. 设置生成参数
    # 如果需要随机种子：
    generator = torch.Generator("cuda")
    # 如果需要固定种子：
    # generator = torch.Generator("cuda").manual_seed(8888)

    joint_attention_kwargs = {"scale": LORA_SCALE} if USE_LORA else None

    # 4. 执行推理
    try:
        image = pipe(
            prompt=short_prompt,  # 给 CLIP
            prompt_2=prompt_text,  # 给 T5
            height=1024,
            width=1024,
            guidance_scale=3.5,
            num_inference_steps=20,
            max_sequence_length=512,
            generator=generator,
            joint_attention_kwargs=joint_attention_kwargs
        ).images[0]

        # 5. 转换为 Base64
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")  # 保证质量，使用 PNG
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        print("✅ 图片生成并编码完成")
        return img_str

    except Exception as e:
        print(f"❌ 生成过程出错: {e}")
        return None