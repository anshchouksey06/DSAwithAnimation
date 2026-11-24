import React from 'react';
import { Composition, CalculateMetadataFunction } from 'remotion';
import { TwoSumComposition, DynamicCompositionProps } from './TwoSumComposition';
import defaultTimeline from '../../output/two-sum-prototype/07_narration_timeline.json';

const calculateMetadata: CalculateMetadataFunction<DynamicCompositionProps> = async ({ props }) => {
  const totalFrames = props?.timelineData?.total_frames || defaultTimeline.total_frames || 2220;
  const fps = props?.timelineData?.fps || defaultTimeline.fps || 30;
  return {
    durationInFrames: totalFrames,
    fps: fps,
    width: 1080,
    height: 1920
  };
};

export const Root: React.FC = () => {
  const totalFrames = defaultTimeline.total_frames || 2220;
  const fps = defaultTimeline.fps || 30;

  return (
    <>
      <Composition
        id="TwoSumVideo"
        component={TwoSumComposition}
        durationInFrames={totalFrames}
        fps={fps}
        width={1080}
        height={1920}
        calculateMetadata={calculateMetadata}
      />
      <Composition
        id="DSAVideo"
        component={TwoSumComposition}
        durationInFrames={totalFrames}
        fps={fps}
        width={1080}
        height={1920}
        calculateMetadata={calculateMetadata}
      />
    </>
  );
};
