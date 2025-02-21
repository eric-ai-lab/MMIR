# Evaluation Guidelines
We provide detailed instructions for evaluation. To execute our evaluation script, please ensure that the structure of your model outputs is the same as ours.

## Model Inference

Download our [dataset](https://huggingface.co/datasets/rippleripple/MMIR) from huggingface.

Clone the official repo of open-sourced models into the following folder:
* Qwen2.5-VL-7B [[repo]](https://github.com/QwenLM/Qwen2.5-VL) [[checkpoint]](https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct)
* LLaVA-NeXT-7B [[repo]](https://github.com/LLaVA-VL/LLaVA-NeXT) [[checkpoint]](https://huggingface.co/llava-hf/llava-v1.6-mistral-7b-hf)
* InternVL2.5-8B [[repo]](https://github.com/OpenGVLab/InternVL) [[checkpoint]](https://huggingface.co/OpenGVLab/InternVL2_5-8B)
* Phi-3.5-Vision-4B [[repo]](https://github.com/microsoft/Phi-3CookBook) [[checkpoint]](https://huggingface.co/microsoft/Phi-3.5-vision-instruct)

Set up the environment for each open-sourced model as instructed by their original repo and run inference. For API-based models: o1 (1217) and GPT-4o (1120), set up your API key in the provided scripts under the /inference folder.

After setting up, run inference.sh to get model outputs on the question files. Your folder structure should look like this:
    .   
    project-root
    ├── Qwen2.5-VL
    │   └── ...
    ├── LLaVA
    │   └── ...
    └── ...
    │
    ├── questions_open.json
    ├── questions_mcq.json
    ├── response_file
    │   └── qwen2.5_vl_open.jsonl
    │   └── qwen2.5_vl_mcq.jsonl
    │   └── llava_next_open.jsonl
    │   └── llava_next_mcq.jsonl
    │   └── ...

## Get Evaluation results and scores

We use o1-mini (0912) as a LLM judge to process the responses from the open-ended setting (*open.jsonl).

After getting the output, run calculate_score.py to get scores for all models.


