---
name: remotion-tutorial-generator
description: Generate professional tutorial and introduction videos for projects using Remotion. Analyzes project workflows, creates structured video compositions with chapters, transitions, and annotations aligned with project architecture.
---

# Remotion Tutorial Generator

This skill enables you to create professional tutorial and introduction videos for software projects using Remotion, a React-based video generation framework.

## Core Capabilities

1. **Project Analysis**: Examine codebase structure, workflows, and architecture
2. **Video Planning**: Design video chapters that align with project workflows
3. **Remotion Setup**: Initialize and configure Remotion projects
4. **Component Generation**: Create video compositions with scenes, transitions, and animations
5. **Content Alignment**: Ensure video content accurately reflects project functionality

## MANDATORY REQUIREMENTS

Before considering this task complete, you MUST:

1. ✅ Create ALL scenes from your outlined chapter breakdown
2. ✅ Ensure total video duration is 2-5 minutes (NOT 1 minute or less)
3. ✅ Test render at least one scene to verify the project works
4. ✅ Run `npm run dev` and confirm the Remotion studio opens
5. ✅ Test render frames from complex scenes to verify NO content overflow beyond 1080px viewport
6. ✅ Complete ALL items in the Implementation Checklist below
7. ✅ Never skip scenes with the rationale "to keep this manageable"

**Do NOT mark the task complete until all checkboxes above are verified.**

## Video Generation Workflow

### Phase 1: Project Discovery

Before generating any video, thoroughly analyze the target project:

1. **Read Project Documentation**
   - README.md, CLAUDE.md, or similar documentation files
   - Identify key features, architecture, and user workflows
   - Note the tech stack and main dependencies

2. **Analyze Code Structure**
   - Examine directory structure and main entry points
   - Identify core components, services, and data flows
   - Map out user journeys and key interactions

3. **Identify Demo-worthy Features**
   - List features that should be highlighted in the video
   - Prioritize based on importance and visual appeal
   - Consider target audience (developers, users, stakeholders)

### Phase 2: Video Structure Planning

Create a structured video outline with chapters:

1. **Chapter Breakdown**
   - **Intro** (5-10 seconds): Project name, tagline, branding
   - **Overview** (10-20 seconds): High-level purpose and value proposition
   - **Key Features** (30-60 seconds per feature): Demonstrate main capabilities
   - **Architecture** (20-40 seconds): **REQUIRED** - Visual representation of system design
     - For projects with unique architecture (like MCP servers), this scene is CRITICAL
     - Do NOT skip this scene - it's often the key differentiator
   - **Getting Started** (20-30 seconds): Quick setup guide
   - **Call to Action** (5-10 seconds): Links, contributing, contact info

2. **Timing Calculations**
   - Set FPS (typically 30 or 60)
   - Calculate `durationInFrames` for each scene
   - Plan transition timing between scenes
   - Total video MUST be 2-5 minutes (120-300 seconds) for tutorials
   - Videos under 2 minutes are INCOMPLETE

3. **Visual Planning**
   - Determine aspect ratio (16:9 for standard, 1:1 for social, 9:16 for mobile)
   - Plan color scheme matching project branding
   - Design text hierarchy and annotation styles
   - Plan code snippet displays if needed

### Phase 3: Remotion Project Setup

Initialize the Remotion project:

```bash
# Create new Remotion project
npx create-video@latest

# Or add to existing project
npm install remotion
```

**Project Structure:**
```
remotion-tutorial/
├── src/
│   ├── Root.tsx                 # Register compositions
│   ├── Video.tsx                # Main video composition
│   ├── scenes/
│   │   ├── Intro.tsx
│   │   ├── Overview.tsx
│   │   ├── FeatureDemo.tsx
│   │   ├── Architecture.tsx
│   │   └── Outro.tsx
│   ├── components/
│   │   ├── ChapterTitle.tsx     # Reusable chapter headers
│   │   ├── CodeSnippet.tsx      # Syntax-highlighted code
│   │   ├── Annotation.tsx       # Text annotations
│   │   └── Transition.tsx       # Transition effects
│   └── utils/
│       ├── animations.ts        # Custom animation helpers
│       └── theme.ts             # Colors, fonts, spacing
├── public/
│   ├── assets/
│   │   ├── logo.png
│   │   ├── screenshots/
│   │   └── audio/
└── package.json
```

### Phase 4: Composition Implementation

#### Main Video Composition

```tsx
// src/Video.tsx
import {Composition} from 'remotion';
import {Intro} from './scenes/Intro';
import {Overview} from './scenes/Overview';
import {FeatureDemo} from './scenes/FeatureDemo';
import {Architecture} from './scenes/Architecture';
import {Outro} from './scenes/Outro';

export const RemotionVideo: React.FC = () => {
  const fps = 30;

  return (
    <>
      {/* Intro Scene */}
      <Sequence durationInFrames={fps * 8}>
        <Intro />
      </Sequence>

      {/* Overview Scene */}
      <Sequence from={fps * 8} durationInFrames={fps * 15}>
        <Overview />
      </Sequence>

      {/* Feature Demos */}
      <Sequence from={fps * 23} durationInFrames={fps * 45}>
        <FeatureDemo />
      </Sequence>

      {/* Architecture Diagram */}
      <Sequence from={fps * 68} durationInFrames={fps * 30}>
        <Architecture />
      </Sequence>

      {/* Outro */}
      <Sequence from={fps * 98} durationInFrames={fps * 10}>
        <Outro />
      </Sequence>
    </>
  );
};
```

#### Scene Components

Each scene should follow this pattern:

```tsx
// src/scenes/FeatureDemo.tsx
import {useCurrentFrame, useVideoConfig, interpolate, spring} from 'remotion';
import {ChapterTitle} from '../components/ChapterTitle';
import {Annotation} from '../components/Annotation';

export const FeatureDemo: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  // Fade in title
  const titleOpacity = interpolate(frame, [0, 30], [0, 1], {
    extrapolateRight: 'clamp'
  });

  // Animate annotation entrance
  const annotationY = spring({
    frame: frame - 60,
    fps,
    config: {
      damping: 100,
      stiffness: 200,
      mass: 0.5
    }
  });

  return (
    <div style={{
      width: '100%',
      height: '100%',
      backgroundColor: '#0f172a',
      position: 'relative'
    }}>
      {/* Chapter Title */}
      <ChapterTitle
        title="Key Features"
        subtitle="Real-time bidding and checkout"
        opacity={titleOpacity}
      />

      {/* Feature Demonstration */}
      <div style={{
        position: 'absolute',
        top: '30%',
        left: '10%',
        right: '10%'
      }}>
        {/* Screenshot or animation here */}
      </div>

      {/* Annotation */}
      {frame > 60 && (
        <Annotation
          text="Guests can place bids in real-time"
          position={{
            x: '20%',
            y: `${50 + annotationY * 10}%`
          }}
        />
      )}
    </div>
  );
};
```

### Phase 5: Reusable Components

#### Chapter Title Component

```tsx
// src/components/ChapterTitle.tsx
import React from 'react';

interface ChapterTitleProps {
  title: string;
  subtitle?: string;
  opacity?: number;
}

export const ChapterTitle: React.FC<ChapterTitleProps> = ({
  title,
  subtitle,
  opacity = 1
}) => {
  return (
    <div style={{
      position: 'absolute',
      top: '10%',
      left: '10%',
      right: '10%',
      opacity
    }}>
      <h1 style={{
        fontSize: '4rem',
        fontWeight: 'bold',
        color: '#ffffff',
        margin: 0,
        textShadow: '0 4px 8px rgba(0,0,0,0.3)'
      }}>
        {title}
      </h1>
      {subtitle && (
        <p style={{
          fontSize: '2rem',
          color: '#cbd5e1',
          marginTop: '1rem'
        }}>
          {subtitle}
        </p>
      )}
    </div>
  );
};
```

#### Transition Component

```tsx
// src/components/Transition.tsx
import {useCurrentFrame, interpolate} from 'remotion';

interface TransitionProps {
  type: 'fade' | 'slide' | 'wipe';
  durationInFrames: number;
  direction?: 'in' | 'out';
  children: React.ReactNode;
}

export const Transition: React.FC<TransitionProps> = ({
  type,
  durationInFrames,
  direction = 'in',
  children
}) => {
  const frame = useCurrentFrame();

  const progress = interpolate(
    frame,
    [0, durationInFrames],
    direction === 'in' ? [0, 1] : [1, 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}
  );

  const style: React.CSSProperties = (() => {
    switch (type) {
      case 'fade':
        return {opacity: progress};
      case 'slide':
        return {transform: `translateX(${(1 - progress) * -100}%)`};
      case 'wipe':
        return {clipPath: `inset(0 ${(1 - progress) * 100}% 0 0)`};
      default:
        return {};
    }
  })();

  return <div style={style}>{children}</div>;
};
```

#### Annotation Component

```tsx
// src/components/Annotation.tsx
interface AnnotationProps {
  text: string;
  position: {x: string; y: string};
  arrow?: {from: string; to: string};
}

export const Annotation: React.FC<AnnotationProps> = ({
  text,
  position,
  arrow
}) => {
  return (
    <div style={{
      position: 'absolute',
      left: position.x,
      top: position.y,
      backgroundColor: '#fbbf24',
      color: '#1f2937',
      padding: '0.5rem 1rem',
      borderRadius: '0.5rem',
      fontSize: '1.5rem',
      fontWeight: '600',
      boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
      zIndex: 100
    }}>
      {text}
      {arrow && (
        <svg
          style={{
            position: 'absolute',
            width: '100%',
            height: '100%',
            pointerEvents: 'none'
          }}
        >
          {/* Arrow implementation */}
        </svg>
      )}
    </div>
  );
};
```

### Phase 6: Animation Patterns

#### Common Animation Helpers

```typescript
// src/utils/animations.ts
import {interpolate, spring, SpringConfig} from 'remotion';

export const fadeIn = (frame: number, startFrame: number, duration: number) => {
  return interpolate(
    frame,
    [startFrame, startFrame + duration],
    [0, 1],
    {extrapolateRight: 'clamp', extrapolateLeft: 'clamp'}
  );
};

export const slideIn = (
  frame: number,
  fps: number,
  delay: number = 0,
  config?: SpringConfig
) => {
  return spring({
    frame: frame - delay,
    fps,
    config: config || {damping: 100, stiffness: 200, mass: 0.5}
  });
};

export const staggeredAppearance = (
  frame: number,
  itemIndex: number,
  staggerDelay: number
) => {
  const startFrame = itemIndex * staggerDelay;
  return interpolate(
    frame,
    [startFrame, startFrame + 20],
    [0, 1],
    {extrapolateRight: 'clamp', extrapolateLeft: 'clamp'}
  );
};
```

### Phase 7: Audio Integration

Add background music and narration:

```tsx
import {Audio, useCurrentFrame} from 'remotion';

// In your main composition
<Audio src="/audio/background-music.mp3" volume={0.3} />

// For narration synced to scenes
<Sequence from={fps * 8}>
  <Audio src="/audio/narration-overview.mp3" />
</Sequence>
```

### Phase 8: Rendering

Render the video with appropriate settings:

```bash
# Preview in browser
npm run dev

# Render single frame for testing
npx remotion still src/index.ts MyVideo --frame=150 --output=preview.png

# Render full video
npx remotion render src/index.ts MyVideo output.mp4

# Render with custom settings
npx remotion render src/index.ts MyVideo output.mp4 \
  --codec=h264 \
  --scale=1 \
  --quality=90
```

### Phase 9: MANDATORY Verification (DO NOT SKIP)

Before completing this skill, you MUST:

1. **Run the development server:**
   ```bash
   npm run dev
   ```
   Verify it starts without errors and opens in browser.

2. **Test render a single frame:**
   ```bash
   npx remotion still src/index.ts [CompositionName] --frame=150 --output=test.png
   ```
   Verify no TypeScript or runtime errors.

3. **Verify ALL planned scenes exist:**
   - Check each scene file was created
   - Confirm each scene is imported in Video.tsx
   - Confirm each scene has a Sequence in the composition

4. **Confirm video duration meets requirements:**
   - Must be 2-5 minutes (120-300 seconds)
   - Count total frames and verify: totalFrames / fps >= 120

5. **Test for content overflow (CRITICAL):**
   ```bash
   # Render a frame from each major scene to check for overflow
   npx remotion still src/index.ts [CompositionName] --frame=[scene-middle-frame] --output=test-scene-X.png
   ```
   - Check scenes with vertical content (Architecture diagrams, code snippets, multi-section layouts)
   - Verify ALL content fits within 1080px viewport height
   - No text, boxes, or elements should extend beyond visible area
   - Common overflow scenes: Architecture diagrams, Getting Started (code blocks), Production Integration
   - **If content overflows:** Reduce font sizes, padding, gaps, and margins until everything fits

**If ANY verification step fails, you have NOT completed the skill.**

## Best Practices

### Content Alignment
- **Match Project Workflows**: Video flow should mirror actual user journeys
- **Accurate Representation**: Show real features, not mockups
- **Technical Accuracy**: Verify architecture diagrams match implementation
- **Update Regularly**: Regenerate videos when major features change

### Visual Design
- **Consistent Branding**: Use project colors, fonts, and logo
- **Readable Text**: Minimum 2rem font size, high contrast
- **Smooth Animations**: Prefer spring() for natural motion
- **Visual Hierarchy**: Most important info should be largest and centered
- **Viewport Awareness**: All content must fit within 1920x1080 viewport. Scenes with vertical stacking (diagrams, code blocks) need compact spacing and smaller fonts to prevent overflow.

### Performance
- **Optimize Assets**: Compress images and audio before importing
- **Lazy Loading**: Use dynamic imports for heavy components
- **Frame Rate**: 30fps is sufficient for most tutorials
- **Resolution**: 1080p (1920x1080) is standard for tutorials

### Transitions
- **Purposeful**: Use transitions to signal topic changes
- **Consistent Duration**: Typically 0.5-1 second (15-30 frames at 30fps)
- **Not Overdone**: Too many fancy transitions are distracting
- **Type Variety**: Mix fade, slide, and wipe based on content flow

### Annotations
- **Timely**: Appear when relevant feature is shown
- **Concise**: 5-10 words maximum
- **Positioned Well**: Don't obscure important content
- **Animated Entrance**: Use spring animations for natural feel

## REQUIRED Implementation Checklist

**You MUST complete every item below before the skill is considered done:**

- [ ] Analyze project structure and identify main workflows
- [ ] Read project documentation (README, CLAUDE.md)
- [ ] Create video outline with chapter breakdown
- [ ] Calculate timing for all scenes (in frames)
- [ ] Initialize Remotion project structure
- [ ] Create reusable component library (ChapterTitle, Annotation, etc.)
- [ ] Implement Intro scene with project branding
- [ ] Implement Overview scene with value proposition
- [ ] Create Feature Demo scenes for each key feature
- [ ] Design Architecture visualization scene
- [ ] Create Getting Started / Call to Action scene
- [ ] Add transitions between all scenes
- [ ] Implement annotations highlighting key points
- [ ] Add background music and narration (if available)
- [ ] Test render individual scenes
- [ ] Render full video and review
- [ ] Adjust timing, animations, and content based on review
- [ ] Export final video with optimized settings

## Common Patterns

### Pattern 1: Multi-Feature Showcase
For projects with multiple features, create a carousel effect:

```tsx
const features = [
  {title: 'Feature 1', description: '...', screenshot: '...'},
  {title: 'Feature 2', description: '...', screenshot: '...'},
  // ...
];

features.map((feature, index) => (
  <Sequence
    key={index}
    from={fps * (23 + index * 15)}
    durationInFrames={fps * 15}
  >
    <FeatureSlide feature={feature} />
  </Sequence>
));
```

### Pattern 2: Code Walkthrough
Show code snippets with syntax highlighting:

```tsx
import {CodeSnippet} from './components/CodeSnippet';

<Sequence from={fps * 50} durationInFrames={fps * 20}>
  <CodeSnippet
    language="typescript"
    code={`
      const handleBid = async (itemId: string, amount: number) => {
        await db.collection('bids').add({
          itemId,
          amount,
          timestamp: serverTimestamp()
        });
      };
    `}
    highlights={[2, 3, 4]} // Highlight specific lines
  />
</Sequence>
```

### Pattern 3: Architecture Diagram
Animate system architecture components:

```tsx
<Sequence durationInFrames={fps * 30}>
  <ArchitectureDiagram>
    <Box label="React Frontend" delay={0} />
    <Arrow from="frontend" to="firebase" delay={30} />
    <Box label="Firebase" delay={30} />
    <Arrow from="firebase" to="firestore" delay={60} />
    <Box label="Firestore DB" delay={60} />
  </ArchitectureDiagram>
</Sequence>
```

## Common Mistakes to Avoid

❌ **Creating only 3-4 scenes and calling it "manageable"**
   - If you outlined 7 scenes, create all 7 scenes
   - Do not rationalize skipping scenes

❌ **Skipping the Architecture scene**
   - This is often the most important differentiator
   - For projects with unique architecture, this is CRITICAL

❌ **Not testing the render**
   - Always run `npm run dev` before marking complete
   - Verify the project actually works

❌ **Making videos shorter than 2 minutes**
   - Tutorial videos need 120+ seconds minimum
   - 60 seconds is NOT a complete tutorial

❌ **Rationalizing shortcuts like "you can add these later"**
   - Complete the full scope now, or it's not done
   - The user asked for a complete skill execution

❌ **Skipping verification steps**
   - Phase 9 verification is MANDATORY
   - Test renders are REQUIRED

❌ **Content overflow beyond viewport**
   - Scenes with vertical content (diagrams, code, multi-section layouts) often overflow
   - Always test render frames from complex scenes
   - Reduce font sizes, padding, gaps, and margins to fit 1080px height
   - Architecture and Production Integration scenes are common culprits

## Troubleshooting

- **Video too long**: Reduce durationInFrames or remove less important scenes
- **Animations jerky**: Use spring() instead of interpolate() for smoother motion
- **Text unreadable**: Increase font size and improve contrast
- **Render takes too long**: Reduce resolution or frame rate for testing
- **Out of sync audio**: Ensure all Sequence timings are accurate
- **Content extends beyond screen**: Reduce padding (2rem → 1rem), font sizes (2rem → 1.5rem), gaps (2rem → 0.5rem), and top positioning (30% → 26%). Test with `npx remotion still` to verify fixes.

## References

- Official Remotion Docs: https://remotion.dev/docs
- Remotion GitHub: https://github.com/remotion-dev/remotion
- Community Examples: https://remotion.dev/showcase

## Success Criteria

A successful tutorial video should:
1. Accurately represent project functionality and workflows
2. Be 2-5 minutes in length
3. Have clear chapter structure with smooth transitions
4. Include helpful annotations at key moments
5. Use consistent branding and professional visual design
6. Be technically accurate in all representations
7. Engage viewers and clearly communicate value proposition
8. Have all content properly fitted within the 1920x1080 viewport with no overflow

## Skill Completion Checklist

Before reporting "skill complete", verify:

- [ ] Video duration is between 2-5 minutes (check totalDuration in Video.tsx)
- [ ] ALL scenes from your outline are implemented (not just "core" scenes)
- [ ] Architecture scene exists and visualizes the system design
- [ ] `npm run dev` runs without errors
- [ ] At least one test frame renders successfully
- [ ] **Test frames from complex scenes show NO content overflow** (Architecture, Production Integration, etc.)
- [ ] All 17 items in REQUIRED Implementation Checklist are complete
- [ ] README.md includes complete instructions
- [ ] You did NOT skip features with "you can add later" rationale

**If any checkbox is unchecked, the skill is INCOMPLETE.**
