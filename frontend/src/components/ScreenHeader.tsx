import React from "react";
import { StyleSheet, Text, View, ViewStyle } from "react-native";

import { BackButton } from "@/src/components/BackButton";
import { useTheme } from "@/src/context/ThemeContext";
import { fonts, spacing } from "@/src/theme";

/**
 * Unified top-bar for every non-tab screen. Guarantees the same title font
 * (extra-bold Figtree 800 with subtle tracking), same 44pt height, and the
 * standard BackButton on the left so the app has one visual identity.
 *
 * Layout: [back or spacer] · [title (centered on native, left on web)] · [right slot]
 *
 * Use it as:
 *   <ScreenHeader title="Notifications" right={<Ionicons name="ellipsis" />} />
 */
export function ScreenHeader({
  title,
  showBack = true,
  onBack,
  right,
  variant = "default",
  style,
}: {
  title: string;
  showBack?: boolean;
  onBack?: () => void;
  right?: React.ReactNode;
  variant?: "default" | "overlay";
  style?: ViewStyle;
}) {
  const { colors } = useTheme();
  const isOverlay = variant === "overlay";
  return (
    <View
      style={[
        styles.bar,
        {
          borderBottomColor: isOverlay ? "transparent" : colors.border,
          backgroundColor: isOverlay ? "transparent" : colors.surface,
        },
        style,
      ]}
    >
      <View style={styles.side}>
        {showBack ? (
          <BackButton
            onPress={onBack}
            variant={isOverlay ? "overlay" : "plain"}
            color={isOverlay ? "#FFFFFF" : undefined}
          />
        ) : null}
      </View>
      <Text
        style={[
          styles.title,
          { color: isOverlay ? "#FFFFFF" : colors.onSurface },
        ]}
        numberOfLines={1}
      >
        {title}
      </Text>
      <View style={[styles.side, styles.rightSide]}>{right}</View>
    </View>
  );
}

const styles = StyleSheet.create({
  bar: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    minHeight: 52,
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    borderBottomWidth: StyleSheet.hairlineWidth,
  },
  side: {
    width: 60,
    justifyContent: "center",
  },
  rightSide: {
    alignItems: "flex-end",
  },
  title: {
    flex: 1,
    textAlign: "center",
    fontFamily: fonts.displayBold,
    fontSize: 18,
    letterSpacing: 0.2,
  },
});
