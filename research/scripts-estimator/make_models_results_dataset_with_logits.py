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

# Main Script to calculate raw logits and combine them with quality_score
def evaluate_model_performance(pickle_file, val_metadata):
    # Load model results
    with open(pickle_file, "rb") as f:
        model_results = pickle.load(f)

    # Generate the label map and mapping
    labels, mapping_vn2act = generate_label_map()

    # Map actions to verbs and nouns
    mapping_act2v = {i: int(vn.split(':')[0]) for (vn, i) in mapping_vn2act.items()}
    mapping_act2n = {i: int(vn.split(':')[1]) for (vn, i) in mapping_vn2act.items()}

    # Prepare an empty DataFrame to hold results
    results = pd.DataFrame()

# Handle AVION format
    if 'logits' in model_results:
        # Extract logits directly
        all_logits = model_results['logits']
        all_targets = model_results['targets']
        
        # Apply softmax to get probabilities
        all_probs = scipy.special.softmax(all_logits, axis=1)
        
        # Assuming you have the mapping from actions to verbs and nouns (as shown earlier):
        mapping_act2v = {i: int(vn.split(':')[0]) for (vn, i) in mapping_vn2act.items()}
        mapping_act2n = {i: int(vn.split(':')[1]) for (vn, i) in mapping_vn2act.items()}

        # Map actions to their corresponding verb and noun classes
        target_to_verb = np.array([mapping_act2v[a] for a in all_targets])
        target_to_noun = np.array([mapping_act2n[a] for a in all_targets])

        # Get the probabilities corresponding to the correct class
        action_probs = all_probs[np.arange(all_probs.shape[0]), all_targets]

        # If not available separately, you can marginalize action probabilities to get verb and noun probabilities.
        actions = pd.DataFrame.from_dict({'verb': mapping_act2v.values(), 'noun': mapping_act2n.values()})
        vi = get_marginal_indexes(actions, 'verb')
        ni = get_marginal_indexes(actions, 'noun')

        verb_probs = marginalize(all_probs, vi)[np.arange(all_probs.shape[0]), target_to_verb]
        noun_probs = marginalize(all_probs, ni)[np.arange(all_probs.shape[0]), target_to_noun]
        
        # Store probabilities for correlation analysis
        results = pd.DataFrame({
            'narration_id': val_metadata['narration_id'],
            'avion_raw_logit_action': action_probs,
            'avion_raw_logit_verb': verb_probs,
            'avion_raw_logit_noun': noun_probs,
        })


    # Handle TSN format
    elif 'verb_output' in model_results and 'noun_output' in model_results:
        narration_id = model_results['narration_id']
        verb_output = model_results['verb_output']
        noun_output = model_results['noun_output']

        # Apply softmax to get probabilities
        verb_probs = scipy.special.softmax(verb_output, axis=1)
        noun_probs = scipy.special.softmax(noun_output, axis=1)

        # Extract ground truth verb and noun classes
        targets = val_metadata.set_index('narration_id')
        verb_targets = targets.loc[narration_id, 'verb_class'].values
        noun_targets = targets.loc[narration_id, 'noun_class'].values

        # Get the probabilities corresponding to the correct class
        verb_probs = verb_probs[np.arange(verb_probs.shape[0]), verb_targets]
        noun_probs = noun_probs[np.arange(noun_probs.shape[0]), noun_targets]

        # For TSN, action probabilities can be estimated by combining verb and noun probabilities
        action_probs = verb_probs * noun_probs  # or any other combination logic you prefer

        # Store probabilities for correlation analysis
        results = pd.DataFrame({
            'narration_id': narration_id,
            'tsn_raw_logit_verb': verb_probs,
            'tsn_raw_logit_noun': noun_probs,
            'tsn_raw_logit_action': action_probs,
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
    
    # Combine results with validation metadata
    val_metadata = pd.merge(val_metadata, tsn_results, on='narration_id')
    val_metadata = pd.merge(val_metadata, avion_results, on='narration_id')

    # Save to CSV
    output_csv = '/home/ec2-user/environment/data-estimator/model_results_with_logits.csv'
    val_metadata.to_csv(output_csv, index=False)
    print(f"Results saved to {output_csv}")

# Note: In the final correlation study, you will be correlating these raw logits directly with `quality_score`.
