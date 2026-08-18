import { Stack } from 'expo-router';
import { useEffect, useState } from 'react';
import { ActivityIndicator, View } from 'react-native';
import { supabase } from '../src/lib/supabase';

export default function RootLayout() {
  const [ready, setReady] = useState(false);
  const [signedIn, setSignedIn] = useState(false);

  useEffect(() => {
    let mounted = true;
    supabase.auth.getSession().then(({ data }) => {
      if (!mounted) return;
      setSignedIn(Boolean(data.session));
      setReady(true);
    });
    const { data: listener } = supabase.auth.onAuthStateChange((_event, session) => {
      setSignedIn(Boolean(session));
    });
    return () => {
      mounted = false;
      listener.subscription.unsubscribe();
    };
  }, []);

  if (!ready) {
    return <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}><ActivityIndicator /></View>;
  }

  return <Stack screenOptions={{ headerShown: false }}><Stack.Screen name="index" /><Stack.Screen name="login" /></Stack>;
}
