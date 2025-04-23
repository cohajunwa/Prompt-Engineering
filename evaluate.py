import sacrebleu
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

_codebert = None

def _get_codebert_model():
  """
  Function to load model only once (avoid overhead)
  """
  global _codebert
  if _codebert is None:
      _codebert = SentenceTransformer("microsoft/codebert-base")
  return _codebert

def get_cosine_similarity(response1, response2):
    embeddings = _get_codebert_model().encode([response1, response2])
    return cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]

def get_bleu_4_score(response_1, response_2):
  return sacrebleu.corpus_bleu([response_1], [[response_2]]).score