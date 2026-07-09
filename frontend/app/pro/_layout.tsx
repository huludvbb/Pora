import { Stack } from "expo-router";
import React from "react";
import { StatusBar } from "expo-status-bar";
import { View } from "react-native";

import { proColors } from "@/src/pro/theme";

/**
 * Dedicated stack for the "Pro" 1-on-1 video tutoring sub-app. Uses its own
 * warm Neo-Minimalism palette so it feels like a separate high-end product
 * while still living inside the main app (shared auth).
 */
export default function ProLayout() {
  return (
    <View style={{ flex: 1, backgroundColor: proColors.bg }}>
      <StatusBar style="dark" />
      <Stack
        screenOptions={{
          headerShown: false,
          contentStyle: { backgroundColor: proColors.bg },
          animation: "default",
        }}
      />
    </View>
  );
}
