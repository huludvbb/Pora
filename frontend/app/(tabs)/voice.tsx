import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import * as Haptics from "expo-haptics";
import { useFocusEffect, useRouter } from "expo-router";
import React, { useCallback, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  FlatList,
  Modal,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  TextInput,
  View,
} from "react-native";
import { KeyboardAvoidingView } from "react-native-keyboard-controller";
import { SafeAreaView } from "react-native-safe-area-context";

import { Avatar } from "@/src/components/Avatar";
import { FlagIcon } from "@/src/components/FlagIcon";
import { SpeakingBars } from "@/src/components/SpeakingBars";
import { countryToCode } from "@/src/constants/countries";
import { langName } from "@/src/constants/languages";
import { useAuth } from "@/src/context/AuthContext";
import { useTheme } from "@/src/context/ThemeContext";
import { fonts, radius, shadow, spacing, ThemeColors } from "@/src/theme";
import { api, Room } from "@/src/utils/api";
import { timeAgo } from "@/src/utils/time";

const BG_GRADIENTS: [string, string][] = [
  ["#6D5AE8", "#4B3F87"],
  ["#0EA5E9", "#0369A1"],
  ["#EC4899", "#701A75"],
  ["#F59E0B", "#B45309"],
];

const bgForRoom = (room: Room) => {
  if (typeof room.background === "number") {
    return BG_GRADIENTS[room.background % BG_GRADIENTS.length];
  }
  let hash = 0;
  for (const ch of room.id) hash = (hash * 31 + ch.charCodeAt(0)) % 997;
  return BG_GRADIENTS[hash % BG_GRADIENTS.length];
};

const MODES: {
  id: "chat" | "music" | "interactive" | "game";
  label: string;
  icon: keyof typeof Ionicons.glyphMap;
  locked?: boolean;
}[] = [
  { id: "chat", label: "Chat", icon: "chatbubbles" },
  { id: "music", label: "Music", icon: "musical-notes" },
  { id: "interactive", label: "Interactive", icon: "easel", locked: true },
  { id: "game", label: "Game", icon: "game-controller", locked: true },
];

const TOPIC_TAGS = [
  "Small Talk",
  "Culture",
  "Music",
  "Games",
  "Study Together",
  "Just Chatting",
  "News",
  "Travel",
];

export default function Voice() {
  const router = useRouter();
  const { user } = useAuth();
  const { colors } = useTheme();
  const styles = React.useMemo(() => makeStyles(colors), [colors]);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [roomLangs, setRoomLangs] = useState<string[]>([]);
  const [mode, setMode] = useState<"chat" | "music">("chat");
  const [topic, setTopic] = useState<string | null>(null);
  const [isPrivate, setIsPrivate] = useState(false);
  const [background, setBackground] = useState(0);
  const [announcement, setAnnouncement] = useState("");
  const [shareToMoments, setShareToMoments] = useState(true);

  // Room languages come from the user's own languages (native + teach + learning).
  const myLangs = Array.from(
    new Set(
      [
        user?.native_language,
        ...(user?.teach_languages || []),
        ...(user?.learning_languages?.length
          ? user.learning_languages
          : user?.learning_language
            ? [user.learning_language]
            : []),
      ].filter(Boolean) as string[],
    ),
  );

  const toggleRoomLang = (code: string) => {
    setRoomLangs((prev) =>
      prev.includes(code)
        ? prev.filter((c) => c !== code)
        : prev.length >= 2
          ? prev
          : [...prev, code],
    );
  };

  const load = useCallback(async () => {
    try {
      const data = await api.get<Room[]>("/rooms");
      setRooms(data);
    } catch {
      // keep previous list
    } finally {
      setLoading(false);
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      load();
      const t = setInterval(load, 10000);
      return () => clearInterval(t);
    }, [load]),
  );

  const resetForm = () => {
    setTitle("");
    setRoomLangs([]);
    setMode("chat");
    setTopic(null);
    setIsPrivate(false);
    setBackground(0);
    setAnnouncement("");
    setShareToMoments(true);
  };

  const createRoom = async () => {
    if (!title.trim() || creating || roomLangs.length === 0) return;
    setCreating(true);
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    try {
      const room = await api.post<Room>("/rooms", {
        title: title.trim(),
        language: roomLangs[0],
        languages: roomLangs,
        topic,
        mode,
        is_private: isPrivate,
        background,
        announcement: announcement.trim() || null,
        share_to_moments: shareToMoments && !isPrivate,
      });
      setModalOpen(false);
      resetForm();
      router.push(`/room/${room.id}`);
    } catch {
      // keep modal open for retry
    } finally {
      setCreating(false);
    }
  };

  const joinRoom = async (room: Room) => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    try {
      await api.post(`/rooms/${room.id}/join`);
      router.push(`/room/${room.id}`);
    } catch {
      load();
    }
  };

  return (
    <SafeAreaView style={styles.container} edges={["top"]} testID="voice-screen">
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Voice Rooms</Text>
        <Text style={styles.headerSub}>
          Join live audio rooms and practice speaking
        </Text>
      </View>

      {loading ? (
        <View style={styles.center}>
          <ActivityIndicator size="large" color={colors.brand} />
        </View>
      ) : (
        <FlatList
          data={rooms}
          keyExtractor={(item) => item.id}
          contentContainerStyle={
            rooms.length === 0 ? { flex: 1 } : styles.list
          }
          ListEmptyComponent={
            <View style={styles.center}>
              <LinearGradient
                colors={["#38BDF8", "#6366F1"]}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 1 }}
                style={styles.emptyIconCircle}
              >
                <Ionicons name="mic" size={42} color="#FFFFFF" />
              </LinearGradient>
              <Text style={styles.emptyTitle}>No live rooms right now</Text>
              <Text style={styles.emptyText}>
                Be the first! Start a room and practice speaking with partners
                around the world.
              </Text>
            </View>
          }
          renderItem={({ item }) => {
            const previewExtra = Math.max(
              0,
              item.member_count - (item.members_preview?.length || 0),
            );
            return (
              <Pressable
                testID={`room-card-${item.id}`}
                style={styles.cardWrap}
                onPress={() => joinRoom(item)}
              >
                <LinearGradient colors={bgForRoom(item)} style={styles.card}>
                  <View style={styles.cardTop}>
                    <View style={styles.badgeRow}>
                      <View style={styles.langBadge}>
                        <FlagIcon code={item.language} size={12} />
                        <Text style={styles.langText}>
                          {langName(item.language)}
                        </Text>
                      </View>
                      {item.topic ? (
                        <View style={styles.topicBadge}>
                          <Text style={styles.topicText}>#{item.topic}</Text>
                        </View>
                      ) : null}
                      {item.is_private ? (
                        <Ionicons
                          name="lock-closed"
                          size={12}
                          color="rgba(255,255,255,0.85)"
                        />
                      ) : null}
                    </View>
                    <View style={styles.liveBadge}>
                      <SpeakingBars />
                      <Text style={styles.liveText}>LIVE</Text>
                    </View>
                  </View>

                  <Text style={styles.cardTitle} numberOfLines={2}>
                    {item.title}
                  </Text>

                  <View style={styles.cardBottom}>
                    <View style={styles.hostRow}>
                      <Avatar
                        name={item.host?.name}
                        url={item.host?.avatar_url}
                        size={26}
                        flagCode={countryToCode(item.host?.country)}
                        frame={item.host?.active_frame}
                      />
                      <Text style={styles.hostName} numberOfLines={1}>
                        {item.host?.name} · {timeAgo(item.created_at)}
                      </Text>
                    </View>
                    <View style={styles.memberStack}>
                      {(item.members_preview || []).map((m, i) => (
                        <View
                          key={m.id}
                          style={[
                            styles.stackAvatar,
                            { marginLeft: i === 0 ? 0 : -9, zIndex: 10 - i },
                          ]}
                        >
                          <Avatar name={m.name} url={m.avatar_url} size={24} />
                        </View>
                      ))}
                      <View style={styles.memberCountPill}>
                        <Ionicons name="people" size={11} color="#FFFFFF" />
                        <Text style={styles.memberCountText}>
                          {previewExtra > 0 ? `+${previewExtra}` : item.member_count}
                        </Text>
                      </View>
                    </View>
                  </View>
                </LinearGradient>
              </Pressable>
            );
          }}
        />
      )}

      <Pressable
        testID="room-create-fab"
        style={styles.fab}
        onPress={() => setModalOpen(true)}
      >
        <Ionicons name="add" size={26} color={colors.onBrand} />
        <Text style={styles.fabText}>Create Room</Text>
      </Pressable>

      <Modal
        visible={modalOpen}
        animationType="slide"
        onRequestClose={() => setModalOpen(false)}
      >
        <SafeAreaView style={styles.createScreen} edges={["top", "bottom"]}>
          <View style={styles.createHeader}>
            <Pressable
              testID="room-modal-close-btn"
              onPress={() => setModalOpen(false)}
              hitSlop={8}
            >
              <Ionicons name="close" size={24} color={colors.onSurface} />
            </Pressable>
            <Text style={styles.createHeaderTitle}>Create a Room</Text>
            <View style={{ width: 24 }} />
          </View>

          <KeyboardAvoidingView
            style={{ flex: 1 }}
            behavior={Platform.OS === "ios" ? "padding" : undefined}
          >
            <ScrollView
              contentContainerStyle={styles.createBody}
              keyboardShouldPersistTaps="handled"
            >
              <TextInput
                testID="room-title-input"
                style={styles.topicInput}
                placeholder="What will you talk about?"
                placeholderTextColor={colors.onSurfaceSecondary}
                value={title}
                onChangeText={setTitle}
                maxLength={80}
                multiline
              />

              <View style={styles.announceHeaderRow}>
                <Ionicons name="megaphone" size={15} color={colors.brand} />
                <Text style={styles.announceLabel}>Announcement</Text>
                <Text style={styles.announceHint}>Optional</Text>
              </View>
              <TextInput
                testID="room-announcement-input"
                style={styles.announceInput}
                placeholder="Pin a welcome message — house rules, today's topic, or a warm hello. Guests see it right away."
                placeholderTextColor={colors.onSurfaceSecondary}
                value={announcement}
                onChangeText={setAnnouncement}
                maxLength={300}
                multiline
              />
              <Text style={styles.announceCounter}>{announcement.length}/300</Text>

              <Text style={styles.sectionLabel}>
                Language ({roomLangs.length}/2)
              </Text>
              <ScrollView
                horizontal
                showsHorizontalScrollIndicator={false}
                contentContainerStyle={{ gap: spacing.sm }}
              >
                {myLangs.map((code) => {
                  const active = roomLangs.includes(code);
                  return (
                    <Pressable
                      key={code}
                      testID={`room-lang-${code}`}
                      onPress={() => toggleRoomLang(code)}
                      style={[styles.langChip, active && styles.langChipActive]}
                    >
                      <FlagIcon code={code} size={16} />
                      <Text
                        style={[
                          styles.langChipText,
                          active && styles.langChipTextActive,
                        ]}
                      >
                        {langName(code)}
                      </Text>
                    </Pressable>
                  );
                })}
              </ScrollView>

              <Text style={styles.sectionLabel}>Mode</Text>
              <View style={styles.modeGrid}>
                {MODES.map((m) => {
                  const active = mode === m.id;
                  return (
                    <Pressable
                      key={m.id}
                      testID={`room-mode-${m.id}`}
                      style={[
                        styles.modeItem,
                        active && styles.modeItemActive,
                        m.locked && styles.modeItemLocked,
                      ]}
                      onPress={() =>
                        m.locked
                          ? Alert.alert(
                              "Coming soon",
                              `${m.label} rooms are coming in a future update!`,
                            )
                          : setMode(m.id as "chat" | "music")
                      }
                    >
                      <Ionicons
                        name={m.icon}
                        size={20}
                        color={
                          m.locked
                            ? colors.onSurfaceSecondary
                            : active
                              ? colors.onBrand
                              : colors.onSurface
                        }
                      />
                      <Text
                        style={[
                          styles.modeLabel,
                          active && styles.modeLabelActive,
                          m.locked && styles.modeLabelLocked,
                        ]}
                      >
                        {m.label}
                      </Text>
                      {m.locked && (
                        <View style={styles.lockChip}>
                          <Ionicons name="lock-closed" size={9} color="#FFFFFF" />
                          <Text style={styles.lockChipText}>Soon</Text>
                        </View>
                      )}
                    </Pressable>
                  );
                })}
              </View>

              <Text style={styles.sectionLabel}>Topic</Text>
              <ScrollView
                horizontal
                showsHorizontalScrollIndicator={false}
                contentContainerStyle={{ gap: spacing.sm }}
              >
                {TOPIC_TAGS.map((t) => {
                  const active = topic === t;
                  return (
                    <Pressable
                      key={t}
                      testID={`room-topic-${t}`}
                      onPress={() => setTopic(active ? null : t)}
                      style={[styles.langChip, active && styles.langChipActive]}
                    >
                      <Text
                        style={[
                          styles.langChipText,
                          active && styles.langChipTextActive,
                        ]}
                      >
                        {t}
                      </Text>
                    </Pressable>
                  );
                })}
              </ScrollView>

              <Text style={styles.sectionLabel}>Background</Text>
              <View style={styles.bgRow}>
                {BG_GRADIENTS.map((g, i) => (
                  <Pressable
                    key={i}
                    testID={`room-bg-swatch-${i}`}
                    onPress={() => setBackground(i)}
                    style={styles.bgSwatchWrap}
                  >
                    <LinearGradient
                      colors={g}
                      style={[
                        styles.bgSwatch,
                        background === i && styles.bgSwatchActive,
                      ]}
                    >
                      {background === i && (
                        <Ionicons name="checkmark" size={16} color="#FFFFFF" />
                      )}
                    </LinearGradient>
                  </Pressable>
                ))}
              </View>

              <View style={styles.toggleRow}>
                <View style={{ flex: 1 }}>
                  <Text style={styles.toggleLabel}>Private Room</Text>
                  <Text style={styles.toggleSub}>
                    Only people you invite can join
                  </Text>
                </View>
                <Switch
                  testID="room-private-toggle"
                  value={isPrivate}
                  onValueChange={setIsPrivate}
                  trackColor={{ true: colors.brand, false: colors.border }}
                />
              </View>

              <View style={styles.toggleRow}>
                <View style={{ flex: 1 }}>
                  <Text style={styles.toggleLabel}>Share to Moments</Text>
                  <Text style={styles.toggleSub}>
                    {isPrivate
                      ? "Not available for private rooms"
                      : "Let others discover and join from your feed"}
                  </Text>
                </View>
                <Switch
                  testID="room-share-toggle"
                  value={shareToMoments && !isPrivate}
                  onValueChange={setShareToMoments}
                  disabled={isPrivate}
                  trackColor={{ true: colors.brand, false: colors.border }}
                />
              </View>
            </ScrollView>

            <View style={styles.createFooter}>
              <Pressable
                testID="room-create-submit-btn"
                style={[
                  styles.createBtn,
                  (!title.trim() || roomLangs.length === 0 || creating) && {
                    opacity: 0.4,
                  },
                ]}
                disabled={!title.trim() || roomLangs.length === 0 || creating}
                onPress={createRoom}
              >
                {creating ? (
                  <ActivityIndicator color={colors.onBrand} />
                ) : (
                  <Text style={styles.createText}>Start Voiceroom</Text>
                )}
              </Pressable>
            </View>
          </KeyboardAvoidingView>
        </SafeAreaView>
      </Modal>
    </SafeAreaView>
  );
}

const makeStyles = (colors: ThemeColors) =>
  StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: colors.surfaceSecondary,
    },
    header: {
      paddingHorizontal: spacing.xl,
      paddingTop: spacing.md,
      paddingBottom: spacing.sm,
    },
    headerTitle: {
      fontFamily: fonts.display,
      fontSize: 22,
      color: colors.onSurface,
    },
    headerSub: {
      fontFamily: fonts.text,
      fontSize: 13,
      color: colors.onSurfaceSecondary,
      marginTop: 2,
    },
    list: {
      padding: spacing.lg,
      paddingBottom: 110,
      gap: spacing.md,
    },
    cardWrap: {
      borderRadius: radius.lg,
      ...shadow.card,
    },
    card: {
      borderRadius: radius.lg,
      padding: spacing.lg,
      gap: spacing.md,
    },
    cardTop: {
      flexDirection: "row",
      justifyContent: "space-between",
      alignItems: "flex-start",
      gap: spacing.sm,
    },
    badgeRow: {
      flexDirection: "row",
      alignItems: "center",
      gap: 6,
      flexWrap: "wrap",
      flex: 1,
    },
    langBadge: {
      flexDirection: "row",
      alignItems: "center",
      gap: 4,
      backgroundColor: "rgba(255,255,255,0.2)",
      borderRadius: radius.pill,
      paddingHorizontal: spacing.sm,
      paddingVertical: 3,
    },
    langText: {
      fontFamily: fonts.textBold,
      fontSize: 10.5,
      color: "#FFFFFF",
    },
    topicBadge: {
      backgroundColor: "rgba(255,255,255,0.14)",
      borderRadius: radius.pill,
      paddingHorizontal: spacing.sm,
      paddingVertical: 3,
    },
    topicText: {
      fontFamily: fonts.textSemi,
      fontSize: 10.5,
      color: "rgba(255,255,255,0.9)",
    },
    liveBadge: {
      flexDirection: "row",
      alignItems: "center",
      gap: 5,
      backgroundColor: "rgba(0,0,0,0.28)",
      borderRadius: radius.pill,
      paddingHorizontal: spacing.sm,
      paddingVertical: 4,
    },
    liveText: {
      fontFamily: fonts.textBold,
      fontSize: 10,
      color: "#FFFFFF",
      letterSpacing: 0.8,
    },
    cardTitle: {
      fontFamily: fonts.displaySemi,
      fontSize: 17,
      color: "#FFFFFF",
      lineHeight: 23,
    },
    cardBottom: {
      flexDirection: "row",
      justifyContent: "space-between",
      alignItems: "center",
    },
    hostRow: {
      flexDirection: "row",
      alignItems: "center",
      gap: spacing.sm,
      flex: 1,
    },
    hostName: {
      fontFamily: fonts.textSemi,
      fontSize: 12.5,
      color: "rgba(255,255,255,0.85)",
      flexShrink: 1,
    },
    memberStack: {
      flexDirection: "row",
      alignItems: "center",
    },
    stackAvatar: {
      borderWidth: 1.5,
      borderColor: "rgba(255,255,255,0.5)",
      borderRadius: 14,
    },
    memberCountPill: {
      flexDirection: "row",
      alignItems: "center",
      gap: 3,
      backgroundColor: "rgba(0,0,0,0.28)",
      borderRadius: radius.pill,
      paddingHorizontal: 7,
      paddingVertical: 3,
      marginLeft: 6,
    },
    memberCountText: {
      fontFamily: fonts.textBold,
      fontSize: 11,
      color: "#FFFFFF",
    },
    center: {
      flex: 1,
      alignItems: "center",
      justifyContent: "center",
      gap: spacing.sm,
      padding: spacing.xl,
    },
    emptyTitle: {
      fontFamily: fonts.displaySemi,
      fontSize: 18,
      color: colors.onSurface,
      marginTop: spacing.md,
    },
    emptyIconCircle: {
      width: 88,
      height: 88,
      borderRadius: 44,
      alignItems: "center",
      justifyContent: "center",
    },
    emptyText: {
      fontFamily: fonts.text,
      fontSize: 14,
      color: colors.onSurfaceSecondary,
      textAlign: "center",
    },
    fab: {
      position: "absolute",
      right: spacing.xl,
      bottom: spacing.xl,
      flexDirection: "row",
      alignItems: "center",
      gap: spacing.xs,
      backgroundColor: colors.brand,
      borderRadius: radius.pill,
      paddingHorizontal: spacing.lg,
      paddingVertical: spacing.md,
      ...shadow.card,
    },
    fabText: {
      color: colors.onBrand,
      fontFamily: fonts.textBold,
      fontSize: 15,
    },
    createScreen: {
      flex: 1,
      backgroundColor: colors.surfaceSecondary,
    },
    createHeader: {
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "space-between",
      paddingHorizontal: spacing.lg,
      paddingVertical: spacing.md,
      backgroundColor: colors.surface,
      borderBottomWidth: StyleSheet.hairlineWidth,
      borderBottomColor: colors.border,
    },
    createHeaderTitle: {
      fontFamily: fonts.displaySemi,
      fontSize: 17,
      color: colors.onSurface,
    },
    createBody: {
      padding: spacing.lg,
      gap: spacing.md,
      paddingBottom: spacing.xxl,
    },
    topicInput: {
      backgroundColor: colors.surface,
      borderRadius: radius.md,
      padding: spacing.lg,
      fontFamily: fonts.displaySemi,
      fontSize: 18,
      color: colors.onSurface,
      minHeight: 70,
      textAlignVertical: "top",
      ...shadow.card,
    },
    sectionLabel: {
      fontFamily: fonts.textBold,
      fontSize: 12,
      color: colors.onSurfaceSecondary,
      textTransform: "uppercase",
      letterSpacing: 0.5,
      marginTop: spacing.xs,
    },
    langChip: {
      flexDirection: "row",
      alignItems: "center",
      gap: 6,
      paddingHorizontal: spacing.md,
      paddingVertical: spacing.sm,
      borderRadius: radius.pill,
      backgroundColor: colors.surface,
    },
    langChipActive: {
      backgroundColor: colors.brandTertiary,
    },
    langChipText: {
      fontFamily: fonts.textSemi,
      fontSize: 13,
      color: colors.onSurfaceTertiary,
    },
    langChipTextActive: {
      color: colors.onBrandTertiary,
      fontFamily: fonts.textBold,
    },
    modeGrid: {
      flexDirection: "row",
      flexWrap: "wrap",
      gap: spacing.sm,
    },
    modeItem: {
      width: "47%",
      backgroundColor: colors.surface,
      borderRadius: radius.md,
      paddingVertical: spacing.md,
      alignItems: "center",
      gap: 6,
      position: "relative",
      borderWidth: 1.5,
      borderColor: "transparent",
      ...shadow.card,
    },
    modeItemActive: {
      borderColor: colors.brand,
      backgroundColor: colors.brand,
    },
    modeItemLocked: {
      opacity: 0.6,
    },
    modeLabel: {
      fontFamily: fonts.textSemi,
      fontSize: 13,
      color: colors.onSurface,
    },
    modeLabelActive: {
      color: colors.onBrand,
      fontFamily: fonts.textBold,
    },
    modeLabelLocked: {
      color: colors.onSurfaceSecondary,
    },
    lockChip: {
      position: "absolute",
      top: 6,
      right: 6,
      flexDirection: "row",
      alignItems: "center",
      gap: 2,
      backgroundColor: colors.onSurfaceSecondary,
      borderRadius: radius.pill,
      paddingHorizontal: 5,
      paddingVertical: 1,
    },
    lockChipText: {
      fontFamily: fonts.textBold,
      fontSize: 8,
      color: "#FFFFFF",
    },
    bgRow: {
      flexDirection: "row",
      gap: spacing.md,
    },
    bgSwatchWrap: {
      borderRadius: 22,
    },
    bgSwatch: {
      width: 44,
      height: 44,
      borderRadius: 22,
      alignItems: "center",
      justifyContent: "center",
      borderWidth: 2,
      borderColor: "transparent",
    },
    bgSwatchActive: {
      borderColor: colors.onSurface,
    },
    toggleRow: {
      flexDirection: "row",
      alignItems: "center",
      backgroundColor: colors.surface,
      borderRadius: radius.md,
      padding: spacing.lg,
      gap: spacing.md,
      ...shadow.card,
    },
    toggleLabel: {
      fontFamily: fonts.textSemi,
      fontSize: 14.5,
      color: colors.onSurface,
    },
    toggleSub: {
      fontFamily: fonts.text,
      fontSize: 12,
      color: colors.onSurfaceSecondary,
      marginTop: 1,
    },
    createFooter: {
      padding: spacing.lg,
      backgroundColor: colors.surface,
      borderTopWidth: StyleSheet.hairlineWidth,
      borderTopColor: colors.border,
    },
    createBtn: {
      backgroundColor: colors.brand,
      borderRadius: radius.pill,
      paddingVertical: spacing.lg,
      alignItems: "center",
    },
    createText: {
      color: colors.onBrand,
      fontFamily: fonts.textBold,
      fontSize: 16,
    },
  });
