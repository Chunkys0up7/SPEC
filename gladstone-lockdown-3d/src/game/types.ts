export type ArtType =
  | 'door'
  | 'vault'
  | 'elevator'
  | 'cabinet'
  | 'drawer'
  | 'safe'
  | 'wallsafe'
  | 'register'
  | 'monitor'
  | 'phone'
  | 'fax'
  | 'mug'
  | 'calc'
  | 'box'
  | 'plant'
  | 'shredder'
  | 'binder'
  | 'whiteboard'
  | 'poster'
  | 'frame'
  | 'panel'
  | 'sticky'
  | 'sheet'
  | 'folder';

export type ChallengeKind = 'mc' | 'code';

export interface Find {
  id: string;
  art: ArtType;
  glyph?: string;
  label: string;
  decoy?: true;
  kind?: ChallengeKind;
  q?: string;
  o?: [string, string, string, string];
  a?: 0 | 1 | 2 | 3;
  code?: string;
  text: string;
}

export interface Lock {
  id: string;
  art: ArtType;
  kind: ChallengeKind;
  title: string;
  q: string;
  o?: [string, string, string, string];
  a?: 0 | 1 | 2 | 3;
  code?: string;
  requires?: string;
  exit?: true;
}

export interface Room {
  n: 1 | 2 | 3 | 4;
  name: string;
  theme: string;
  color: 'c1' | 'c2' | 'c3' | 'c4';
  accent: `#${string}`;
  wall: `#${string}`;
  floor: `#${string}`;
  win: boolean;
  blurb: string;
  finds: Find[];
  locks: Lock[];
}

export type RoomId = 1 | 2 | 3 | 4;

export type SpotClass = 'sealed' | 'live' | 'hunt' | 'done' | 'open';

export interface SpotState {
  cls: SpotClass;
  glyph: string;
  sub: string;
}

export interface GameState {
  v: 3;
  order: string[];
  turnPos: number;
  found: Record<RoomId, string[]>;
  solved: Record<RoomId, string[]>;
  rooms: Record<RoomId, Record<string, number>>;
  lifelines: Record<RoomId, Record<string, true>>;
  helper: Record<RoomId, string | null>;
  completed: Record<RoomId, boolean>;
}
