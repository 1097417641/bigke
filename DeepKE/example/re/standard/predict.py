import os
import sys
import torch
import logging
import hydra
from hydra import utils
from deepke.relation_extraction.standard.tools import Serializer
from deepke.relation_extraction.standard.tools import _serialize_sentence, _convert_tokens_into_index, _add_pos_seq, _handle_relation_data , _lm_serialize
import matplotlib.pyplot as plt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from deepke.relation_extraction.standard.utils import load_pkl, load_csv
import deepke.relation_extraction.standard.models as models


logger = logging.getLogger(__name__)


def _preprocess_data(data, cfg):
    
    relation_data = load_csv(os.path.join(cfg.cwd, cfg.data_path, 'relation.csv'), verbose=False)
    rels = _handle_relation_data(relation_data)

    if cfg.model_name != 'lm':
        vocab = load_pkl(os.path.join(cfg.cwd, cfg.out_path, 'vocab.pkl'), verbose=False)
        cfg.vocab_size = vocab.count
        serializer = Serializer(do_chinese_split=cfg.chinese_split)
        serial = serializer.serialize

        _serialize_sentence(data, serial, cfg)
        _convert_tokens_into_index(data, vocab)
        _add_pos_seq(data, cfg)
    else:
        _lm_serialize(data,cfg)

    return data, rels


def _get_predict_instance(cfg,data):

    sentence = data['sentence']
    head = data['head']
    head_type = data['head_type']
    tail = data['tail']
    tail_type = data['tail_type']
    instance = dict()
    instance['sentence'] = sentence.strip()
    instance['head'] = head.strip()
    instance['tail'] = tail.strip()
    if head_type.strip() == '' or tail_type.strip() == '':
        cfg.replace_entity_with_type = False
        instance['head_type'] = 'None'
        instance['tail_type'] = 'None'
    else:
        instance['head_type'] = head_type.strip()
        instance['tail_type'] = tail_type.strip()

    return instance


def pred(cfg,data):
    cwd = utils.get_original_cwd()
    # cwd = cwd[0:-5]
    cfg.cwd = cwd
    cfg.pos_size = 2 * cfg.pos_limit + 2

    # get predict instance
    instance = _get_predict_instance(cfg,data)
    data = [instance]
    # preprocess data
    data, rels = _preprocess_data(data, cfg)

    # model
    __Model__ = {
        'cnn': models.PCNN,
        'rnn': models.BiLSTM,
        'transformer': models.Transformer,
        'gcn': models.GCN,
        'capsule': models.Capsule,
        'lm': models.LM,
    }

    # 最好在 cpu 上预测
    cfg.use_gpu = False
    if cfg.use_gpu and torch.cuda.is_available():
        device = torch.device('cuda', cfg.gpu_id)
    else:
        device = torch.device('cpu')

    model = __Model__[cfg.model_name](cfg)
    model.load(cfg.fp, device=device)
    model.eval()

    x = dict()
    x['word'], x['lens'] = torch.tensor([data[0]['token2idx']]), torch.tensor([data[0]['seq_len']])
    
    if cfg.model_name != 'lm':
        x['head_pos'], x['tail_pos'] = torch.tensor([data[0]['head_pos']]), torch.tensor([data[0]['tail_pos']])
        if cfg.model_name == 'cnn':
            if cfg.use_pcnn:
                x['pcnn_mask'] = torch.tensor([data[0]['entities_pos']])
        if cfg.model_name == 'gcn':
            # 没找到合适的做 parsing tree 的工具，暂时随机初始化
            adj = torch.empty(1,data[0]['seq_len'],data[0]['seq_len']).random_(2)
            x['adj'] = adj


    for key in x.keys():
        x[key] = x[key].to(device)

    with torch.no_grad():
        y_pred = model(x)
        y_pred = torch.softmax(y_pred, dim=-1)[0]
        prob = y_pred.max().item()
        prob_rel = list(rels.keys())[y_pred.argmax().item()]
        logger.info(f"\"{data[0]['head']}\" 和 \"{data[0]['tail']}\" 在句中关系为：\"{prob_rel}\"，置信度为{prob:.2f}。")
        return prob_rel

@hydra.main(config_path="conf", config_name="config",strict=False)
def tr1ple(cfg):
    a = {}
    data={"sentence":'abc为枣庄市xxx科长',"head":'abc',"head_type":'人物',"tail":'xxx',"tail_type":'机构'}
    relation = pred(cfg,data)
    a[data['head_type']] = data['head']
    a['relation'] = relation
    a[data['tail_type']] = data['tail']
    print(a)


if __name__ == '__main__':
     tr1ple()
