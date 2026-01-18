
function getSpeakerColor(speaker: string): string {
    const colors = [
        "bg-blue-500/10 text-blue-400 border-blue-500/20",
        "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
        "bg-amber-500/10 text-amber-400 border-amber-500/20",
        "bg-violet-500/10 text-violet-400 border-violet-500/20",
        "bg-pink-500/10 text-pink-400 border-pink-500/20",
        "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
    ];

    if (!speaker) return colors[0];

    let hash = 0;
    for (let i = 0; i < speaker.length; i++) {
        hash = speaker.charCodeAt(i) + ((hash << 5) - hash);
    }
    const index = Math.abs(hash) % colors.length;
    return `Speaker: "${speaker}" -> Index: ${index} -> Color: ${colors[index]}`;
}

console.log(getSpeakerColor("Speaker 0"));
console.log(getSpeakerColor("Speaker 1"));
console.log(getSpeakerColor("SPEAKER_00"));
console.log(getSpeakerColor("SPEAKER_01"));
console.log(getSpeakerColor("Homme"));
console.log(getSpeakerColor("Femme"));
