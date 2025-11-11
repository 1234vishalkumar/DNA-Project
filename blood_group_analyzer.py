"""
Blood Group Detection from DNA Sequence
Based on ABO and Rh blood group genes
"""

def detect_blood_group(dna_sequence):
    """
    Detect blood group from DNA sequence
    This is a simplified model based on common genetic markers
    """
    sequence = dna_sequence.upper()
    
    # ABO gene markers (simplified)
    # These are example patterns - in reality, blood group determination is more complex
    abo_markers = {
        'A': ['GTGCAC', 'CGTGCA', 'GCGTGC', 'TGCGTG'],
        'B': ['GTGCTG', 'CTGGTG', 'TGCTGG', 'GGCTGT'],
        'O': ['GTGCAG', 'CAGGTG', 'TGCAGG', 'GGCAGT']
    }
    
    # Rh factor markers (simplified)
    rh_positive_markers = ['CCTAGG', 'CCTGGG', 'GCCCTG', 'TCCCTG']
    rh_negative_markers = ['CCTAGC', 'CCTGGC', 'GCCCTC', 'TCCCTC']
    
    # Count marker occurrences
    abo_scores = {'A': 0, 'B': 0, 'O': 0}
    
    for blood_type, markers in abo_markers.items():
        for marker in markers:
            abo_scores[blood_type] += sequence.count(marker)
    
    # Determine ABO type
    if abo_scores['A'] > abo_scores['B'] and abo_scores['A'] > abo_scores['O']:
        if abo_scores['B'] > abo_scores['O']:
            abo_type = 'AB'
        else:
            abo_type = 'A'
    elif abo_scores['B'] > abo_scores['A'] and abo_scores['B'] > abo_scores['O']:
        abo_type = 'B'
    else:
        abo_type = 'O'
    
    # Determine Rh factor
    rh_positive_count = sum(sequence.count(marker) for marker in rh_positive_markers)
    rh_negative_count = sum(sequence.count(marker) for marker in rh_negative_markers)
    
    if rh_positive_count > rh_negative_count:
        rh_factor = '+'
    else:
        rh_factor = '-'
    
    blood_group = f"{abo_type}{rh_factor}"
    
    # Calculate confidence based on marker strength
    total_markers = sum(abo_scores.values()) + rh_positive_count + rh_negative_count
    confidence = min(0.95, (total_markers / 20) * 0.8 + 0.2)  # Scale confidence
    
    return {
        'blood_group': blood_group,
        'abo_type': abo_type,
        'rh_factor': rh_factor,
        'confidence': round(confidence, 2),
        'marker_counts': {
            'A_markers': abo_scores['A'],
            'B_markers': abo_scores['B'],
            'O_markers': abo_scores['O'],
            'Rh_positive': rh_positive_count,
            'Rh_negative': rh_negative_count
        },
        'interpretation': get_blood_group_info(blood_group)
    }

def get_blood_group_info(blood_group):
    """Get information about the blood group"""
    info = {
        'A+': {
            'can_donate_to': ['A+', 'AB+'],
            'can_receive_from': ['A+', 'A-', 'O+', 'O-'],
            'frequency': '35.7%',
            'description': 'Second most common blood type'
        },
        'A-': {
            'can_donate_to': ['A+', 'A-', 'AB+', 'AB-'],
            'can_receive_from': ['A-', 'O-'],
            'frequency': '6.3%',
            'description': 'Relatively rare blood type'
        },
        'B+': {
            'can_donate_to': ['B+', 'AB+'],
            'can_receive_from': ['B+', 'B-', 'O+', 'O-'],
            'frequency': '8.5%',
            'description': 'Less common blood type'
        },
        'B-': {
            'can_donate_to': ['B+', 'B-', 'AB+', 'AB-'],
            'can_receive_from': ['B-', 'O-'],
            'frequency': '1.5%',
            'description': 'Rare blood type'
        },
        'AB+': {
            'can_donate_to': ['AB+'],
            'can_receive_from': ['All blood types'],
            'frequency': '3.4%',
            'description': 'Universal recipient'
        },
        'AB-': {
            'can_donate_to': ['AB+', 'AB-'],
            'can_receive_from': ['AB-', 'A-', 'B-', 'O-'],
            'frequency': '0.6%',
            'description': 'Rarest blood type'
        },
        'O+': {
            'can_donate_to': ['O+', 'A+', 'B+', 'AB+'],
            'can_receive_from': ['O+', 'O-'],
            'frequency': '37.4%',
            'description': 'Most common blood type'
        },
        'O-': {
            'can_donate_to': ['All blood types'],
            'can_receive_from': ['O-'],
            'frequency': '6.6%',
            'description': 'Universal donor'
        }
    }
    
    return info.get(blood_group, {
        'can_donate_to': ['Unknown'],
        'can_receive_from': ['Unknown'],
        'frequency': 'Unknown',
        'description': 'Blood group information not available'
    })

def analyze_blood_compatibility(donor_group, recipient_group):
    """Check if donor blood is compatible with recipient"""
    compatibility_matrix = {
        'O-': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
        'O+': ['O+', 'A+', 'B+', 'AB+'],
        'A-': ['A-', 'A+', 'AB-', 'AB+'],
        'A+': ['A+', 'AB+'],
        'B-': ['B-', 'B+', 'AB-', 'AB+'],
        'B+': ['B+', 'AB+'],
        'AB-': ['AB-', 'AB+'],
        'AB+': ['AB+']
    }
    
    compatible = recipient_group in compatibility_matrix.get(donor_group, [])
    
    return {
        'compatible': compatible,
        'donor': donor_group,
        'recipient': recipient_group,
        'status': 'Compatible' if compatible else 'Incompatible',
        'risk_level': 'Safe' if compatible else 'Dangerous - Do Not Transfuse'
    }
