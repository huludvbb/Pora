import { Ionicons } from "@expo/vector-icons";
import { Image } from "expo-image";
import * as ImagePicker from "expo-image-picker";
import { useRouter } from "expo-router";
import React, { useMemo, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { BackButton } from "@/src/components/BackButton";
import { useTheme } from "@/src/context/ThemeContext";
import { fonts, radius, spacing, ThemeColors } from "@/src/theme";
import { api } from "@/src/utils/api";

/**
 * Full-page moment composer. Opened via router.push('/moment-compose').
 * Order matches the user's request: photo picker area first, then a big
 * text area, then tag suggestions + a free-text "add your own" input.
 */

// Curated starter tag suggestions — the community picks up on these and users
// still get a custom-tag input to invent their own.
const SUGGESTED_TAGS = [
  "language",
  "practice",
  "questions",
  "grammar",
  "culture",
  "travel",
  "music",
  "food",
  "study",
  "motivation",
  "meetnewfriends",
  "exchange",
];

export default function MomentComposeScreen() {
  const router = useRouter();
  const { colors } = useTheme();
  const styles = useMemo(() => makeStyles(colors), [colors]);
  const [text, setText] = useState("");
  const [photo, setPhoto] = useState<{ base64: string; uri: string; mime: string } | null>(null);
  const [tags, setTags] = useState<string[]>([]);
  const [customTag, setCustomTag] = useState("");
  const [posting, setPosting] = useState(false);

  const pickPhoto = async () => {
    if (posting) return;
    if (Platform.OS !== "web") {
      const perm = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (!perm.granted) {
        Alert.alert(
          "Photos",
          "We need photo access to attach a picture. Enable it from Settings.",
        );
        return;
      }
    }
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ["images"],
      quality: 0.6,
      base64: true,
    });
    const asset = result.assets?.[0];
    if (result.canceled || !asset?.base64) return;
    setPhoto({
      base64: asset.base64,
      uri: asset.uri,
      mime: asset.mimeType || "image/jpeg",
    });
  };

  const toggleTag = (tag: string) => {
    setTags((prev) => {
      if (prev.includes(tag)) return prev.filter((t) => t !== tag);
      if (prev.length >= 8) return prev;
      return [...prev, tag];
    });
  };

  const addCustomTag = () => {
    const raw = customTag.trim().replace(/^#/, "").toLowerCase();
    const clean = raw.replace(/[^a-z0-9_]/g, "");
    if (!clean) return;
    if (tags.includes(clean) || tags.length >= 8) {
      setCustomTag("");
      return;
    }
    setTags((prev) => [...prev, clean]);
    setCustomTag("");
  };

  const publish = async () => {
    if (posting) return;
    if (!text.trim() && !photo) {
      Alert.alert("Nothing to post", "Add a photo, some text, or both.");
      return;
    }
    setPosting(true);
    try {
      await api.post("/moments", {
        text: text.trim(),
        image_base64: photo?.base64,
        mime: photo?.mime,
        tags,
      });
      router.back();
    } catch (e) {
      Alert.alert("Post", e instanceof Error ? e.message : "Could not post.");
    } finally {
      setPosting(false);
    }
  };

  const canPost = (text.trim().length > 0 || !!photo) && !posting;

  return (
    <SafeAreaView style={styles.screen} edges={["top"]}>
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : undefined}
        style={{ flex: 1 }}
      >
        <View style={styles.header}>
          <BackButton testID="compose-back-btn" />
          <Text style={styles.title}>New Moment</Text>
          <Pressable
            testID="compose-post-btn"
            onPress={publish}
            disabled={!canPost}
            style={[styles.postBtn, !canPost && { opacity: 0.5 }]}
          >
            {posting ? (
              <ActivityIndicator color="#FFFFFF" size="small" />
            ) : (
              <Text style={styles.postBtnText}>Post</Text>
            )}
          </Pressable>
        </View>

        <ScrollView
          contentContainerStyle={styles.body}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          {/* Photo section */}
          {photo ? (
            <View style={styles.photoBox}>
              <Image source={{ uri: photo.uri }} style={styles.photo} contentFit="cover" />
              <Pressable
                testID="compose-photo-remove-btn"
                style={styles.photoRemove}
                onPress={() => setPhoto(null)}
              >
                <Ionicons name="close" size={16} color="#FFF" />
              </Pressable>
            </View>
          ) : (
            <Pressable
              testID="compose-photo-add-btn"
              onPress={pickPhoto}
              style={styles.photoPlaceholder}
            >
              <Ionicons name="image-outline" size={30} color={colors.brand} />
              <Text style={styles.photoPlaceholderText}>Add a photo</Text>
              <Text style={styles.photoPlaceholderHint}>Optional — tap to attach</Text>
            </Pressable>
          )}

          {/* Text section */}
          <TextInput
            testID="compose-text-input"
            style={styles.textInput}
            placeholder="Share what's on your mind — ask a language question, tell a story, celebrate a win…"
            placeholderTextColor={colors.onSurfaceSecondary}
            value={text}
            onChangeText={setText}
            multiline
            maxLength={1000}
            autoFocus
          />
          <Text style={styles.counter}>{text.length}/1000</Text>

          {/* Tags section */}
          <View style={styles.tagSection}>
            <View style={styles.tagHeader}>
              <Ionicons name="pricetag" size={15} color={colors.onSurfaceSecondary} />
              <Text style={styles.tagLabel}>Tags</Text>
              <Text style={styles.tagCounter}>{tags.length}/8</Text>
            </View>

            {tags.length > 0 && (
              <View style={styles.chipRow}>
                {tags.map((t) => (
                  <Pressable
                    key={t}
                    testID={`compose-tag-selected-${t}`}
                    onPress={() => toggleTag(t)}
                    style={styles.chipSelected}
                  >
                    <Text style={styles.chipSelectedText}>#{t}</Text>
                    <Ionicons name="close" size={13} color="#FFFFFF" />
                  </Pressable>
                ))}
              </View>
            )}

            <Text style={styles.suggestLabel}>Suggested</Text>
            <View style={styles.chipRow}>
              {SUGGESTED_TAGS.filter((t) => !tags.includes(t)).map((t) => (
                <Pressable
                  key={t}
                  testID={`compose-tag-suggest-${t}`}
                  onPress={() => toggleTag(t)}
                  style={styles.chipSuggest}
                >
                  <Text style={styles.chipSuggestText}>#{t}</Text>
                </Pressable>
              ))}
            </View>

            <Text style={styles.suggestLabel}>Add your own</Text>
            <View style={styles.customTagRow}>
              <View style={styles.customInputWrap}>
                <Text style={styles.hashPrefix}>#</Text>
                <TextInput
                  testID="compose-tag-custom-input"
                  style={styles.customInput}
                  value={customTag}
                  onChangeText={setCustomTag}
                  placeholder="mytag"
                  placeholderTextColor={colors.onSurfaceSecondary}
                  autoCapitalize="none"
                  onSubmitEditing={addCustomTag}
                  returnKeyType="done"
                  maxLength={30}
                />
              </View>
              <Pressable
                testID="compose-tag-add-btn"
                onPress={addCustomTag}
                disabled={!customTag.trim() || tags.length >= 8}
                style={[
                  styles.addBtn,
                  (!customTag.trim() || tags.length >= 8) && { opacity: 0.4 },
                ]}
              >
                <Ionicons name="add" size={20} color="#FFFFFF" />
              </Pressable>
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const makeStyles = (colors: ThemeColors) =>
  StyleSheet.create({
    screen: { flex: 1, backgroundColor: colors.background },
    header: {
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "space-between",
      paddingHorizontal: spacing.md,
      paddingVertical: spacing.sm,
      borderBottomWidth: StyleSheet.hairlineWidth,
      borderBottomColor: colors.border,
    },
    title: { fontFamily: fonts.displaySemi, fontSize: 17, color: colors.onSurface },
    postBtn: {
      backgroundColor: colors.brand,
      borderRadius: radius.pill,
      paddingHorizontal: spacing.lg,
      paddingVertical: 8,
      minWidth: 68,
      alignItems: "center",
    },
    postBtnText: { fontFamily: fonts.textBold, fontSize: 14, color: "#FFFFFF" },
    body: { padding: spacing.lg, gap: spacing.md, paddingBottom: spacing.xxl * 2 },
    photoBox: {
      borderRadius: radius.md,
      overflow: "hidden",
      backgroundColor: colors.surfaceSecondary,
      aspectRatio: 4 / 3,
    },
    photo: { width: "100%", height: "100%" },
    photoRemove: {
      position: "absolute",
      top: 10,
      right: 10,
      width: 28,
      height: 28,
      borderRadius: 14,
      backgroundColor: "rgba(0,0,0,0.55)",
      alignItems: "center",
      justifyContent: "center",
    },
    photoPlaceholder: {
      backgroundColor: colors.surfaceSecondary,
      borderRadius: radius.md,
      borderWidth: 2,
      borderColor: colors.border,
      borderStyle: "dashed",
      alignItems: "center",
      justifyContent: "center",
      paddingVertical: spacing.xxl,
      gap: 4,
    },
    photoPlaceholderText: {
      fontFamily: fonts.textBold,
      fontSize: 14,
      color: colors.onSurface,
    },
    photoPlaceholderHint: {
      fontFamily: fonts.textSemi,
      fontSize: 12,
      color: colors.onSurfaceSecondary,
    },
    textInput: {
      minHeight: 120,
      fontFamily: fonts.textSemi,
      fontSize: 16,
      color: colors.onSurface,
      lineHeight: 22,
      textAlignVertical: "top",
      ...(Platform.OS === "web" ? ({ outlineStyle: "none" } as object) : {}),
    },
    counter: {
      alignSelf: "flex-end",
      fontFamily: fonts.textSemi,
      fontSize: 11,
      color: colors.onSurfaceSecondary,
    },
    tagSection: {
      marginTop: spacing.md,
      gap: spacing.sm,
    },
    tagHeader: {
      flexDirection: "row",
      alignItems: "center",
      gap: 6,
    },
    tagLabel: {
      fontFamily: fonts.textBold,
      fontSize: 13,
      color: colors.onSurface,
      textTransform: "uppercase",
      letterSpacing: 0.5,
      flex: 1,
    },
    tagCounter: {
      fontFamily: fonts.textSemi,
      fontSize: 12,
      color: colors.onSurfaceSecondary,
    },
    chipRow: {
      flexDirection: "row",
      flexWrap: "wrap",
      gap: 8,
    },
    chipSelected: {
      flexDirection: "row",
      alignItems: "center",
      gap: 4,
      backgroundColor: colors.brand,
      borderRadius: radius.pill,
      paddingHorizontal: 12,
      paddingVertical: 6,
    },
    chipSelectedText: {
      fontFamily: fonts.textBold,
      fontSize: 12,
      color: "#FFFFFF",
    },
    chipSuggest: {
      backgroundColor: colors.surfaceSecondary,
      borderRadius: radius.pill,
      paddingHorizontal: 12,
      paddingVertical: 6,
    },
    chipSuggestText: {
      fontFamily: fonts.textBold,
      fontSize: 12,
      color: colors.onSurface,
    },
    suggestLabel: {
      fontFamily: fonts.textBold,
      fontSize: 11,
      color: colors.onSurfaceSecondary,
      textTransform: "uppercase",
      letterSpacing: 0.4,
      marginTop: spacing.sm,
    },
    customTagRow: {
      flexDirection: "row",
      alignItems: "center",
      gap: 8,
      marginTop: 2,
    },
    customInputWrap: {
      flex: 1,
      flexDirection: "row",
      alignItems: "center",
      backgroundColor: colors.surfaceSecondary,
      borderRadius: radius.pill,
      paddingHorizontal: 14,
      paddingVertical: 8,
    },
    hashPrefix: {
      fontFamily: fonts.textBold,
      fontSize: 15,
      color: colors.brand,
      marginRight: 4,
    },
    customInput: {
      flex: 1,
      fontFamily: fonts.textSemi,
      fontSize: 14,
      color: colors.onSurface,
      padding: 0,
      ...(Platform.OS === "web" ? ({ outlineStyle: "none" } as object) : {}),
    },
    addBtn: {
      width: 40,
      height: 40,
      borderRadius: 20,
      backgroundColor: colors.brand,
      alignItems: "center",
      justifyContent: "center",
    },
  });
