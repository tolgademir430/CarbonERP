import { Tabs } from 'expo-router';

export default function TabsLayout() {
  return <Tabs screenOptions={{ headerShown: true, tabBarActiveTintColor: '#111827' }}>
    <Tabs.Screen name="home" options={{ title: 'Ana Sayfa', tabBarLabel: 'Ana Sayfa' }} />
    <Tabs.Screen name="customers" options={{ title: 'Müşteriler', tabBarLabel: 'Müşteri' }} />
    <Tabs.Screen name="products" options={{ title: 'Ürünler', tabBarLabel: 'Stok' }} />
    <Tabs.Screen name="sales" options={{ title: 'Satışlar', tabBarLabel: 'Satış' }} />
    <Tabs.Screen name="finance" options={{ title: 'Cari & Tahsilat', tabBarLabel: 'Cari' }} />
    <Tabs.Screen name="operations" options={{ title: 'Operasyon', tabBarLabel: 'Operasyon' }} />
  </Tabs>
}
