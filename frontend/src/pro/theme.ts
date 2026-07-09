// "Pro" — Neo-Minimalism & Glassmorphism design tokens for the 1-on-1
// video tutoring sub-app. Warm, calming lifestyle-product feel. Kept in its
// own module so it never touches the main app theme.

export const proColors = {
  // Canvas
  bg: "#FBF9F6", // warm cream / alabaster
  bgAlt: "#F4EFE9", // slightly deeper cream for sections
  surface: "#FFFFFF",
  surfaceMuted: "#F6F2EC",

  // Ink / text
  ink: "#221E1A", // near-black warm
  inkSoft: "#6B625A",
  inkFaint: "#A79E95",

  // Accents (used strictly for focal CTAs)
  terracotta: "#C05A46",
  terracottaSoft: "#E7C6BE",
  terracottaTint: "#F7ECE9",
  sage: "#4A6B5D",
  sageSoft: "#CBD8D1",
  sageTint: "#EAF0EC",

  // Utility
  gold: "#C9A24B",
  border: "#ECE5DC",
  borderStrong: "#DFD6CA",
  divider: "#F0EAE2",
  online: "#4A9D6B",
  danger: "#C0483B",
  onAccent: "#FFFFFF",

  // Glass overlay
  glass: "rgba(255,255,255,0.65)",
  glassStrong: "rgba(255,255,255,0.82)",
  scrim: "rgba(20,16,12,0.45)",
} as const;

export const proRadius = {
  sm: 10,
  md: 12, // buttons
  lg: 18,
  xl: 24, // dashboard cards
  xxl: 32,
  pill: 999,
} as const;

export const proFonts = {
  // Elegant serif headers
  serif: "PlayfairDisplay_700Bold",
  serifBold: "PlayfairDisplay_800ExtraBold",
  serifSemi: "PlayfairDisplay_600SemiBold",
  // Ultra-clean sans for interactive elements + body
  sans: "Inter_400Regular",
  sansMedium: "Inter_500Medium",
  sansSemi: "Inter_600SemiBold",
  sansBold: "Inter_700Bold",
} as const;

export const proShadow = {
  // Soft, highly diffused ambient depth
  card: {
    shadowColor: "#3A2E22",
    shadowOpacity: 0.06,
    shadowRadius: 24,
    shadowOffset: { width: 0, height: 8 },
    elevation: 3,
  },
  soft: {
    shadowColor: "#3A2E22",
    shadowOpacity: 0.04,
    shadowRadius: 14,
    shadowOffset: { width: 0, height: 4 },
    elevation: 2,
  },
} as const;
