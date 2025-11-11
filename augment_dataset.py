import random

def mutate_sequence(seq, mutation_rate=0.02):
    bases = ['A', 'T', 'G', 'C', 'N']
    seq_list = list(seq)
    num_mutations = max(1, int(len(seq) * mutation_rate))
    positions = random.sample(range(len(seq)), num_mutations)
    for pos in positions:
        seq_list[pos] = random.choice(bases)
    return ''.join(seq_list)

def reverse_complement(seq):
    complement = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G', 'N': 'N'}
    return ''.join(complement.get(base, base) for base in reversed(seq))

def augment_dataset(input_file, output_file, multiplier=3):
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    header = lines[0]
    sequences = [line.strip().split('\t') for line in lines[1:] if line.strip()]
    
    augmented = []
    for seq, label in sequences:
        augmented.append((seq, label))
        for _ in range(multiplier - 1):
            method = random.choice(['mutate', 'reverse'])
            if method == 'mutate':
                augmented.append((mutate_sequence(seq), label))
            else:
                augmented.append((reverse_complement(seq), label))
    
    with open(output_file, 'w') as f:
        f.write(header)
        for seq, label in augmented:
            f.write(f"{seq}\t{label}\n")
    
    print(f"Original: {len(sequences)}, Augmented: {len(augmented)}")

if __name__ == "__main__":
    augment_dataset('dataset/human.txt', 'dataset/human_augmented.txt', multiplier=3)
