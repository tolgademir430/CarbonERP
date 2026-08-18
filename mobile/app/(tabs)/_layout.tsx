import { Tabs } from 'expo-router';
import { Text } from 'react-native';
const icon=(label:string)=>(props:{color:string})=><Text style={{color:props.color,fontSize:17}}>{label}</Text>;
export default function TabsLayout(){return <Tabs screenOptions={{headerShown:true,tabBarActiveTintColor:'#111827',tabBarLabelStyle:{fontSize:11,fontWeight:'600'}}}>
<Tabs.Screen name="home" options={{title:'Ana Sayfa',tabBarLabel:'Ana',tabBarIcon:icon('⌂')}}/>
<Tabs.Screen name="customers" options={{title:'Müşteriler',tabBarLabel:'Müşteri',tabBarIcon:icon('👤')}}/>
<Tabs.Screen name="products" options={{title:'Ürünler ve Stok',tabBarLabel:'Stok',tabBarIcon:icon('▣')}}/>
<Tabs.Screen name="sales" options={{title:'Satışlar',tabBarLabel:'Satış',tabBarIcon:icon('₺')}}/>
<Tabs.Screen name="finance" options={{title:'Cari ve Tahsilat',tabBarLabel:'Cari',tabBarIcon:icon('●')}}/>
<Tabs.Screen name="operations" options={{title:'Operasyon',tabBarLabel:'Operasyon',tabBarIcon:icon('↗')}}/>
<Tabs.Screen name="reports" options={{title:'Raporlar',tabBarLabel:'Rapor',tabBarIcon:icon('▥')}}/>
</Tabs>}
