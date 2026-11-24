import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';

interface IntroProps {
  title?: string;
  subtitle?: string;
  difficulty?: string;
  topic?: string;
}

export const IntroScene: React.FC<IntroProps> = ({
  title = "Two Sum",
  subtitle = "Finding Two Numbers That Add Up to Target",
  difficulty = "Easy",
  topic = "Arrays & Hashing"
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleScale = spring({ frame, fps, from: 0.8, to: 1, config: { damping: 12 } });
  const opacity = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" });
  const badgeSlide = spring({ frame: frame - 10, fps, from: 50, to: 0 });

  return (
    <div style={{
      width: '100%',
      height: '100%',
      background: 'linear-gradient(180deg, #0b0f19 0%, #111827 50%, #030712 100%)',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      color: '#ffffff',
      fontFamily: 'Inter, system-ui, sans-serif',
      padding: '80px',
      boxSizing: 'border-box'
    }}>
      <div style={{
        display: 'flex',
        gap: '20px',
        marginBottom: '60px',
        transform: `translateY(${badgeSlide}px)`,
        opacity
      }}>
        <div style={{
          backgroundColor: '#065f46',
          color: '#34d399',
          padding: '16px 36px',
          borderRadius: '9999px',
          fontSize: '32px',
          fontWeight: 700,
          border: '2px solid #059669'
        }}>
          {difficulty}
        </div>
        <div style={{
          backgroundColor: '#1e3a8a',
          color: '#60a5fa',
          padding: '16px 36px',
          borderRadius: '9999px',
          fontSize: '32px',
          fontWeight: 700,
          border: '2px solid #2563eb'
        }}>
          {topic}
        </div>
      </div>

      <div style={{
        fontSize: '110px',
        fontWeight: 900,
        letterSpacing: '-2px',
        textAlign: 'center',
        background: 'linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #f472b6 100%)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        transform: `scale(${titleScale})`,
        marginBottom: '40px'
      }}>
        {title}
      </div>

      <div style={{
        fontSize: '44px',
        fontWeight: 400,
        color: '#94a3b8',
        textAlign: 'center',
        maxWidth: '850px',
        lineHeight: 1.4,
        opacity
      }}>
        {subtitle}
      </div>

      <div style={{
        marginTop: '120px',
        padding: '30px 60px',
        borderRadius: '24px',
        backgroundColor: 'rgba(255, 255, 255, 0.05)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        display: 'flex',
        alignItems: 'center',
        gap: '24px'
      }}>
        <div style={{
          width: '24px',
          height: '24px',
          borderRadius: '50%',
          backgroundColor: '#10b981',
          boxShadow: '0 0 20px #10b981'
        }} />
        <span style={{ fontSize: '36px', color: '#e2e8f0', fontWeight: 600 }}>
          AI DSA Studio — Animated Walkthrough
        </span>
      </div>
    </div>
  );
};
