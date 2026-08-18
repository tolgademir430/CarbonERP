import { router } from 'expo-router';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { supabase } from '../src/lib/supabase';

const actions = [
  ['Müşteriler', 'Müşteri ve cari kart'],
  ['Yeni Satış', 'Hızlı satış oluştur'],
  ['Tahsilat', 'Müşteri bakiyesi'],
  ['Ürünler', 'Ürün ve stok'],
  ['Stok Sayımı', 'Mevcut stok girişi'],
  ['Siparişler', 'Sipariş ve teslimat'],
];

export default function HomeScreen() {
  async function logout() {
    await supabase.auth.signOut();
    router.replace('/login');
  }

  return <View style={styles.container}>
    <View style={styles.header}><View><Text style={styles.brand}>CarbonERP</Text><Text style={styles.caption}>İşletme paneli</Text></View><Pressable onPress={logout}><Text style={styles.logout}>Çıkış</Text></Pressable></View>
    <Text style={styles.title}>Bugün ne yapmak istiyorsun?</Text>
    <View style={styles.grid}>{actions.map(([title, subtitle]) => <Pressable key={title} style={styles.card}><Text style={styles.cardTitle}>{title}</Text><Text style={styles.cardSubtitle}>{subtitle}</Text></Pressable>)}</View>
  </View>;
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f7f8fa', padding: 20, paddingTop: 58 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 34 },
  brand: { fontSize: 26, fontWeight: '800' },
  caption: { color: '#6b7280', marginTop: 2 },
  logout: { fontWeight: '700' },
  title: { fontSize: 22, fontWeight: '700', marginBottom: 18 },
  grid: { gap: 12 },
  card: { backgroundColor: '#fff', borderRadius: 16, padding: 18, borderWidth: 1, borderColor: '#e5e7eb' },
  cardTitle: { fontSize: 17, fontWeight: '700' },
  cardSubtitle: { color: '#6b7280', marginTop: 5 }
});
