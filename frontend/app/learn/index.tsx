import AsyncStorage from "@react-native-async-storage/async-storage";
import { useFocusEffect, useRouter } from "expo-router";
import React, { useCallback, useState } from "react";
import { ActivityIndicator, View } from "react-native";

import { learnColors } from "@/src/learn/theme";

const KEY = "learn_onboarded_v1";

/**
 * Learn stack entry — decides whether to show the multi-slide intro (first
 * time in) or go straight to the dashboard on subsequent visits.
 */
export default function LearnIndex() {
  const router = useRouter();
  const [ready, setReady] = useState(false);

  useFocusEffect(
    useCallback(() => {
      let mounted = true;
      (async () => {
        try {
          const seen = await AsyncStorage.getItem(KEY);
          if (!mounted) return;
          router.replace(seen ? "/learn/dashboard" : "/learn/onboarding");
        } catch {
          router.replace("/learn/onboarding");
        }
        setReady(true);
      })();
      return () => {
        mounted = false;
      };
    }, [router]),
  );

  return (
    <View
      style={{
        flex: 1,
        backgroundColor: learnColors.bg,
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      {!ready && <ActivityIndicator color={learnColors.yellow} />}
    </View>
  );
}
