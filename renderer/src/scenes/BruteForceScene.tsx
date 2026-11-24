import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';

interface BruteForceProps {
  values?: number[];
  array?: number[];
  target?: number;
  pointer_i?: number;
  currentI?: number;
  pointer_j?: number;
  currentJ?: number;
  currentSum?: number;
  sum?: number;
  time_complexity?: string;
}

export const BruteForceScene: React.FC<BruteForceProps> = ({
  values,
  array,
  target = 9,
  pointer_i,
  currentI,
  pointer_j,
  currentJ,
  time_complexity = "O(n²)"
}) => {
  const displayValues = array || values || [2, 7, 11, 15];
  const activeI = currentI !== undefined ? currentI : (pointer_i !== undefined ? pointer_i : 0);
  const activeJ = currentJ !== undefined ? currentJ : (pointer_j !== undefined ? pointer_j : 1);
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const isMatch = ((displayValues[activeI] || 0) + (displayValues[activeJ] || 0)) === target;
  const matchPop = spring({ frame: frame - 15, fps, from: 1, to: isMatch ? 1.08 : 1 });

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
        fontSize: '60px',
        fontWeight: 800,
        marginBottom: '20px',
        color: '#f8fafc'
      }}>
        Approach 1: Brute Force
      </div>

      <div style={{
        backgroundColor: '#7f1d1d',
        color: '#fca5a5',
        border: '2px solid #ef4444',
        borderRadius: '9999px',
        padding: '12px 36px',
        fontSize: '32px',
        fontWeight: 700,
        marginBottom: '60px'
      }}>
        Time Complexity: {time_complexity}
      </div>

      {/* Target & Check formula */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '24px',
        fontSize: '52px',
        fontWeight: 700,
        backgroundColor: '#1e293b',
        border: isMatch ? '4px solid #10b981' : '2px solid #475569',
        padding: '24px 60px',
        borderRadius: '28px',
        marginBottom: '100px',
        boxShadow: isMatch ? '0 0 50px rgba(16, 185, 129, 0.4)' : 'none',
        transform: `scale(${matchPop})`
      }}>
        <span style={{ color: '#60a5fa' }}>nums[{activeI}] ({displayValues[activeI]})</span>
        <span style={{ color: '#94a3b8' }}>+</span>
        <span style={{ color: '#f472b6' }}>nums[{activeJ}] ({displayValues[activeJ]})</span>
        <span style={{ color: '#94a3b8' }}>=</span>
        <span style={{ color: isMatch ? '#34d399' : '#f87171' }}>{(displayValues[activeI] || 0) + (displayValues[activeJ] || 0)}</span>
        {isMatch && <span style={{ color: '#34d399', marginLeft: '20px' }}>✓ MATCH!</span>}
      </div>

      {/* Array Boxes */}
      <div style={{
        display: 'flex',
        gap: '30px',
        justifyContent: 'center',
        alignItems: 'center'
      }}>
        {displayValues.map((val, idx) => {
          const isI = idx === activeI;
          const isJ = idx === activeJ;
          let borderColor = '#475569';
          let bgColor = '#1e293b';

          if (isI) {
            borderColor = '#3b82f6';
            bgColor = 'rgba(59, 130, 246, 0.2)';
          } else if (isJ) {
            borderColor = '#ec4899';
            bgColor = 'rgba(236, 72, 153, 0.2)';
          }

          return (
            <div key={idx} style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center'
            }}>
              {/* Pointers above */}
              <div style={{
                height: '60px',
                display: 'flex',
                alignItems: 'center',
                fontSize: '36px',
                fontWeight: 800,
                color: isI ? '#60a5fa' : isJ ? '#f472b6' : 'transparent'
              }}>
                {isI ? 'pointer i ↓' : isJ ? 'pointer j ↓' : ''}
              </div>

              <div style={{
                width: '180px',
                height: '180px',
                borderRadius: '28px',
                backgroundColor: bgColor,
                border: `4px solid ${borderColor}`,
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                fontSize: '72px',
                fontWeight: 800,
                color: '#f1f5f9'
              }}>
                {val}
              </div>

              <div style={{
                marginTop: '16px',
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
