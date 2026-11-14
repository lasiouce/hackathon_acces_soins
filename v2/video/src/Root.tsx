import React from 'react';
import { Composition } from 'remotion';
import { Pitch, TOTAL } from './Pitch';
import { PitchV2, TOTAL_V2 } from './PitchV2';

export const Root: React.FC = () => (
  <>
    <Composition id="Pitch" component={Pitch} durationInFrames={TOTAL} fps={30} width={1920} height={1080} defaultProps={{ bgm: true, subtitles: true }} />
    <Composition id="PitchV2" component={PitchV2} durationInFrames={TOTAL_V2} fps={30} width={1920} height={1080} defaultProps={{ subtitles: true }} />
  </>
);
