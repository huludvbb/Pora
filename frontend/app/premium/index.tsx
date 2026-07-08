import { Redirect } from "expo-router";
import React from "react";

// Landing on /premium simply drops the user into the club's chats tab.
export default function PremiumIndex() {
  return <Redirect href="/premium/chats" />;
}
