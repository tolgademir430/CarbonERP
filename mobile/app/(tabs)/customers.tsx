import { useEffect, useState } from 'react';
import { ActivityIndicator, FlatList, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { router } from 'expo-router';
import { supabase } from '../../src/lib/supabase';

type Customer={id:string;name:string;phone:string|null;city:string|null;customer_code:string|null;credit_limit:number|null};
export default function Customers(){
 const [items,setItems]=useState<Customer[]>([]); const [q,setQ]=useState(''); const [loading,setLoading]=useState(true);
 async function load(){setLoading(true); let query=supabase.from('customers').select('id,name,phone,city,customer_code,credit_limit').eq('is_active',true).order('name').limit(100); if(q.trim()) query=query.ilike('name',`%${q.trim()}%`); const {data}=await query; setItems((data??[]) as Customer[]); setLoading(false)}
 useEffect(()=>{load()},[q]);
 return <View style={styles.page}><TextInput style={styles.search} placeholder="Müşteri ara..." value={q} onChangeText={setQ}/>{loading?<ActivityIndicator style={{marginTop:30}}/>:<FlatList data={items} keyExtractor={x=>x.id} renderItem={({item})=><Pressable style={styles.row} onPress={()=>router.push({pathname:'/customer/[id]',params:{id:item.id}})}><View style={{flex:1}}><Text style={styles.name}>{item.name}</Text><Text style={styles.meta}>{item.customer_code??'Kod yok'}{item.city?` • ${item.city}`:''}</Text>{item.phone?<Text style={styles.meta}>{item.phone}</Text>:null}</View><Text style={styles.arrow}>›</Text></Pressable>}/>}</View>
}
const styles=StyleSheet.create({page:{flex:1,backgroundColor:'#f7f8fa',padding:16},search:{backgroundColor:'#fff',borderWidth:1,borderColor:'#e5e7eb',borderRadius:12,padding:13,fontSize:16,marginBottom:12},row:{backgroundColor:'#fff',borderRadius:14,padding:16,marginBottom:9,flexDirection:'row',alignItems:'center',borderWidth:1,borderColor:'#e5e7eb'},name:{fontSize:16,fontWeight:'700'},meta:{color:'#6b7280',marginTop:3},arrow:{fontSize:28,color:'#9ca3af'}});
