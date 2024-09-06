import csv
import pickle
import numpy as np
import pandas as pd
from sklearn.metrics import top_k_accuracy_score
import scipy.special
import argparse

# Utility Functions (as provided before)
def get_marginal_indexes(actions, mode):
    vi = []
    for v in range(actions[mode].max() + 1):
        vals = actions[actions[mode] == v].index.values
        if len(vals) > 0:
            vi.append(vals)
        else:
            vi.append(np.array([0]))
    return vi

def marginalize(probs, indexes):
    mprobs = []
    for ilist in indexes:
        mprobs.append(probs[:, ilist].sum(1))
    return np.array(mprobs).T

def generate_label_map():
    print("Preprocess ek100 action label space")
    vn_list = []
    mapping_vn2narration = {}
    for f in [
        '/home/ec2-user/environment/AVION/datasets/EK100/epic-kitchens-100-annotations/EPIC_100_train.csv',
        '/home/ec2-user/environment/AVION/datasets/EK100/epic-kitchens-100-annotations/EPIC_100_validation.csv',
    ]:
        csv_reader = csv.reader(open(f))
        _ = next(csv_reader)  # skip the header
        for row in csv_reader:
            vn = '{}:{}'.format(int(row[10]), int(row[12]))
            narration = row[8]
            if vn not in vn_list:
                vn_list.append(vn)
            if vn not in mapping_vn2narration:
                mapping_vn2narration[vn] = [narration]
            else:
                mapping_vn2narration[vn].append(narration)
    vn_list = sorted(vn_list)
    print('# of action= {}'.format(len(vn_list)))
    mapping_vn2act = {vn: i for i, vn in enumerate(vn_list)}
    labels = [list(set(mapping_vn2narration[vn_list[i]])) for i in range(len(mapping_vn2act))]
    print(labels[:5])
    return labels, mapping_vn2act

# Main Script to calculate binary top-k accuracy per narration_id for both AVION and TSN
def evaluate_model_performance(pickle_file, val_metadata):
    # Load model results
    with open(pickle_file, "rb") as f:
        model_results = pickle.load(f)

    # Generate the label map and mapping
    labels, mapping_vn2act = generate_label_map()

    # Map actions to verbs and nouns
    mapping_act2v = {i: int(vn.split(':')[0]) for (vn, i) in mapping_vn2act.items()}
    mapping_act2n = {i: int(vn.split(':')[1]) for (vn, i) in mapping_vn2act.items()}

    # Handle AVION format
    if 'logits' in model_results:
        # Extract logits, probabilities, and targets from the model results
        all_logits = model_results['logits']
        all_probs = scipy.special.softmax(all_logits, axis=1)
        all_targets = model_results['targets']

        # Calculate binary top-1 and top-5 accuracy for each narration_id
        avion_top1_action = (np.argsort(all_probs, axis=1)[:, -1:] == all_targets[:, None]).astype(float)
        avion_top5_action = (np.argsort(all_probs, axis=1)[:, -5:] == all_targets[:, None]).astype(float).sum(axis=1, keepdims=True)

        actions = pd.DataFrame.from_dict({'verb': mapping_act2v.values(), 'noun': mapping_act2n.values()})
        vi = get_marginal_indexes(actions, 'verb')
        ni = get_marginal_indexes(actions, 'noun')

        verb_scores = marginalize(all_probs, vi)
        noun_scores = marginalize(all_probs, ni)
        target_to_verb = np.array([mapping_act2v[a] for a in all_targets.tolist()])
        target_to_noun = np.array([mapping_act2n[a] for a in all_targets.tolist()])

        avion_top1_verb = (np.argsort(verb_scores, axis=1)[:, -1:] == target_to_verb[:, None]).astype(float)
        avion_top5_verb = (np.argsort(verb_scores, axis=1)[:, -5:] == target_to_verb[:, None]).astype(float).sum(axis=1, keepdims=True)

        avion_top1_noun = (np.argsort(noun_scores, axis=1)[:, -1:] == target_to_noun[:, None]).astype(float)
        avion_top5_noun = (np.argsort(noun_scores, axis=1)[:, -5:] == target_to_noun[:, None]).astype(float).sum(axis=1, keepdims=True)

        # Prepare data for CSV
        results = pd.DataFrame({
            'narration_id': val_metadata['narration_id'],
            'avion_top1_action': avion_top1_action.flatten(),
            'avion_top5_action': avion_top5_action.flatten(),
            'avion_top1_verb': avion_top1_verb.flatten(),
            'avion_top5_verb': avion_top5_verb.flatten(),
            'avion_top1_noun': avion_top1_noun.flatten(),
            'avion_top5_noun': avion_top5_noun.flatten(),
        })

    # Handle TSN format
    elif 'verb_output' in model_results and 'noun_output' in model_results:
        narration_id = model_results['narration_id']
        verb_output = model_results['verb_output']
        noun_output = model_results['noun_output']

        # Calculate probabilities from logits
        verb_probs = scipy.special.softmax(verb_output, axis=1)
        noun_probs = scipy.special.softmax(noun_output, axis=1)

        # Extract ground truth verb and noun classes
        targets = val_metadata.set_index('narration_id')
        verb_targets = targets.loc[narration_id, 'verb_class'].values
        noun_targets = targets.loc[narration_id, 'noun_class'].values

        # Calculate binary top-1 and top-5 accuracy for verbs and nouns
        top1_verb = (np.argsort(verb_probs, axis=1)[:, -1:] == verb_targets[:, None]).astype(float)
        top5_verb = (np.argsort(verb_probs, axis=1)[:, -5:] == verb_targets[:, None]).astype(float).sum(axis=1, keepdims=True)

        top1_noun = (np.argsort(noun_probs, axis=1)[:, -1:] == noun_targets[:, None]).astype(float)
        top5_noun = (np.argsort(noun_probs, axis=1)[:, -5:] == noun_targets[:, None]).astype(float).sum(axis=1, keepdims=True)

        # For TSN, action is usually not available directly as a combined class, but you can combine top-1 verb and noun predictions to calculate action accuracy
        top1_action = (top1_verb * top1_noun).astype(float)
        top5_action = (top5_verb * top5_noun).astype(float)

        # Prepare data for CSV
        results = pd.DataFrame({
            'narration_id': narration_id,
            'tsn_top1_action': top1_action.flatten(),
            'tsn_top5_action': top5_action.flatten(),
            'tsn_top1_verb': top1_verb.flatten(),
            'tsn_top5_verb': top5_verb.flatten(),
            'tsn_top1_noun': top1_noun.flatten(),
            'tsn_top5_noun': top5_noun.flatten(),
        })

    else:
        raise ValueError("Unsupported model results format.")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process model results")
    parser.add_argument('--augment', action=argparse.BooleanOptionalAction, required=False, help='With augmentations.')
    args = parser.parse_args()


    if args.augment:
        val_metadata_path = "/home/ec2-user/environment/my-dissertation/augmentation-pipeline/out/augmentated_segments.csv"
        avion_results_path = '/home/ec2-user/environment/AVION/results/quality_all_results.pt'
        tsn_results_path = '/home/ec2-user/environment/C1-Action-Recognition-TSN-TRN-TSM/results/quality_all_results.pt'
    else:
        val_metadata_path = "/home/ec2-user/environment/data-estimator/base_quality.csv"
        avion_results_path = '/home/ec2-user/environment/AVION/results/quality_results.pt'
        tsn_results_path = '/home/ec2-user/environment/C1-Action-Recognition-TSN-TRN-TSM/results/quality_results.pt'
   
    # Load validation metadata
    val_metadata = pd.read_csv(val_metadata_path)
    avion_results = evaluate_model_performance(
        avion_results_path, 
        val_metadata)
    tsn_results = evaluate_model_performance(
        tsn_results_path, 
        val_metadata
    )
    
    val_metadata = pd.merge(val_metadata, tsn_results, on='narration_id')
    val_metadata = pd.merge(val_metadata, avion_results, on='narration_id')
    # tracking_df = pd.concat([tracking_df, df], ignore_index=True)
    # Save to CSV
    output_csv = '/home/ec2-user/environment/data-estimator/model_all_results.csv'
    val_metadata.to_csv(output_csv, index=False)
    print(f"Results saved to {output_csv}")

# if __name__ == "__main__":
#     # Example usage
#     pickle_file = "./quality_results.pt"
#     val_metadata_file = "/home/ec2-user/environment/C1-Action-Recognition-TSN-TRN-TSM/base_quality.csv"
#     evaluate_model_performance(pickle_file, val_metadata_file)
