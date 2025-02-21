import re
import fire
from openai import AsyncAzureOpenAI, AzureOpenAI

def extract_xml(text: str, tag: str) -> str:
    """
    Extracts the content of the specified XML tag from the given text. Used for parsing structured responses 

    Args:
        text (str): The text containing the XML.
        tag (str): The XML tag to extract content from.

    Returns:
        str: The content of the specified XML tag, or an empty string if the tag is not found.
    """
    match = re.search(f'<{tag}>(.*?)</{tag}>', text, re.DOTALL)
    return match.group(1) if match else ""

def check_answer(answer_id, gt_ans):
    """
    Validates extracted answer IDs against ground-truth answers.

    Args:
        answer_id (str): The answer ID(s) extracted from the response.
        gt_ans (list): A list of ground-truth answer IDs.

    Returns:
        float: A score between 0 and 1 based on answer correctness.
    """
    # contains at most two numbers
    number_strings = re.findall(r'\d+', answer_id)
    answer_ids = list(set([int(num) for num in number_strings]))
    if len(answer_ids) > 2 or len(answer_ids) == 0: return 0 # incorrect format
    elif len(gt_ans) == 1: # acc. if single GT
        if len(answer_ids) == 1: 
            if gt_ans[0] == answer_ids[0]: return 1
            else: return 0
        if gt_ans[0] in answer_ids: return 0.5
        else: return 0
    else: # acc. if two GT
        s = 0
        for ans in answer_ids:
            if ans in gt_ans: s += 1
        return s/2

def llm_judge(data):
    """
    Uses AzureOpenAI to evaluate and match elements from the provided data.
    
    Args:
        data (list): List of response dictionaries containing sentences and options.
    
    Returns:
        list: Updated data with LLM-generated answers.
    """
    client = AzureOpenAI(
        api_key=api_key,  
        api_version=api_version,
        base_url=f"{api_base}/openai/deployments/{deployment_name}"
    )
    llm_ans = []
    for i, ans_data in tqdm(enumerate(data), total=len(data)):
        prompt = """You are given a sentence referring to one/a pair of elements. Match the element(s) referred in the sentence with the given options. Return the ID(s) of the matched option(s).
    Sentence:\n"""
        try:
            prompt += extract_xml(ans_data["response"], "ans").strip()
        except:
            prompt += extract_xml(ans_data["response"][0], "ans").strip()
        prompt += "\n\nOptions:\n"
        prompt += question_data[ans_data["i"]]['descs']
        prompt += f"""\n\nYour answer must follow the following format:
    <id>
    "[ID1]" or "[ID1],[ID2]" <-- one problematic element ID, or two problematic element IDs from given options separated by comma
    </id>
    """
        messages=[
                    { "role": "user", "content": [  
                        { 
                            "type": "text", 
                            "text": prompt,
                        }
                    ] } 
                ]
        response = client.chat.completions.create(
                    model="o1-mini",
                    messages=messages
                )
        response_texts = [choice.message.content.strip() for choice in response.choices]
        llm_matched_ids = extract_xml(response_texts[0], "id").strip()
        data[i]["llm_ans"] = llm_matched_ids
    return data


def eval(
    eval_setting : str = "open", # open, mcq
    model : str = "qwen2.5_vl", # model name
):
    """
    Evaluates the model's performance across different data sources and settings.
    
    Args:
        eval_setting (str): Type of evaluation ('open' or 'mcq').
        model (str): Name of the model being evaluated.
    """
    src_id = {
        "web": [],
        "office": [],
        "poster": []
    }
    with open(f"questions_{eval_setting}.json", 'r') as f:
        questions = json.load(f)
        for i, q in enumerate(questions):
            if q['source'] == "web page":
                src_id["web"].append(i)
            elif q['source'] == "poster":
                src_id["poster"].append(i)
            else: src_id["office"].append(i)

    ans_file = f"response_file/{model}_{eval_setting}.json"
    with open(ans_file, 'r') as f:
        if ans_file.endswith(".json"):
            data = json.load(f)
        else:
            data = []
            for line in f:
                data.append(json.loads(line.strip()))

    if eval_setting == "open":
        data = llm_judge(data)

    for eval_src in ["web", "office", "poster", "overall"]:
        if eval_src != "overall":
            total_question = len(src_id[eval_src])
        else: total_question = 534
        score = []
        for response in data:
            if eval_src != "overall":
                if response['i'] not in src_id[eval_src]: # Skip if the response doesn't belong to the current source
                    continue
            if "open" in eval_setting:
                answer_id = response["llm_ans"]
            else: 
                answer = response["response"][0]
                try:
                    answer_id = extract_xml(answer, "ans").strip()
                except:
                    answer_id = ""
            gt_ans = response["gt_ans"]
            score.append(check_answer(answer_id, gt_ans))
        print(f"{ans_file}: {eval_src}")
        print(f"score: {sum(score)/total_question}")

if __name__ == "__main__":
    fire.Fire(eval)