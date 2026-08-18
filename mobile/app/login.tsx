import { useState } from 'react';
import { ActivityIndicator, Alert, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { router } from 'expo-router';
import { supabase } from '../src/lib/supabase';

export default function LoginScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  async function login() {
    if (!email.trim() || !password) {
      Alert.alert('Eksik bilgi', 'E-posta ve şifreyi girin.');
      return;
    }
    setLoading(true);
    const { error } = await supabase.auth.signInWithPassword({ email: email.trim(), password });
    setLoading(false);
    if (error) {
      Alert.alert('Giriş başarısız', error.message);
      return;
    }
    router.replace('/');
  }

  return <View style={styles.container}>
    <Text style={styles.brand}>CarbonERP</Text>
    <Text style={styles.title}>Giriş yap</Text>
    <Text style={styles.subtitle}>Devam etmek için hesabınızla giriş yapın.</Text>
    <TextInput style={styles.input} placeholder="E-posta" autoCapitalize="none" keyboardType="email-address" value={email} onChangeText={setEmail} />
    <TextInput style={styles.input} placeholder="Şifre" secureTextEntry value={password} onChangeText={setPassword} />
    <Pressable style={styles.button} onPress={login} disabled={loading}>
      {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>Giriş yap</Text>}
    </Pressable>
  </View>;
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 24, backgroundColor: '#f7f8fa' },
  brand: { fontSize: 30, fontWeight: '800', marginBottom: 28 },
  title: { fontSize: 26, fontWeight: '700', marginBottom: 8 },
  subtitle: { color: '#6b7280', marginBottom: 24 },
  input: { backgroundColor: '#fff', borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 12, padding: 14, marginBottom: 12, fontSize: 16 },
  button: { backgroundColor: '#111827', borderRadius: 12, padding: 15, alignItems: 'center', marginTop: 8 },
  buttonText: { color: '#fff', fontWeight: '700', fontSize: 16 }
});
