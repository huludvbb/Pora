import { Ionicons, MaterialCommunityIcons } from "@expo/vector-icons";
import { useFocusEffect, useRouter } from "expo-router";
import React, { useCallback, useMemo, useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { langName } from "@/src/constants/languages";
import { fonts } from "@/src/theme";
import { api } from "@/src/utils/api";
import { learnColors, learnRadius } from "@/src/learn/theme";

interface LearnStatus {
  language: string;
  due_count: number;
  mistakes_count: number;
  mastered_count: number;
  total_vocab: number;
  streak_days: number;
}

/**
 * Learn dashboard — the home base of the mini-app.
 * Layout (top-down, matching the reference):
 *   1. "Review" top nav (title + user avatar chip)
 *   2. Big yellow "Daily Vocab Workout" card with primary Review Vocab CTA
 *   3. "Your vocabulary" section — purple + green tiles
 *   4. "Custom Collections" section header
 *   5. Save Items list card
 *   6. Bottom nav dock (four rounded chip icons + orange power CTA)
 */
export default function LearnDashboard() {
  const router = useRouter();
  const [status, setStatus] = useState<LearnStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const styles = useMemo(() => makeStyles(), []);

  const load = useCallback(async () => {
    try {
      const s = await api.get<LearnStatus>("/learn/status");
      setStatus(s);
    } catch {
      // Non-fatal — show a soft empty state.
    } finally {
      setLoading(false);
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      load();
    }, [load]),
  );

  return (
    <SafeAreaView style={styles.screen} edges={["top", "bottom"]}>
      {/* Top nav */}
      <View style={styles.topBar}>
        <Pressable
          testID="learn-back"
          onPress={() => router.back()}
          style={styles.topLeft}
          hitSlop={8}
        >
          <Ionicons name="chevron-back" size={22} color="#FFFFFF" />
          <Text style={styles.topTitle}>Review</Text>
        </Pressable>
        <View style={styles.avatarChip}>
          <Text style={styles.avatarChipEmoji}>🙂</Text>
        </View>
      </View>

      <ScrollView
        contentContainerStyle={styles.body}
        showsVerticalScrollIndicator={false}
      >
        {/* Daily Vocab Workout — big yellow card */}
        <View style={styles.yellowCard}>
          <Text style={styles.yellowTitle}>Daily Vocab Workout</Text>
          <Text style={styles.yellowBody}>
            Practice the words and phrases recommended to maximize your vocab
            retention.
          </Text>
          <Pressable
            testID="learn-review-vocab-btn"
            onPress={() => router.push("/learn/session")}
            style={styles.reviewBtn}
          >
            <Text style={styles.reviewBtnText}>Review Vocab</Text>
          </Pressable>
          <View style={styles.yellowFooter}>
            <Ionicons name="alert-circle" size={12} color="#0B0B0F" />
            <Text style={styles.yellowFooterText}>
              {loading
                ? "Loading your daily set…"
                : status
                ? `${status.due_count} words are ready to review · ${langName(status.language)}`
                : "Your next review session is available offline"}
            </Text>
          </View>
        </View>

        {/* Section: Your vocabulary */}
        <Text style={styles.sectionLabel}>Your vocabulary</Text>
        <View style={styles.tileRow}>
          <Pressable
            testID="learn-all-items-btn"
            onPress={() => router.push("/learn/vocabulary")}
            style={[styles.tile, { backgroundColor: learnColors.purple }]}
          >
            <View style={styles.tileIcon}>
              <MaterialCommunityIcons name="book-open" size={22} color="#FFF" />
            </View>
            <Text style={styles.tileLabel}>All Items</Text>
            {status ? (
              <Text style={styles.tileSub}>{status.total_vocab} words</Text>
            ) : null}
          </Pressable>
          <Pressable
            testID="learn-mistakes-btn"
            onPress={() => router.push("/learn/mistakes")}
            style={[styles.tile, { backgroundColor: learnColors.green }]}
          >
            <View style={[styles.tileIcon, styles.tileIconDark]}>
              <Ionicons name="close" size={22} color="#0B0B0F" />
            </View>
            <Text style={[styles.tileLabel, { color: "#0B0B0F" }]}>
              Recent Mistakes
            </Text>
            {status ? (
              <Text style={[styles.tileSub, { color: "#0B0B0F" }]}>
                {status.mistakes_count} to review
              </Text>
            ) : null}
          </Pressable>
        </View>

        {/* Custom Collections */}
        <View style={styles.collectionsHeader}>
          <Text style={styles.sectionLabel}>Custom Collections</Text>
          <Text style={styles.reviewSmall}>Review</Text>
        </View>
        <Pressable
          testID="learn-save-items-btn"
          onPress={() => router.push("/learn/vocabulary")}
          style={styles.collectionRow}
        >
          <View style={styles.collectionIcon}>
            <Ionicons name="bookmark" size={18} color="#FFFFFF" />
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.collectionName}>Save Items</Text>
            <Text style={styles.collectionCount}>
              {status ? `${status.mastered_count} items` : "0 items"}
            </Text>
          </View>
          <Ionicons
            name="chevron-forward"
            size={18}
            color={learnColors.onSurfaceSecondary}
          />
        </Pressable>

        {loading && (
          <ActivityIndicator
            color={learnColors.yellow}
            style={{ marginTop: 24 }}
          />
        )}
      </ScrollView>

      {/* Bottom nav dock */}
      <View style={styles.dock}>
        <DockBtn
          testID="learn-dock-home"
          icon="home"
          onPress={() => router.replace("/learn/dashboard")}
          active
        />
        <DockBtn
          testID="learn-dock-plan"
          icon="checkmark-circle"
          onPress={() => router.replace("/learn/plan")}
        />
        <DockBtn
          testID="learn-dock-classes"
          icon="people"
          orange
          onPress={() => router.replace("/learn/classes")}
        />
        <DockBtn
          testID="learn-dock-explore"
          icon="telescope"
          onPress={() => router.replace("/learn/explore")}
        />
      </View>
    </SafeAreaView>
  );
}

const DockBtn = ({
  icon,
  onPress,
  active,
  orange,
  testID,
}: {
  icon: keyof typeof Ionicons.glyphMap;
  onPress: () => void;
  active?: boolean;
  orange?: boolean;
  testID: string;
}) => {
  return (
    <Pressable
      testID={testID}
      onPress={onPress}
      style={[
        dockStyles.btn,
        active && dockStyles.btnActive,
        orange && dockStyles.btnOrange,
      ]}
    >
      <Ionicons
        name={icon}
        size={22}
        color={orange ? "#FFFFFF" : active ? "#FFFFFF" : "#B0B0BD"}
      />
    </Pressable>
  );
};

const dockStyles = StyleSheet.create({
  btn: {
    width: 54,
    height: 54,
    borderRadius: 18,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: learnColors.surfaceRaised,
    borderWidth: 1,
    borderColor: learnColors.border,
  },
  btnActive: {
    borderColor: "#4A4A55",
    backgroundColor: learnColors.surfaceHigh,
  },
  btnOrange: {
    backgroundColor: learnColors.orange,
    borderColor: learnColors.orange,
    width: 60,
    height: 60,
    borderRadius: 20,
  },
});

const makeStyles = () =>
  StyleSheet.create({
    screen: {
      flex: 1,
      backgroundColor: learnColors.bg,
    },
    topBar: {
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "space-between",
      paddingHorizontal: 20,
      paddingVertical: 12,
    },
    topLeft: {
      flexDirection: "row",
      alignItems: "center",
      gap: 4,
    },
    topTitle: {
      fontFamily: fonts.displaySemi,
      fontSize: 15,
      color: "#FFFFFF",
    },
    avatarChip: {
      width: 34,
      height: 34,
      borderRadius: 17,
      backgroundColor: learnColors.surfaceRaised,
      alignItems: "center",
      justifyContent: "center",
    },
    avatarChipEmoji: { fontSize: 18 },
    body: {
      paddingHorizontal: 20,
      paddingBottom: 120,
      gap: 20,
    },
    yellowCard: {
      backgroundColor: learnColors.yellow,
      borderRadius: 28,
      padding: 22,
      gap: 8,
    },
    yellowTitle: {
      fontFamily: fonts.displayBold,
      fontSize: 22,
      color: learnColors.onYellow,
    },
    yellowBody: {
      fontFamily: fonts.textSemi,
      fontSize: 13,
      color: learnColors.onYellow,
      lineHeight: 18,
    },
    reviewBtn: {
      backgroundColor: "#0B0B0F",
      borderRadius: learnRadius.chip,
      paddingVertical: 14,
      alignItems: "center",
      marginTop: 6,
    },
    reviewBtnText: {
      fontFamily: fonts.textBold,
      color: "#FFFFFF",
      fontSize: 14,
    },
    yellowFooter: {
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "center",
      gap: 5,
      marginTop: 2,
    },
    yellowFooterText: {
      fontFamily: fonts.textSemi,
      fontSize: 11,
      color: learnColors.onYellow,
    },
    sectionLabel: {
      fontFamily: fonts.displayBold,
      fontSize: 15,
      color: "#FFFFFF",
    },
    tileRow: {
      flexDirection: "row",
      gap: 14,
    },
    tile: {
      flex: 1,
      borderRadius: 22,
      padding: 16,
      minHeight: 130,
      justifyContent: "space-between",
    },
    tileIcon: {
      width: 34,
      height: 34,
      borderRadius: 12,
      backgroundColor: "rgba(255,255,255,0.22)",
      alignItems: "center",
      justifyContent: "center",
    },
    tileIconDark: {
      backgroundColor: "rgba(0,0,0,0.15)",
    },
    tileLabel: {
      fontFamily: fonts.displayBold,
      fontSize: 15,
      color: "#FFFFFF",
    },
    tileSub: {
      fontFamily: fonts.textSemi,
      fontSize: 12,
      color: "rgba(255,255,255,0.75)",
      marginTop: 2,
    },
    collectionsHeader: {
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "space-between",
    },
    reviewSmall: {
      fontFamily: fonts.textSemi,
      fontSize: 12,
      color: learnColors.onSurfaceSecondary,
    },
    collectionRow: {
      flexDirection: "row",
      alignItems: "center",
      gap: 12,
      backgroundColor: learnColors.surfaceRaised,
      borderRadius: 18,
      padding: 14,
    },
    collectionIcon: {
      width: 36,
      height: 36,
      borderRadius: 12,
      backgroundColor: "#2E2E38",
      alignItems: "center",
      justifyContent: "center",
    },
    collectionName: {
      fontFamily: fonts.textBold,
      fontSize: 14,
      color: "#FFFFFF",
    },
    collectionCount: {
      fontFamily: fonts.textSemi,
      fontSize: 12,
      color: learnColors.onSurfaceSecondary,
    },
    dock: {
      position: "absolute",
      left: 20,
      right: 20,
      bottom: 24,
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "space-between",
      backgroundColor: learnColors.surface,
      borderRadius: 26,
      padding: 8,
      borderWidth: 1,
      borderColor: learnColors.border,
    },
  });
