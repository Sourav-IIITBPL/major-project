"""Static Compiled Decision Tree Predictor – Auto-Generated."""

# DO NOT EDIT MANUALLY. Re-run models/train_all_models.py to regenerate.


def predict_strategy(feats: dict) -> str:
    if feats['hamming_weight'] <= 350.0000:
        if feats['longest_one_run'] <= 12.5000:
            if feats['zero_density'] <= 0.4297:
                return 'wNAF'
            else:
                if feats['hamming_weight'] <= 265.0000:
                    return 'Binary'
                else:
                    return 'Binary'
        else:
            if feats['hamming_weight'] <= 134.5000:
                return 'Binary'
            else:
                if feats['hamming_weight'] <= 161.0000:
                    return 'NAF'
                else:
                    return 'NAF'
    else:
        if feats['wnaf_weight'] <= 259.5000:
            if feats['wnaf_weight'] <= 218.0000:
                if feats['hamming_weight'] <= 2151.5000:
                    return 'NAF'
                else:
                    return 'VLIM'
            else:
                if feats['wnaf_weight'] <= 257.5000:
                    return 'wNAF'
                else:
                    return 'NAF'
        else:
            if feats['wnaf_zero_density'] <= 0.7468:
                if feats['wnaf_zero_density'] <= 0.7464:
                    return 'wNAF'
                else:
                    return 'NAF'
            else:
                if feats['zero_density'] <= 0.5006:
                    return 'VLIM'
                else:
                    return 'VLIM'
