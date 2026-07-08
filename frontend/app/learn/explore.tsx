import { Ionicons, MaterialCommunityIcons } from "@expo/vector-icons";
import { useRouter } from "expo-router";
import React from "react";
import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { fonts } from "@/src/theme";
import { learnColors, learnRadius } from "@/src/learn/theme";

/**
 * Learn / Explore — the discovery hub.
 * Big colorful cards route the user to focused learning surfaces (Courses,
 * All Chat Partner, Grammar Guide, …). Layout matches the reference: dark
 * shell, a "fire streak" chip + avatar in the top-right, and big rounded
 * cards with a hand-drawn wavy line pattern as decoration.
 */
export default function LearnExplore() {
  const router = useRouter();
  return (
    <SafeAreaView style={styles.screen} edges={["top", "bottom"]}>
      <View style={styles.topBar}>
        <Text style={styles.h1}>Explore</Text>
        <View style={styles.rightGroup}>
          <View style={styles.streakChip}>
            <Text style={{ fontSize: 15 }}>🔥</Text>
          </View>
          <View style={styles.avatarChip}>
            <Text style={styles.avatarEmoji}>🙂</Text>
          </View>
        </View>
      </View>

      <ScrollView
        contentContainerStyle={styles.body}
        showsVerticalScrollIndicator={false}
      >
        <Pressable
          testID="learn-explore-search"
          style={styles.searchChip}
          onPress={() => router.push("/learn/vocabulary")}
        >
          <Ionicons name="search" size={18} color="#FFFFFF" />
        </Pressable>

        <ExploreCard
          testID="learn-explore-courses"
          color="#DABFFF"
          title="Courses"
          body="Find all courses here, based on your level, skills, and interests—tailored for growth."
          icon={<MaterialCommunityIcons name="school" size={22} color="#2B1D51" />}
          onPress={() => router.push("/learn/vocabulary")}
        />
        <ExploreCard
          testID="learn-explore-chat-partner"
          color={learnColors.yellow}
          title="All Chat Partner"
          body="Speak in your own words in real time dialogues, expressing thoughts and ideas."
          icon={
            <MaterialCommunityIcons name="chip" size={22} color="#0B0B0F" />
          }
          onPress={() => router.push("/learn/classes")}
        />
        <ExploreCard
          testID="learn-explore-grammar"
          color={learnColors.green}
          title="Grammar Guide"
          body="Simple grammar explanations with clear, easy-to-understand examples for every level."
          icon={
            <MaterialCommunityIcons
              name="puzzle-outline"
              size={22}
              color="#0B0B0F"
            />
          }
          onPress={() => router.push("/learn/vocabulary")}
        />
      </ScrollView>

      <LearnDock active="explore" />
    </SafeAreaView>
  );
}

const ExploreCard = ({
  color,
  title,
  body,
  icon,
  onPress,
  testID,
}: {
  color: string;
  title: string;
  body: string;
  icon: React.ReactNode;
  onPress: () => void;
  testID: string;
}) => (
  <Pressable
    testID={testID}
    onPress={onPress}
    style={[styles.card, { backgroundColor: color }]}
  >
    <View style={styles.iconChip}>{icon}</View>
    <Text style={styles.cardTitle}>{title}</Text>
    <Text style={styles.cardBody}>{body}</Text>
    {/* Decorative wavy line motif (approximated with view + border-radius) */}
    <View
      pointerEvents="none"
      style={[
        styles.wave,
        { backgroundColor: "rgba(0,0,0,0.06)" },
      ]}
    />
  </Pressable>
);

// Shared floating dock used across learn pages.
export const LearnDock = ({
  active,
}: {
  active: "home" | "plan" | "classes" | "explore";
}) => {
  const router = useRouter();
  return (
    <View style={dockStyles.dock}>
      <DockBtn
        testID="learn-dock-home"
        icon="home"
        active={active === "home"}
        onPress={() => router.replace("/learn/dashboard")}
      />
      <DockBtn
        testID="learn-dock-plan"
        icon="checkmark-circle"
        active={active === "plan"}
        onPress={() => router.replace("/learn/dashboard")}
      />
      <DockBtn
        testID="learn-dock-classes"
        icon="people"
        orange
        active={active === "classes"}
        onPress={() => router.replace("/learn/classes")}
      />
      <DockBtn
        testID="learn-dock-explore"
        icon="telescope"
        active={active === "explore"}
        onPress={() => router.replace("/learn/explore")}
      />
    </View>
  );
};

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
}) => (
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

const dockStyles = StyleSheet.create({
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

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: learnColors.bg },
  topBar: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 20,
    paddingTop: 8,
    paddingBottom: 8,
  },
  h1: {
    fontFamily: fonts.displayBold,
    fontSize: 28,
    color: "#FFFFFF",
    letterSpacing: -0.5,
  },
  rightGroup: { flexDirection: "row", gap: 8 },
  streakChip: {
    width: 34,
    height: 34,
    borderRadius: 17,
    backgroundColor: learnColors.surfaceRaised,
    alignItems: "center",
    justifyContent: "center",
  },
  avatarChip: {
    width: 34,
    height: 34,
    borderRadius: 17,
    backgroundColor: learnColors.surfaceRaised,
    alignItems: "center",
    justifyContent: "center",
  },
  avatarEmoji: { fontSize: 17 },
  body: {
    paddingHorizontal: 20,
    paddingBottom: 130,
    gap: 16,
  },
  searchChip: {
    alignSelf: "flex-end",
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: learnColors.surfaceRaised,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 4,
  },
  card: {
    borderRadius: 28,
    padding: 22,
    minHeight: 190,
    gap: 8,
    overflow: "hidden",
    position: "relative",
  },
  iconChip: {
    alignSelf: "flex-end",
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: "rgba(0,0,0,0.08)",
    alignItems: "center",
    justifyContent: "center",
  },
  cardTitle: {
    fontFamily: fonts.displayBold,
    fontSize: 26,
    color: "#0B0B0F",
    marginTop: 4,
  },
  cardBody: {
    fontFamily: fonts.textSemi,
    fontSize: 14,
    color: "#0B0B0F",
    lineHeight: 20,
    opacity: 0.75,
  },
  wave: {
    position: "absolute",
    bottom: -30,
    right: -50,
    width: 260,
    height: 70,
    borderTopLeftRadius: 200,
    borderTopRightRadius: 200,
    transform: [{ rotate: "-6deg" }],
    opacity: 0.5,
  },
});
