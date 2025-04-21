import sacrebleu

def get_bleu_4_score(response_1, response_2):
  return sacrebleu.corpus_bleu([response_1], [[response_2]]).score

def compute_bleu_between_models(responses):
    models = list(responses.keys())
    if len(models) != 2:
        raise ValueError("Expected exactly two model responses for BLEU computation.")
    
    return get_bleu_4_score(responses[models[0]], responses[models[1]])