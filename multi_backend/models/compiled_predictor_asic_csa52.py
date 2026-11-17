"""Compiled Decision Tree for compiled_predictor_asic_csa52.py."""


def predict_strategy(feats: dict) -> str:
    if feats['hamming_weight'] <= 57.5000:
        if feats['longest_one_run'] <= 2.5000:
            if feats['zero_density'] <= 0.8819:
                return 'VLIM'
            else:
                if feats['bit_length'] <= 768.0000:
                    if feats['bit_length'] <= 384.0000:
                        return 'Binary'
                    else:
                        return 'Binary'
                else:
                    if feats['longest_one_run'] <= 1.5000:
                        return 'VLIM'
                    else:
                        return 'VLIM'
        else:
            if feats['hamming_weight'] <= 27.5000:
                return 'NAF'
            else:
                return 'VLIM'
    else:
        if feats['wnaf_weight'] <= 36.5000:
            if feats['bit_length'] <= 384.0000:
                if feats['longest_wnaf_zero_run'] <= 19.5000:
                    return 'VLIM'
                else:
                    if feats['wnaf_weight'] <= 26.5000:
                        return 'NAF'
                    else:
                        return 'NAF'
            else:
                if feats['bit_length'] <= 768.0000:
                    return 'VLIM'
                else:
                    return 'VLIM'
        else:
            return 'VLIM'
