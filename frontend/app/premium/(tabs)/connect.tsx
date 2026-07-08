import { Ionicons } from "@expo/vector-icons";
import { useFocusEffect, useRouter } from "expo-router";
import React, { useCallback, useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  Pressable,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { Avatar } from "@/src/components/Avatar";
import { countryToCode } from "@/src/constants/countries";
import { fonts } from "@/src/theme";
import { api } from "@/src/utils/api";
import { premiumColors, premiumRadius } from "@/src/premium/theme";

interface PremiumMember {
  id: string;
  name: string;
  avatar_url?: string;
  country?: string;
  learning_language?: string;
  native_language?: string;
  is_online?: boolean;
  is_vip?: boolean;
  vip_tier?: string;
  bio?: string;
  active_frame?: string;
}

export default function PremiumConnect() {
  const router = useRouter();
  const [members, setMembers] = useState<PremiumMember[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const data = await api.get<PremiumMember[]>("/users");
      // Only show VIPs — the premium club is members-only.
      setMembers(data.filter((u) => u.is_vip));
    } catch {
      // keep list
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
    <SafeAreaView
      style={styles.container}
      edges={["top"]}
      testID="premium-connect-screen"
    >
      <View style={styles.header}>
        <View style={{ flex: 1 }}>
          <Text style={styles.brand}>PREMIUM CLUB</Text>
          <Text style={styles.title}>Members</Text>
        </View>
        <View style={styles.countPill}>
          <Ionicons name="diamond" size={11} color={premiumColors.gold} />
          <Text style={styles.countText}>{members.length} online</Text>
        </View>
      </View>

      {loading ? (
        <View style={styles.center}>
          <ActivityIndicator size="large" color={premiumColors.gold} />
        </View>
      ) : (
        <FlatList
          data={members}
          keyExtractor={(m) => m.id}
          numColumns={2}
          columnWrapperStyle={{ gap: 12 }}
          contentContainerStyle={styles.list}
          ItemSeparatorComponent={() => <View style={{ height: 12 }} />}
          ListEmptyComponent={
            <View style={styles.emptyBox}>
              <View style={styles.emptyBadge}>
                <Ionicons name="diamond" size={28} color={premiumColors.gold} />
              </View>
              <Text style={styles.emptyTitle}>No members yet</Text>
              <Text style={styles.emptyBody}>
                Be the first premium member — upgrade your account.
              </Text>
            </View>
          }
          renderItem={({ item }) => (
            <Pressable
              testID={`premium-member-${item.id}`}
              onPress={() => router.push(`/user/${item.id}`)}
              style={styles.card}
            >
              <View style={styles.avatarRow}>
                <Avatar
                  name={item.name}
                  url={item.avatar_url}
                  size={62}
                  flagCode={countryToCode(item.country)}
                  online={item.is_online}
                  frame={item.active_frame}
                />
                <View style={styles.vipRibbon}>
                  <Ionicons name="diamond" size={9} color={premiumColors.onGold} />
                  <Text style={styles.vipRibbonText}>VIP</Text>
                </View>
              </View>
              <Text style={styles.name} numberOfLines={1}>
                {item.name}
              </Text>
              {item.bio ? (
                <Text style={styles.bio} numberOfLines={2}>
                  “{item.bio}”
                </Text>
              ) : (
                <Text style={styles.bioMuted}>Verified member</Text>
              )}
              <View style={styles.footerRow}>
                <View style={styles.langPill}>
                  <Text style={styles.langText} numberOfLines={1}>
                    {(item.learning_language || "lang").toUpperCase()}
                  </Text>
                </View>
                <Pressable
                  onPress={() => router.push(`/chat/new?userId=${item.id}`)}
                  style={styles.chatBtn}
                  testID={`premium-connect-chat-${item.id}`}
                >
                  <Ionicons
                    name="chatbubble-ellipses"
                    size={14}
                    color={premiumColors.onGold}
                  />
                </Pressable>
              </View>
            </Pressable>
          )}
        />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: premiumColors.bg },
  header: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    paddingHorizontal: 20,
    paddingTop: 6,
    paddingBottom: 12,
  },
  brand: {
    fontFamily: fonts.textBold,
    fontSize: 10,
    letterSpacing: 2,
    color: premiumColors.gold,
  },
  title: {
    fontFamily: fonts.displayBold,
    fontSize: 22,
    color: premiumColors.onSurface,
    marginTop: 2,
  },
  countPill: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    backgroundColor: premiumColors.surfaceRaised,
    borderRadius: premiumRadius.pill,
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderWidth: 1,
    borderColor: premiumColors.gold,
  },
  countText: {
    fontFamily: fonts.textBold,
    fontSize: 11,
    color: premiumColors.gold,
  },
  list: { paddingHorizontal: 20, paddingBottom: 40 },
  card: {
    flex: 1,
    backgroundColor: premiumColors.surfaceRaised,
    borderRadius: premiumRadius.xl,
    padding: 14,
    borderWidth: 1,
    borderColor: premiumColors.border,
    gap: 6,
    minHeight: 190,
  },
  avatarRow: {
    alignItems: "center",
    justifyContent: "center",
    position: "relative",
  },
  vipRibbon: {
    position: "absolute",
    bottom: -4,
    flexDirection: "row",
    alignItems: "center",
    gap: 3,
    backgroundColor: premiumColors.gold,
    borderRadius: premiumRadius.pill,
    paddingHorizontal: 8,
    paddingVertical: 2,
  },
  vipRibbonText: {
    fontFamily: fonts.textBold,
    fontSize: 9,
    color: premiumColors.onGold,
    letterSpacing: 0.5,
  },
  name: {
    fontFamily: fonts.displayBold,
    fontSize: 14,
    color: premiumColors.onSurface,
    marginTop: 8,
    textAlign: "center",
  },
  bio: {
    fontFamily: fonts.text,
    fontSize: 11,
    color: premiumColors.onSurfaceSecondary,
    textAlign: "center",
    fontStyle: "italic",
    minHeight: 30,
  },
  bioMuted: {
    fontFamily: fonts.textSemi,
    fontSize: 11,
    color: premiumColors.onSurfaceTertiary,
    textAlign: "center",
    minHeight: 30,
  },
  footerRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginTop: 4,
  },
  langPill: {
    backgroundColor: premiumColors.surfaceHigh,
    borderRadius: premiumRadius.pill,
    paddingHorizontal: 10,
    paddingVertical: 4,
  },
  langText: {
    fontFamily: fonts.textBold,
    fontSize: 10,
    color: premiumColors.gold,
    letterSpacing: 0.8,
  },
  chatBtn: {
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: premiumColors.gold,
    alignItems: "center",
    justifyContent: "center",
  },
  center: { flex: 1, alignItems: "center", justifyContent: "center" },
  emptyBox: {
    alignItems: "center",
    paddingHorizontal: 32,
    paddingTop: 60,
    gap: 8,
  },
  emptyBadge: {
    width: 76,
    height: 76,
    borderRadius: 38,
    backgroundColor: premiumColors.surfaceRaised,
    borderWidth: 2,
    borderColor: premiumColors.gold,
    alignItems: "center",
    justifyContent: "center",
  },
  emptyTitle: {
    fontFamily: fonts.displayBold,
    fontSize: 18,
    color: premiumColors.onSurface,
    marginTop: 10,
  },
  emptyBody: {
    fontFamily: fonts.textSemi,
    fontSize: 13,
    color: premiumColors.onSurfaceSecondary,
    textAlign: "center",
    lineHeight: 19,
  },
});
