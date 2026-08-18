# CarbonERP Mobile

CarbonERP'nin mobil operasyon uygulaması. Web yönetim paneli ile aynı Supabase veritabanını kullanır.

## Mimari

- React Native + Expo + Expo Router
- Supabase Auth + RLS
- Publishable key ile istemci bağlantısı
- Kritik satış, iade, teslimat ve stok işlemleri `secure-rpc` Edge Function üzerinden
- Offline çalışma yok: internet/Supabase bağlantısı olmadan işletme işlemleri yapılmaz
- Android ve iOS hedeflenir

## Mobil özellikler

- Güvenli giriş ve oturum yenileme
- Ana panel ve hızlı işlem kartları
- Müşteri arama, müşteri oluşturma ve cari kart görüntüleme
- Ürün arama, stok/fiyat görüntüleme ve ürün oluşturma
- Yeni satış oluşturma
- Satış geçmişi
- Tahsilat geçmişi ve yeni tahsilat
- Stok sayımı ve maliyetli mevcut stok girişi
- Teslimat/sipariş görünümü
- Mobil rapor özeti
- Çıkış ve oturum yönetimi

## Kurulum

```bash
cd mobile
npm install
npx expo start
```

`.env` içinde:

```text
EXPO_PUBLIC_SUPABASE_URL=https://YOUR_PROJECT.supabase.co
EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY=YOUR_PUBLISHABLE_KEY
```

Telefonunda Expo Go ile QR kodu okutabilir veya Android Studio/emülatör ile çalıştırabilirsin.

## Güvenlik

Service-role key mobil uygulamaya konulmaz. Kritik işlemler JWT ile doğrulanan `secure-rpc` fonksiyonundan geçer ve yalnızca yetkili admin hesabı için izin verilir. RLS veritabanı katmanında aktiftir.

## Bilinçli kapsam dışı

- Offline veri/senkronizasyon yok.
- Fiziksel cihaz üzerinde bu ortamdan Android/iOS derlemesi çalıştırılamadı; son doğrulama yerel Expo/Android Studio veya Expo Go üzerinde yapılmalıdır.
