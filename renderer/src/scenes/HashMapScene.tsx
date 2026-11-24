import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';

interface Step {
  step: number;
  i: number;
  val: number;
  complement: number;
  found: boolean;
  map?: Record<string, number>;
  result?: number[];
}

interface HashMapProps {
  values?: number[];
  array?: number[];
  target?: number;
  steps?: Step[];
  mapEntries?: Array<{ key: string; val: number }>;
  activeStep?: number;
  complement?: number;
  foundMatch?: boolean;
  resultIndices?: number[];
}

export const HashMapScene: React.FC<HashMapProps> = ({
  values,
  array,
  target = 9,
  steps
}) => {
  const displayValues = array || values || [2, 7, 11, 15];
  const activeSteps = steps || [
    { step: 1, i: 0, val: displayValues[0] || 2, complement: target - (displayValues[0] || 2), found: false, map: { [String(displayValues[0] || 2)]: 0 } },
    { step: 2, i: 1, val: displayValues[1] || 7, complement: target - (displayValues[1] || 7), found: true, result: [0, 1] }
  ];
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Switch between step 1 and step 2 based on frame
  const currentStepIdx = frame < 300 ? 0 : Math.min(1, activeSteps.length - 1);
  const currentStep = activeSteps[currentStepIdx] || activeSteps[0];

  const mapScale = spring({ frame: frame % 300, fps, from: 0.9, to: 1 });

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
        fontSize: '56px',
        fontWeight: 800,
        marginBottom: '16px',
        color: '#f8fafc'
      }}>
        Hash Map Dry-Run (Step {currentStep.step} of {steps.length})
      </div>

      <div style={{
        backgroundColor: '#064e3b',
        color: '#6ee7b7',
        border: '2px solid #10b981',
        borderRadius: '9999px',
        padding: '10px 32px',
        fontSize: '30px',
        fontWeight: 700,
        marginBottom: '50px'
      }}>
        O(1) Complement Lookup
      </div>

      {/* Array row with active index indicator */}
      <div style={{
        display: 'flex',
        gap: '24px',
        marginBottom: '60px'
      }}>
        {displayValues.map((v, idx) => {
          const isActive = idx === currentStep.i;
          return (
            <div key={idx} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <div style={{
                height: '40px',
                fontSize: '28px',
                fontWeight: 700,
                color: isActive ? '#facc15' : 'transparent'
              }}>
                {isActive ? 'current ↓' : ''}
              </div>
              <div style={{
                width: '140px',
                height: '140px',
                borderRadius: '24px',
                backgroundColor: isActive ? 'rgba(250, 204, 21, 0.2)' : '#1e293b',
                border: isActive ? '4px solid #facc15' : '3px solid #475569',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                fontSize: '56px',
                fontWeight: 800,
                color: '#fff'
              }}>
                {v}
              </div>
              <div style={{ marginTop: '10px', fontSize: '28px', color: '#64748b' }}>
                idx: {idx}
              </div>
            </div>
          );
        })}
      </div>

      {/* Complement Computation Card */}
      <div style={{
        backgroundColor: '#0f172a',
        border: '2px solid #334155',
        borderRadius: '24px',
        padding: '30px 60px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '16px',
        marginBottom: '60px',
        width: '80%'
      }}>
        <div style={{ fontSize: '36px', color: '#94a3b8' }}>
          Formula: <span style={{ color: '#fff' }}>complement = target - nums[{currentStep.i}]</span>
        </div>
        <div style={{ fontSize: '48px', fontWeight: 800, color: '#38bdf8' }}>
          {target} - {currentStep.val} = <span style={{ color: '#f472b6' }}>{currentStep.complement}</span>
        </div>
        <div style={{
          fontSize: '34px',
          fontWeight: 700,
          color: currentStep.found ? '#34d399' : '#fbbf24'
        }}>
          {currentStep.found ? `✓ Found complement in hash map at index 0!` : `✗ Not in map yet -> Store { ${currentStep.val}: ${currentStep.i} }`}
        </div>
      </div>

      {/* Hash Map State Visualizer */}
      <div style={{
        width: '80%',
        backgroundColor: '#1e293b',
        borderRadius: '28px',
        border: '3px solid #475569',
        padding: '36px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        transform: `scale(${mapScale})`
      }}>
        <div style={{ fontSize: '34px', fontWeight: 700, color: '#a78bfa', marginBottom: '24px' }}>
          Hash Map (seen values → indices)
        </div>
        <div style={{
          display: 'flex',
          gap: '24px',
          justifyContent: 'center',
          flexWrap: 'wrap'
        }}>
          {currentStepIdx === 0 ? (
            <div style={{
              backgroundColor: '#0f172a',
              border: '2px solid #a855f7',
              borderRadius: '18px',
              padding: '18px 36px',
              fontSize: '36px',
              fontWeight: 700,
              color: '#c084fc'
            }}>
              2 → index 0
            </div>
          ) : (
            <div style={{
              backgroundColor: '#064e3b',
              border: '3px solid #10b981',
              borderRadius: '18px',
              padding: '24px 48px',
              fontSize: '42px',
              fontWeight: 800,
              color: '#34d399',
              boxShadow: '0 0 30px rgba(16, 185, 129, 0.4)'
            }}>
              Match: indices [0, 1] sum to 9!
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
