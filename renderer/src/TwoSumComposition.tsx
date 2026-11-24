import React from 'react';
import { Sequence } from 'remotion';
import { IntroScene } from './scenes/IntroScene';
import { ArrayScene } from './scenes/ArrayScene';
import { BruteForceScene } from './scenes/BruteForceScene';
import { HashMapScene } from './scenes/HashMapScene';
import { ComplexityScene } from './scenes/ComplexityScene';
import { SummaryScene } from './scenes/SummaryScene';

import scenePlan from '../../examples/two-sum/04_scene_plan.json';
import timelineData from '../../output/two-sum-prototype/07_narration_timeline.json';

const COMPONENT_MAP: Record<string, React.FC<any>> = {
  IntroScene,
  ArrayScene,
  BruteForceScene,
  HashMapScene,
  ComplexityScene,
  SummaryScene
};

export interface DynamicCompositionProps {
  scenePlan?: { scenes: any[] };
  timelineData?: { segments: any[]; total_frames?: number; fps?: number };
}

export const TwoSumComposition: React.FC<DynamicCompositionProps> = ({
  scenePlan: propScenePlan,
  timelineData: propTimelineData
}) => {
  const activeTimeline = propTimelineData || timelineData;
  const activeScenePlan = propScenePlan || scenePlan;

  const segments = activeTimeline.segments || [];
  const scenes = activeScenePlan.scenes || [];

  // Match each scene to its narration timing
  const timelineMap: Record<string, any> = {};
  for (const seg of segments) {
    timelineMap[seg.segment_id] = seg;
  }

  return (
    <div style={{ width: '100%', height: '100%', backgroundColor: '#000' }}>
      {scenes.map((scene) => {
        const seg = timelineMap[scene.narration_segment_id];
        if (!seg) return null;

        const Component = COMPONENT_MAP[scene.component];
        if (!Component) return null;

        return (
          <Sequence
            key={scene.scene_id}
            from={seg.start_frame}
            durationInFrames={seg.duration_frames}
          >
            <Component {...(scene.props || {})} />
          </Sequence>
        );
      })}
    </div>
  );
};
