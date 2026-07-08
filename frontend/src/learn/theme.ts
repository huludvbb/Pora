// Learn Module Design Tokens
// Dark palette + vibrant neon accents inspired by the reference UI.
// Kept in its own file so the whole Learn stack shares one visual system
// without polluting the app-wide light/dark themes.

export const learnColors = {
  bg: "#0B0B0F",
  surface: "#121218",
  surfaceRaised: "#1A1A21",
  surfaceHigh: "#25252E",
  border: "#2A2A34",
  onSurface: "#FFFFFF",
  onSurfaceSecondary: "#A0A0AB",
  onSurfaceTertiary: "#6B6B75",
  // Accent tiles / cards
  yellow: "#EAFF61",
  onYellow: "#0B0B0F",
  purple: "#8A5EF7",
  onPurple: "#FFFFFF",
  green: "#3BE39B",
  onGreen: "#0B0B0F",
  orange: "#FF5C1F",
  onOrange: "#FFFFFF",
  // Onboarding backgrounds
  onboardingLilac: "#DABFFF",
  onboardingYellow: "#EAFF61",
  onboardingOrange: "#FF6D33",
} as const;

export const learnRadius = {
  chip: 999,
  sm: 12,
  md: 20,
  lg: 28,
  xl: 36,
} as const;
