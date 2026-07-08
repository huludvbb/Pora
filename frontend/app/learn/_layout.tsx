import { Stack } from "expo-router";
import React from "react";
import { StatusBar } from "expo-status-bar";
import { View } from "react-native";

import { learnColors } from "@/src/learn/theme";

/**
 * Dedicated stack for the Learn "mini-app". Enforces a dark, immersive shell
 * (near-black bg + light status bar) that persists across every learn screen,
 * regardless of the app-wide light/dark theme the user is running.
 */
export default function LearnLayout() {
  return (
    <View style={{ flex: 1, backgroundColor: learnColors.bg }}>
      <StatusBar style="light" />
      <Stack
        screenOptions={{
          headerShown: false,
          contentStyle: { backgroundColor: learnColors.bg },
          animation: "slide_from_right",
        }}
      />
    </View>
  );
}
