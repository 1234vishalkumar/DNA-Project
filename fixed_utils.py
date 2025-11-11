def parse_dna_input(file_content, filename):
    """Parse DNA input from various formats"""
    try:
        # Convert bytes to string if needed
        if isinstance(file_content, bytes):
            try:
                content = file_content.decode('utf-8')
            except UnicodeDecodeError:
                content = file_content.decode('latin-1')
        else:
            content = str(file_content)
        
        content = content.strip()
        
        # Auto-detect format based on content and filename
        if filename.lower().endswith(('.fasta', '.fa')) or content.startswith('>'):
            # Parse FASTA format manually
            sequences = []
            lines = content.split('\n')
            current_seq = ""
            
            for line in lines:
                line = line.strip()
                if line.startswith('>'):
                    if current_seq:
                        sequences.append(clean_sequence(current_seq))
                        current_seq = ""
                else:
                    current_seq += line
            
            if current_seq:
                sequences.append(clean_sequence(current_seq))
            
            return sequences[0] if sequences else None
        
        else:
            # Parse as plain text sequence
            cleaned = clean_sequence(content)
            return cleaned if len(cleaned) > 10 else None  # Minimum length check
    
    except Exception as e:
        print(f"Error parsing DNA input: {e}")
        return None

def clean_sequence(seq):
    return ''.join([s for s in seq.upper() if s in "ACGT"])