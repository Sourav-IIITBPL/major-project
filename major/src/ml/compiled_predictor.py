"""Static Compiled Decision Tree Predictor – Auto-Generated."""

# DO NOT EDIT MANUALLY. Re-run models/train_all_models.py to regenerate.


def predict_strategy(feats: dict) -> str:
    if feats['hamming_weight'] <= 435.0000:
        if feats['longest_one_run'] <= 15.0000:
            if feats['hamming_weight'] <= 244.5000:
                if feats['avg_zero_run'] <= 6.8147:
                    return 'Binary'
                else:
                    return 'Binary'
            else:
                if feats['wnaf_zero_density'] <= 0.7497:
                    return 'Binary'
                else:
                    return 'Binary'
        else:
            if feats['hamming_weight'] <= 239.0000:
                if feats['longest_one_run'] <= 60.5000:
                    return 'NAF'
                else:
                    return 'wNAF'
            else:
                if feats['wnaf_weight'] <= 18.5000:
                    return 'NAF'
                else:
                    return 'wNAF'
    else:
        if feats['wnaf_weight'] <= 504.5000:
            if feats['wnaf_weight'] <= 122.0000:
                if feats['hamming_weight'] <= 1990.5000:
                    return 'NAF'
                else:
                    return 'VLIM'
            else:
                if feats['hamming_weight'] <= 3745.0000:
                    return 'wNAF'
                else:
                    return 'NAF'
        else:
            if feats['longest_one_run'] <= 11.5000:
                if feats['wnaf_zero_density'] <= 0.7517:
                    return 'VLIM'
                else:
                    return 'VLIM'
            else:
                return 'wNAF'
