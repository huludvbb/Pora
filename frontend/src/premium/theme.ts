// Royal-purple + gold premium palette for the exclusive members' area.
// Kept in its own module so screens can pick it up without touching the
// main app theme.

export const premiumColors = {
  // Backgrounds
  bg: "#0F0623",           // very deep royal black-purple
  surface: "#1A0F2E",       // main surface
  surfaceRaised: "#251742", // elevated card
  surfaceHigh: "#312057",   // active state
  chip: "#3B2A63",

  // Text
  onSurface: "#F5EDDA",         // cream white (matches gold)
  onSurfaceSecondary: "#B9A5D6",// soft lilac
  onSurfaceTertiary: "#7A6B96",

  // Accents
  gold: "#FFB627",         // rich gold — primary brand
  goldSoft: "#FFD866",     // softer gold for hover / secondary
  goldDeep: "#C08316",     // deep gold for pressed state
  onGold: "#1A0F2E",        // text on gold

  // Utility
  border: "#3B2456",
  divider: "#241338",
  error: "#F87171",
  success: "#A5FF5C",
  info: "#B4A0FF",

  // Category tints (softened for premium)
  purple: "#B892FF",
  rose: "#FF9AC7",
  emerald: "#7FF6C3",
  amber: "#FFCE6F",
} as const;

export const premiumRadius = {
  sm: 10,
  md: 16,
  lg: 20,
  xl: 26,
  pill: 999,
} as const;
