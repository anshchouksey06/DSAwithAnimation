import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';

interface SummaryProps {
  title?: string;
  problemTitle?: string;
  points?: string[];
  takeaway?: string;
  result_indices?: number[];
  resultIndices?: number[];
}

export const SummaryScene: React.FC<SummaryProps> = ({
  title,
  problemTitle,
  points,
  takeaway,
  result_indices,
  resultIndices
}) => {
  const displayTitle = problemTitle ? `${problemTitle} Summary` : (title || "Key Takeaways");
  const displayPoints = points || (takeaway ? [
    takeaway,
    "Algorithm verified against edge cases",
    "Time and space constraints verified"
  ] : [
    "Complement = Target - Current Value",
    "Hash Map provides O(1) average lookup",
    "Time reduced from O(n²) to O(n)"
  ]);
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <div style={{
      width: '100%',
      height: '100%',
      background: 'linear-gradient(180deg, #0b0f19 0%, #111827 50%, #030712 100%)',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: 'Inter, system-ui, sans-serif',
      color: '#fff',
      padding: '70px',
      boxSizing: 'border-box'
    }}>
      <div style={{
        fontSize: '72px',
        fontWeight: 900,
        marginBottom: '70px',
        background: 'linear-gradient(135deg, #38bdf8 0%, #a855f7 100%)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        textAlign: 'center'
      }}>
        {displayTitle}
      </div>

      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '36px',
        width: '90%',
        marginBottom: '90px'
      }}>
        {displayPoints.map((pt, idx) => {
          const ptSpring = spring({ frame: frame - idx * 12, fps, from: 0.8, to: 1 });
          const ptOpacity = interpolate(frame - idx * 12, [0, 15], [0, 1], { extrapolateRight: 'clamp' });

          return (
            <div key={idx} style={{
              display: 'flex',
              alignItems: 'center',
              gap: '30px',
              backgroundColor: '#1e293b',
              border: '2px solid #334155',
              borderRadius: '24px',
              padding: '36px 48px',
              transform: `scale(${ptSpring})`,
              opacity: ptOpacity
            }}>
              <div style={{
                width: '56px',
                height: '56px',
                borderRadius: '50%',
                backgroundColor: '#3b82f6',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                fontSize: '32px',
                fontWeight: 900,
                color: '#fff',
                flexShrink: 0
              }}>
                {idx + 1}
              </div>
              <div style={{ fontSize: '40px', fontWeight: 600, color: '#f1f5f9' }}>
                {pt}
              </div>
            </div>
          );
        })}
      </div>

      <div style={{
        backgroundColor: 'rgba(56, 189, 248, 0.1)',
        border: '3px solid #38bdf8',
        borderRadius: '30px',
        padding: '30px 60px',
        fontSize: '44px',
        fontWeight: 800,
        color: '#38bdf8'
      }}>
        Final Answer: [{result_indices.join(', ')}]
      </div>
    </div>
  );
};
