import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';

interface ArraySceneProps {
  values?: number[];
  array?: number[];
  target?: number;
  title?: string;
  label?: string;
  formula?: string;
  highlightIndices?: number[];
}

export const ArrayScene: React.FC<ArraySceneProps> = ({
  values,
  array,
  target = 9,
  title,
  label,
  formula,
  highlightIndices = []
}) => {
  const displayValues = array || values || [2, 7, 11, 15];
  const displayTitle = label || title || "Problem Array";
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <div style={{
      width: '100%',
      height: '100%',
      background: 'linear-gradient(180deg, #0b0f19 0%, #111827 100%)',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: 'Inter, system-ui, sans-serif',
      color: '#fff',
      padding: '60px',
      boxSizing: 'border-box'
    }}>
      <div style={{
        fontSize: '64px',
        fontWeight: 800,
        marginBottom: '60px',
        color: '#f8fafc',
        textAlign: 'center'
      }}>
        {displayTitle}
      </div>

      <div style={{
        backgroundColor: '#1e293b',
        border: '2px solid #38bdf8',
        borderRadius: '24px',
        padding: '24px 60px',
        fontSize: '48px',
        fontWeight: 700,
        color: '#38bdf8',
        marginBottom: '100px',
        boxShadow: '0 10px 30px rgba(56, 189, 248, 0.2)'
      }}>
        Target: <span style={{ color: '#facc15' }}>{target}</span>
      </div>

      {formula && (
        <div style={{
          backgroundColor: '#0f172a',
          border: '2px dashed #a855f7',
          borderRadius: '20px',
          padding: '28px 48px',
          fontSize: '40px',
          fontWeight: 600,
          color: '#c084fc',
          marginBottom: '80px',
          fontFamily: 'Consolas, monospace'
        }}>
          {formula}
        </div>
      )}

      <div style={{
        display: 'flex',
        gap: '30px',
        justifyContent: 'center',
        alignItems: 'center'
      }}>
        {displayValues.map((val, idx) => {
          const itemSpring = spring({ frame: frame - idx * 5, fps, from: 0.5, to: 1 });
          const itemOpacity = interpolate(frame - idx * 5, [0, 10], [0, 1], { extrapolateRight: "clamp" });

          return (
            <div key={idx} style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              transform: `scale(${itemSpring})`,
              opacity: itemOpacity
            }}>
              <div style={{
                width: '180px',
                height: '180px',
                borderRadius: '28px',
                backgroundColor: '#1e293b',
                border: '4px solid #475569',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                fontSize: '72px',
                fontWeight: 800,
                color: '#f1f5f9',
                boxShadow: '0 20px 40px rgba(0,0,0,0.5)'
              }}>
                {val}
              </div>
              <div style={{
                marginTop: '20px',
                fontSize: '36px',
                fontWeight: 600,
                color: '#64748b'
              }}>
                idx: {idx}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
