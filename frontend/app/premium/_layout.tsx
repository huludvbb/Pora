import { Stack } from "expo-router";
import React from "react";
import { StatusBar } from "expo-status-bar";
import { View } from "react-native";

import { premiumColors } from "@/src/premium/theme";

/**
 * Dedicated stack for the Premium members' club. Uses its own royal-purple
 * + gold palette so it feels completely detached from the free main app.
 * The (tabs) group inside this stack renders the bottom tab bar with the
 * same 5 icons as the main app but in the premium palette.
 */
export default function PremiumLayout() {
  return (
    <View style={{ flex: 1, backgroundColor: premiumColors.bg }}>
      <StatusBar style="light" />
      <Stack
        screenOptions={{
          headerShown: false,
          contentStyle: { backgroundColor: premiumColors.bg },
          animation: "default",
        }}
      />
    </View>
  );
}
