import { router } from 'expo-router';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { supabase } from '../../src/lib/supabase';

const cards = [
  ['Yeni Satış','Hızlı satış oluştur','/sales/new'],
  ['Tahsilat','Müşteri bakiyesi ve tahsilat','/finance'],
  ['Stok Sayımı','Mevcut stoğu say ve kaydet','/operations'],
  ['Siparişler','Teslimatları takip et','/operations'],
];

export default function Home() {
  async function logout(){ await supabase.auth.signOut(); router.replace('/login'); }
  return <ScrollView style={styles.page} contentContainerStyle={styles.content}>
    <View style={styles.header}><View><Text style={styles.brand}>CarbonERP</Text><Text style={styles.sub}>Mobil operasyon</Text></View><Pressable onPress={logout}><Text style={styles.logout}>Çıkış</Text></Pressable></View>
    <Text style={styles.title}>Bugün</Text>
    <View style={styles.stats}><Stat label="Müşteri" table="customers"/><Stat label="Ürün" table="products"/><Stat label="Açık sipariş" table="delivery_orders"/></View>
    <Text style={styles.section}>Hızlı işlemler</Text>
    {cards.map(([title,sub,path])=><Pressable key={title} style={styles.card} onPress={()=>router.push(path as any)}><Text style={styles.cardTitle}>{title}</Text><Text style={styles.cardSub}>{sub}</Text></Pressable>)}
  </ScrollView>
}
function Stat({label,table}:{label:string;table:string}){ const [count,setCount]=require('react').useState<number|null>(null); require('react').useEffect(()=>{supabase.from(table).select('*',{count:'exact',head:true}).then(r=>setCount(r.count??0))},[table]); return <View style={styles.stat}><Text style={styles.statValue}>{count ?? '—'}</Text><Text style={styles.statLabel}>{label}</Text></View> }
const styles=StyleSheet.create({page:{flex:1,backgroundColor:'#f7f8fa'},content:{padding:20,paddingBottom:30},header:{flexDirection:'row',justifyContent:'space-between',alignItems:'center',marginBottom:28},brand:{fontSize:28,fontWeight:'800'},sub:{color:'#6b7280',marginTop:2},logout:{fontWeight:'700'},title:{fontSize:24,fontWeight:'800',marginBottom:14},stats:{flexDirection:'row',gap:10,marginBottom:26},stat:{flex:1,backgroundColor:'#fff',borderRadius:14,padding:14,borderWidth:1,borderColor:'#e5e7eb'},statValue:{fontSize:22,fontWeight:'800'},statLabel:{color:'#6b7280',marginTop:3},section:{fontSize:18,fontWeight:'700',marginBottom:10},card:{backgroundColor:'#fff',padding:18,borderRadius:16,borderWidth:1,borderColor:'#e5e7eb',marginBottom:10},cardTitle:{fontSize:17,fontWeight:'700'},cardSub:{color:'#6b7280',marginTop:4}});
