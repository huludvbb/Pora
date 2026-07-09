import { Redirect } from "expo-router";
import React from "react";

// Landing on /pro drops the user into the Home (Pulse) screen.
export default function ProIndex() {
  return <Redirect href="/pro/home" />;
}
