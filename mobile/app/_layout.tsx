import { Stack, router, useSegments } from 'expo-router';
import { useEffect, useState } from 'react';
import { ActivityIndicator, View } from 'react-native';
import { supabase } from '../src/lib/supabase';

export default function RootLayout(){
 const [ready,setReady]=useState(false); const [signedIn,setSignedIn]=useState(false); const segments=useSegments();
 useEffect(()=>{let mounted=true; supabase.auth.getSession().then(({data})=>{if(!mounted)return;setSignedIn(Boolean(data.session));setReady(true)});const {data:l}=supabase.auth.onAuthStateChange((_e,s)=>setSignedIn(Boolean(s)));return()=>{mounted=false;l.subscription.unsubscribe()}},[]);
 useEffect(()=>{if(!ready)return;const inLogin=segments[0]==='login';if(!signedIn&&!inLogin)router.replace('/login');if(signedIn&&inLogin)router.replace('/(tabs)/home')},[ready,signedIn,segments]);
 if(!ready)return <View style={{flex:1,justifyContent:'center',alignItems:'center'}}><ActivityIndicator/></View>;
 return <Stack screenOptions={{headerShown:false}}/>;
}
