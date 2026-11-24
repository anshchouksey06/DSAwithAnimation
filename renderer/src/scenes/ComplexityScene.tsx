import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';

interface Comparison {
  approach: string;
  time: string;
  space: string;
}

interface ComplexityProps {
  comparisons?: Comparison[];
  bruteForceTime?: string;
  bruteForceSpace?: string;
  optimizedTime?: string;
  optimizedSpace?: string;
}

export const ComplexityScene: React.FC<ComplexityProps> = ({
  comparisons,
  bruteForceTime,
  bruteForceSpace,
  optimizedTime,
  optimizedSpace
}) => {
  const activeComparisons: Comparison[] = comparisons || [
    { approach: "Brute Force", time: bruteForceTime || "O(n²)", space: bruteForceSpace || "O(1)" },
    { approach: "Optimized", time: optimizedTime || "O(n)", space: optimizedSpace || "O(n)" }
  ];
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
        marginBottom: '80px',
        color: '#f8fafc',
        textAlign: 'center'
      }}>
        Complexity Comparison
      </div>

      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '40px',
        width: '90%'
      }}>
        {activeComparisons.map((item, idx) => {
          const cardSpring = spring({ frame: frame - idx * 10, fps, from: 0.8, to: 1 });
          const isOptimized = idx === 1;

          return (
            <div key={idx} style={{
              backgroundColor: isOptimized ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
              border: isOptimized ? '4px solid #10b981' : '3px solid #ef4444',
              borderRadius: '32px',
              padding: '48px 60px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              transform: `scale(${cardSpring})`,
              boxShadow: isOptimized ? '0 10px 40px rgba(16, 185, 129, 0.2)' : 'none'
            }}>
              <div>
                <div style={{
                  fontSize: '48px',
                  fontWeight: 800,
                  color: isOptimized ? '#34d399' : '#f87171',
                  marginBottom: '10px'
                }}>
                  {item.approach}
                </div>
                <div style={{ fontSize: '32px', color: '#94a3b8' }}>
                  {isOptimized ? 'Single pass with hash table' : 'Nested nested pair checking'}
                </div>
              </div>

              <div style={{ textAlign: 'right' }}>
                <div style={{
                  fontSize: '52px',
                  fontWeight: 900,
                  color: '#fff',
                  marginBottom: '10px'
                }}>
                  Time: <span style={{ color: isOptimized ? '#34d399' : '#f87171' }}>{item.time}</span>
                </div>
                <div style={{
                  fontSize: '36px',
                  fontWeight: 600,
                  color: '#94a3b8'
                }}>
                  Aux Space: {item.space}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
