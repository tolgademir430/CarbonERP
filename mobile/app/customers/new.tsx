import { useState } from 'react';
import { Alert, Pressable, ScrollView, StyleSheet, Text, TextInput } from 'react-native';
import { router } from 'expo-router';
import { supabase } from '../../src/lib/supabase';

export default function NewCustomer(){
 const [name,setName]=useState(''); const [phone,setPhone]=useState(''); const [city,setCity]=useState(''); const [code,setCode]=useState(''); const [loading,setLoading]=useState(false);
 async function save(){ if(!name.trim()){Alert.alert('Eksik bilgi','Müşteri adı gerekli.');return} setLoading(true); const {data:{user}}=await supabase.auth.getUser(); const {error}=await supabase.from('customers').insert({name:name.trim(),phone:phone.trim()||null,city:city.trim()||null,customer_code:code.trim()||null,updated_by:user?.id}); setLoading(false); if(error){Alert.alert('Kaydedilemedi',error.message);return} Alert.alert('Başarılı','Müşteri oluşturuldu.'); router.back(); }
 return <ScrollView style={s.page} contentContainerStyle={{paddingBottom:40}}><Text style={s.title}>Yeni müşteri</Text><Text style={s.label}>Müşteri adı</Text><TextInput style={s.input} value={name} onChangeText={setName} placeholder="Örn. ABC Restaurant"/><Text style={s.label}>Cari kodu</Text><TextInput style={s.input} value={code} onChangeText={setCode} placeholder="İsteğe bağlı"/><Text style={s.label}>Telefon</Text><TextInput style={s.input} value={phone} onChangeText={setPhone} keyboardType="phone-pad"/><Text style={s.label}>Şehir</Text><TextInput style={s.input} value={city} onChangeText={setCity}/><Pressable style={s.button} onPress={save} disabled={loading}><Text style={s.buttonText}>{loading?'Kaydediliyor...':'Müşteriyi kaydet'}</Text></Pressable></ScrollView>
}
const s=StyleSheet.create({page:{flex:1,backgroundColor:'#f7f8fa',padding:18},title:{fontSize:27,fontWeight:'800',marginBottom:20},label:{fontWeight:'700',marginTop:12,marginBottom:7},input:{backgroundColor:'#fff',borderWidth:1,borderColor:'#e5e7eb',borderRadius:12,padding:14,fontSize:16},button:{backgroundColor:'#111827',padding:16,borderRadius:14,alignItems:'center',marginTop:22},buttonText:{color:'#fff',fontWeight:'800'}});
