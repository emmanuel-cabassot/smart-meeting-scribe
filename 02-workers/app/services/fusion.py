def assign_speaker(start, end, annotation):
    """
    Algorithme de Fusion : Trouve le locuteur majoritaire sur un segment.
    """
    max_overlap = 0
    assigned_speaker = "Unknown"
    
    # Sécurité anti-crash
    if not hasattr(annotation, 'itertracks'):
        return "Speaker_Error"

    for turn, _, speaker in annotation.itertracks(yield_label=True):
        intersection_start = max(start, turn.start)
        intersection_end = min(end, turn.end)
        overlap = intersection_end - intersection_start
        
        if overlap > 0 and overlap > max_overlap:
            max_overlap = overlap
            assigned_speaker = speaker
            
    return assigned_speaker

def merge_transcription_diarization(segments, annotation, speaker_mapping=None):
    """
    Fusionne la liste des segments Whisper avec l'annotation Pyannote.
    
    Args:
        segments: Liste des segments Whisper
        annotation: Annotation de diarisation Pyannote
        speaker_mapping: Dictionnaire optionnel {SPEAKER_00: "Emmanuel", ...}
    """
    formatted_segments = []
    
    for segment in segments:
        speaker = assign_speaker(segment.start, segment.end, annotation)
        
        # Appliquer le mapping si disponible
        if speaker_mapping and speaker in speaker_mapping:
            speaker = speaker_mapping[speaker]
        
        formatted_segments.append({
            "start": round(segment.start, 2),
            "end": round(segment.end, 2),
            "text": segment.text.strip(),
            "speaker": speaker
        })
        
    return formatted_segments
