export type Area = 'hips' | 'shoulders' | 't-spine' | 'breath' | 'ankles' | 'floor' | 'neck';
export type Context = 'desk' | 'pre-wod' | 'post-wod' | 'tv' | 'dad' | 'travel';

export type Movement = {
  id: string;
  title: string;
  area: Area[];
  contexts: Context[];
  time: '1 min' | '2 min' | '3 min' | '5 min' | '10 min' | '20 min';
  equipment: string[];
  useWhen: string;
  dose: string;
  cues: string[];
  mistake: string;
  retest: string;
  source: string;
  dadSafe?: boolean;
};

export type Protocol = {
  id: string;
  title: string;
  context: Context;
  duration: string;
  promise: string;
  steps: { movementId: string; dose: string }[];
};

export const movements: Movement[] = [
  {
    id: 'couch-stretch',
    title: 'Couch Stretch',
    area: ['hips'],
    contexts: ['desk', 'pre-wod'],
    time: '2 min',
    equipment: ['wall', 'couch'],
    useWhen: 'Hips feel locked, low back wants to arch, squats/running are coming.',
    dose: '2 min per side when possible; 60 sec per side for the minimum dose.',
    cues: ['Back knee near wall or couch.', 'Squeeze back-leg glute.', 'Ribs down; breathe without banana-backing.'],
    mistake: 'Arching the low back to fake hip extension.',
    retest: 'Stand tall, squeeze glute, then check squat depth or hip extension again.',
    source: 'Kelly Starrett — Supple Leopard / FoundMyFitness healthy-day episode.',
  },
  {
    id: 'deep-squat-hold',
    title: 'Deep Squat Hold',
    area: ['hips', 'ankles'],
    contexts: ['desk', 'pre-wod', 'tv', 'dad'],
    time: '2 min',
    equipment: ['none'],
    useWhen: 'You have been chair-shaped too long or need to remind the hips/ankles what bottom range is.',
    dose: '60-120 sec total; hold a doorframe or desk if needed.',
    cues: ['Feet rooted.', 'Breathe into the back and ribs.', 'Shift gently side to side.'],
    mistake: 'Forcing depth while holding your breath.',
    retest: 'Bodyweight squat: does bottom position feel less guarded?',
    source: 'Starrett movement minimums; squat as diagnostic and exposure.',
    dadSafe: true,
  },
  {
    id: 'floor-sitting-rotation',
    title: 'Floor Sitting Rotation',
    area: ['floor', 'hips'],
    contexts: ['tv', 'dad', 'desk'],
    time: '20 min',
    equipment: ['floor'],
    useWhen: 'Passive time: TV, calls, reading. Restore ground competence without making it a workout.',
    dose: '20-30 min total; rotate every time a position gets annoying.',
    cues: ['Try long-sit, cross-legged, kneeling, side-sit.', 'Use hands or couch to transition.', 'Discomfort guides rotation; sharp pain stops it.'],
    mistake: 'Treating floor sitting like a perfect posture contest.',
    retest: 'Sit-and-rise: can you get down/up smoother than last week?',
    source: 'Starrett — floor sitting and get-up capacity as daily movement nutrition.',
    dadSafe: true,
  },
  {
    id: 't-spine-chair-opener',
    title: 'T-Spine Chair Opener',
    area: ['t-spine', 'shoulders'],
    contexts: ['desk', 'pre-wod', 'travel'],
    time: '1 min',
    equipment: ['chair'],
    useWhen: 'Shoulders feel jammed, overhead feels short, or desk posture turns into a C-shape.',
    dose: '8-10 slow reps or 60 sec breathing over the chair back.',
    cues: ['Hands behind head or elbows on desk.', 'Extend upper back, not low back.', 'Exhale fully before each reach.'],
    mistake: 'Cranking the neck or flaring ribs to fake thoracic extension.',
    retest: 'Reach overhead: do arms line up closer to ears without rib flare?',
    source: 'Starrett — restore trunk/T-spine before blaming shoulder blades.',
  },
  {
    id: 'doorway-pec-stretch',
    title: 'Doorway Pec Stretch',
    area: ['shoulders'],
    contexts: ['desk', 'pre-wod'],
    time: '2 min',
    equipment: ['doorway'],
    useWhen: 'Front of shoulders feels short or you keep over-retracting shoulder blades at the desk.',
    dose: '60 sec per side; easy pressure.',
    cues: ['Forearm on doorway.', 'Step through gently.', 'Keep ribs stacked; do not shrug.'],
    mistake: 'Letting the shoulder glide forward while chasing a bigger stretch.',
    retest: 'Hands-behind-back or overhead reach: smoother?',
    source: 'Starrett anterior shoulder / pec restriction model.',
  },
  {
    id: 'supported-hang',
    title: 'Supported Hang',
    area: ['shoulders', 't-spine'],
    contexts: ['desk', 'pre-wod', 'dad'],
    time: '1 min',
    equipment: ['bar', 'doorframe', 'desk'],
    useWhen: 'Shoulders need overhead exposure but a full dead hang is too much.',
    dose: '3 x 20 sec supported holds or 1 easy 30 sec hang.',
    cues: ['Keep feet lightly on ground if needed.', 'Let ribs breathe.', 'No aggressive shrugging or yanking.'],
    mistake: 'Turning a mobility snack into a grip max test.',
    retest: 'Overhead reach or press setup: less jammed?',
    source: 'Starrett shoulder archetypes; overhead exposure.',
    dadSafe: true,
  },
  {
    id: 'breath-expansion',
    title: 'Full Trunk Breath Expansion',
    area: ['breath', 't-spine'],
    contexts: ['desk', 'pre-wod', 'post-wod', 'dad', 'travel'],
    time: '1 min',
    equipment: ['none'],
    useWhen: 'You are shallow-breathing, anxious, stiff, or neck/low back feels guarded.',
    dose: '5 slow breaths: full inhale through belly/ribs/chest/back, full exhale.',
    cues: ['Inhale into ribs and upper back.', 'Long full exhale.', 'Keep jaw/neck relaxed.'],
    mistake: 'Forcing breath holds until dizzy.',
    retest: 'Turn head, reach overhead, or hinge: does the spine feel less guarded?',
    source: 'Starrett / Jill Miller / Oxygen Advantage framing: breath is trunk ROM.',
    dadSafe: true,
  },
  {
    id: 'hip-spin-up',
    title: 'Hip Spin-Up',
    area: ['hips', 'floor'],
    contexts: ['pre-wod', 'desk', 'travel'],
    time: '5 min',
    equipment: ['floor'],
    useWhen: 'Before squats, running, CrossFit, or a day that started on the laptop.',
    dose: '3-5 min touching hip flexion, rotation, and a squat shape.',
    cues: ['Move slowly through 90/90 or shin-box positions.', 'Pause and breathe at end range.', 'Finish with a squat hold.'],
    mistake: 'Rushing through shapes as if it is cardio.',
    retest: 'Bodyweight squat or sit-and-rise feels easier?',
    source: 'Starrett healthy-day episode — hip spin-up as daily movement vitamin.',
  },
  {
    id: 'shoulder-spin-up',
    title: 'Shoulder Spin-Up',
    area: ['shoulders', 't-spine', 'breath'],
    contexts: ['desk', 'pre-wod'],
    time: '5 min',
    equipment: ['band', 'wall', 'bar'],
    useWhen: 'Before pressing/pulling or after desk shoulders start feeling haunted.',
    dose: '3-5 min: T-spine opener, pec opening, supported hang or wall slides.',
    cues: ['Start with ribcage/breath.', 'Touch overhead gently.', 'Keep neck quiet.'],
    mistake: 'Only squeezing shoulder blades harder.',
    retest: 'Overhead reach, front rack, or push-up setup.',
    source: 'Starrett — shoulder function depends on trunk/scapula options.',
  },
  {
    id: 'sit-and-rise-practice',
    title: 'Sit-and-Rise Practice',
    area: ['floor', 'hips'],
    contexts: ['dad', 'tv', 'desk'],
    time: '3 min',
    equipment: ['floor', 'couch optional'],
    useWhen: 'You want the highest-signal life-capacity drill: get down and up from the floor.',
    dose: '3-5 smooth reps. Use hands, knee, or couch as needed.',
    cues: ['Lower with control.', 'Find the easiest path up.', 'Make it smoother, not harder.'],
    mistake: 'Scoring yourself instead of practicing the skill.',
    retest: 'Same test weekly: fewer supports or smoother transitions?',
    source: 'Starrett / sit-and-rise longevity proxy discussion.',
    dadSafe: true,
  },
];

export const protocols: Protocol[] = [
  {
    id: 'desk-shoulders-5',
    title: 'Desk Shoulders — 5 min',
    context: 'desk',
    duration: '5 min',
    promise: 'Stop shoulder fidgeting; give ribcage and shoulders better inputs.',
    steps: [
      { movementId: 'breath-expansion', dose: '5 breaths' },
      { movementId: 't-spine-chair-opener', dose: '60 sec' },
      { movementId: 'doorway-pec-stretch', dose: '60 sec/side' },
      { movementId: 'supported-hang', dose: '30 sec easy' },
    ],
  },
  {
    id: 'hips-before-crossfit',
    title: 'Hips Before CrossFit — 10 min',
    context: 'pre-wod',
    duration: '10 min',
    promise: 'Arrive less chair-shaped without burning workout energy.',
    steps: [
      { movementId: 'breath-expansion', dose: '5 breaths' },
      { movementId: 'couch-stretch', dose: '60 sec/side' },
      { movementId: 'hip-spin-up', dose: '3 min' },
      { movementId: 'deep-squat-hold', dose: '90 sec' },
    ],
  },
  {
    id: 'evening-floor-reset',
    title: 'Evening Floor Reset — 20 min',
    context: 'tv',
    duration: '20 min',
    promise: 'Turn TV time into hip and floor-capacity exposure.',
    steps: [
      { movementId: 'floor-sitting-rotation', dose: '15 min' },
      { movementId: 'sit-and-rise-practice', dose: '3 reps' },
      { movementId: 'breath-expansion', dose: '5 breaths' },
    ],
  },
  {
    id: 'dad-floor-capacity',
    title: 'Dad Floor Capacity — 8 min',
    context: 'dad',
    duration: '8 min',
    promise: 'Gentle floor independence practice with support allowed.',
    steps: [
      { movementId: 'sit-and-rise-practice', dose: '3 supported reps' },
      { movementId: 'deep-squat-hold', dose: '60 sec supported' },
      { movementId: 'supported-hang', dose: '3 x 15 sec' },
      { movementId: 'breath-expansion', dose: '5 breaths' },
    ],
  },
];

export const contexts: { id: Context; label: string; helper: string }[] = [
  { id: 'desk', label: 'Desk haunted', helper: 'Shoulders, hips, laptop body' },
  { id: 'pre-wod', label: 'Before CrossFit', helper: 'Warm without draining' },
  { id: 'post-wod', label: 'After training', helper: 'Downshift and recover' },
  { id: 'tv', label: 'TV / passive', helper: 'Floor time without effort' },
  { id: 'dad', label: 'Dad-safe', helper: 'Supported, big-signal basics' },
  { id: 'travel', label: 'Travel', helper: 'No gear, tiny spaces' },
];

export const areas: { id: Area; label: string }[] = [
  { id: 'hips', label: 'Hips' },
  { id: 'shoulders', label: 'Shoulders' },
  { id: 't-spine', label: 'T-spine' },
  { id: 'breath', label: 'Breath' },
  { id: 'floor', label: 'Floor' },
  { id: 'ankles', label: 'Ankles' },
  { id: 'neck', label: 'Neck' },
];
