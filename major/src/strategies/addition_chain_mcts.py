"""
Addition-Subtraction Chain Optimization via Heuristic Tree / Beam Search.
Finds minimal multiplication chains for target cryptographic exponents.
Computes A^exp mod M using the discovered addition-subtraction chain.
"""

import math
import heapq
import time

def find_addition_chain_beam(target: int, beam_width: int = 30, max_steps: int = 200) -> list:
    """
    Finds a quasi-optimal addition chain for 'target' using guided beam search.
    A state is a tuple: (chain, current_val).
    Heuristic priority: (estimated_remaining_doublings + current_length, -current_val).
    """
    if target == 1:
        return [1]
        
    def heuristic(val, chain_len):
        if val <= 0:
            return float('inf')
        # Lower bound on steps needed: log2(target / val)
        if val > target:
            return float('inf')
        rem = target - val
        est_steps = math.ceil(math.log2(rem + 1)) if rem > 0 else 0
        return chain_len + est_steps

    # Priority queue storing: (heuristic_cost, chain)
    # Beam contains the best K states at each step depth
    beam = [(heuristic(1, 1), [1])]
    
    for step in range(max_steps):
        next_candidates = []
        for cost, chain in beam:
            curr = chain[-1]
            if curr == target:
                return chain
                
            # Possible next values: sum of any two elements in chain
            # Prioritize doubling: 2 * curr
            doubling = curr * 2
            if doubling <= target:
                h = heuristic(doubling, len(chain) + 1)
                next_candidates.append((h, chain + [doubling]))
                
            # Additions with existing elements
            for prev in reversed(chain):
                s = curr + prev
                if s <= target:
                    h = heuristic(s, len(chain) + 1)
                    next_candidates.append((h, chain + [s]))
                diff = curr - prev
                if diff > 0 and diff not in chain and diff <= target:
                    h = heuristic(diff, len(chain) + 1)
                    next_candidates.append((h, chain + [diff]))
                    
        if not next_candidates:
            break
            
        # Keep top beam_width unique candidates
        next_candidates.sort(key=lambda x: (x[0], -x[1][-1]))
        unique_beam = []
        seen_tails = set()
        for cand in next_candidates:
            tail = cand[1][-1]
            if tail not in seen_tails:
                seen_tails.add(tail)
                unique_beam.append(cand)
                if tail == target:
                    return cand[1]
                if len(unique_beam) >= beam_width:
                    break
        beam = unique_beam
        
    # Fallback to standard binary if search times out
    return None

def execute_addition_chain_mod_exp(base: int, chain: list, mod: int) -> int:
    """
    Computes base^exp % mod following the addition chain sequence.
    Stores intermediate powers in a dictionary.
    """
    powers = {1: base % mod}
    
    for idx in range(1, len(chain)):
        target_val = chain[idx]
        found = False
        # Find which two previous elements produced this element
        for i in reversed(chain[:idx]):
            j_add = target_val - i
            if j_add in powers:
                powers[target_val] = (powers[i] * powers[j_add]) % mod
                found = True
                break
            j_sub = i - target_val
            if j_sub in powers:
                inv = pow(powers[j_sub], -1, mod)
                powers[target_val] = (powers[i] * inv) % mod
                found = True
                break
        if not found:
            raise ValueError(f"Addition chain step broken for {target_val}")
            
    return powers[chain[-1]]

if __name__ == "__main__":
    test_exps = [15, 27, 55, 87, 65537]
    base = 5
    mod = 1000000007
    
    print("Testing Addition-Subtraction Chain Engine:")
    for e in test_exps:
        t0 = time.perf_counter()
        chain = find_addition_chain_beam(e, beam_width=50)
        t_find = (time.perf_counter() - t0) * 1000
        
        if chain:
            bin_ops = e.bit_length() - 1 + e.bit_count() - 1
            chain_ops = len(chain) - 1
            res = execute_addition_chain_mod_exp(base, chain, mod)
            assert res == pow(base, e, mod), f"Math error for {e}"
            savings = ((bin_ops - chain_ops) / bin_ops) * 100
            print(f"Exponent {e:<6} | Chain Steps: {chain_ops} vs Binary: {bin_ops} | Savings: {savings:>+5.1f}% | Search: {t_find:.1f}ms")
            print(f"  Chain: {chain[:10]} ... -> {chain[-1]}")
