import { useState } from 'react';
import { Alert, Pressable, ScrollView, StyleSheet, Text, TextInput } from 'react-native';
import { router } from 'expo-router';
import { supabase } from '../../src/lib/supabase';

export default function NewProduct(){
 const [name,setName]=useState(''); const [code,setCode]=useState(''); const [unit,setUnit]=useState('kg'); const [sale,setSale]=useState(''); const [purchase,setPurchase]=useState(''); const [min,setMin]=useState(''); const [loading,setLoading]=useState(false);
 async function save(){if(!name.trim()){Alert.alert('Eksik bilgi','Ürün adı gerekli.');return}setLoading(true);const {error}=await supabase.from('products').insert({name:name.trim(),product_code:code.trim()||null,unit:unit.trim()||'kg',sale_price:Number(sale||0),purchase_price:Number(purchase||0),min_stock:Number(min||0)});setLoading(false);if(error){Alert.alert('Kaydedilemedi',error.message);return}Alert.alert('Başarılı','Ürün oluşturuldu.');router.back()}
 return <ScrollView style={s.page} contentContainerStyle={{paddingBottom:40}}><Text style={s.title}>Yeni ürün</Text><Field label="Ürün adı" value={name} onChange={setName}/><Field label="Ürün kodu" value={code} onChange={setCode}/><Field label="Birim" value={unit} onChange={setUnit}/><Field label="Alış fiyatı" value={purchase} onChange={setPurchase} numeric/><Field label="Satış fiyatı" value={sale} onChange={setSale} numeric/><Field label="Minimum stok" value={min} onChange={setMin} numeric/><Pressable style={s.button} onPress={save} disabled={loading}><Text style={s.buttonText}>{loading?'Kaydediliyor...':'Ürünü kaydet'}</Text></Pressable></ScrollView>
}
function Field({label,value,onChange,numeric}:{label:string;value:string;onChange:(v:string)=>void;numeric?:boolean}){return <><Text style={s.label}>{label}</Text><TextInput style={s.input} value={value} onChangeText={onChange} keyboardType={numeric?'decimal-pad':'default'}/></>}
const s=StyleSheet.create({page:{flex:1,backgroundColor:'#f7f8fa',padding:18},title:{fontSize:27,fontWeight:'800',marginBottom:20},label:{fontWeight:'700',marginTop:12,marginBottom:7},input:{backgroundColor:'#fff',borderWidth:1,borderColor:'#e5e7eb',borderRadius:12,padding:14,fontSize:16},button:{backgroundColor:'#111827',padding:16,borderRadius:14,alignItems:'center',marginTop:22},buttonText:{color:'#fff',fontWeight:'800'}});
