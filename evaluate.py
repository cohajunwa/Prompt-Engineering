import sacrebleu
from sklearn.metrics.pairwise import cosine_similarity
from transformers import RobertaTokenizer, RobertaModel
import torch

_tokenizer = None
_model = None

def _load_codebert():
    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        _tokenizer = RobertaTokenizer.from_pretrained("microsoft/codebert-base")
        _model = RobertaModel.from_pretrained("microsoft/codebert-base")
        _model.eval()
    return _tokenizer, _model

def get_cosine_similarity(text1, text2):
    if not text1.strip() or not text2.strip():
        raise ValueError("Empty input.")

    tokenizer, model = _load_codebert()
    inputs = tokenizer([text1, text2], padding=True, truncation=True, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)
        embeddings = outputs.last_hidden_state[:, 0, :]

    return float(cosine_similarity(embeddings[0:1], embeddings[1:2])[0][0])

def get_bleu_4_score(response_1, response_2):
  return sacrebleu.corpus_bleu([response_1], [[response_2]]).score
