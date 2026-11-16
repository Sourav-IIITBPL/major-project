"""Compiled Decision Tree for compiled_predictor_asic_csa52.py."""


def predict_strategy(feats: dict) -> str:
    if feats['hamming_weight'] <= 18.5000:
        if feats['bit_length'] <= 384.0000:
            if feats['hamming_weight'] <= 13.0000:
                return 'Binary'
            else:
                if feats['wnaf_weight'] <= 14.5000:
                    if feats['longest_zero_run'] <= 96.0000:
                        return 'VLIM'
                    else:
                        return 'VLIM'
                else:
                    return 'Binary'
        else:
            return 'VLIM'
    else:
        if feats['wnaf_weight'] <= 35.0000:
            if feats['bit_length'] <= 384.0000:
                if feats['longest_one_run'] <= 2.5000:
                    return 'VLIM'
                else:
                    if feats['longest_wnaf_zero_run'] <= 29.0000:
                        return 'NAF'
                    else:
                        return 'NAF'
            else:
                return 'VLIM'
        else:
            if feats['hamming_weight'] <= 40.0000:
                return 'VLIM'
            else:
                return 'VLIM'
