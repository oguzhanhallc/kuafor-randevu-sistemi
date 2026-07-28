<img width="445" height="429" alt="Admin Girişi" src="https://github.com/user-attachments/assets/e7458ca1-b8fe-4e72-a62e-b190f74b8b33" />

Sistem üzerindeki tüm randevu süreçleri, yetkili erişim protokolüne tabi olan yönetim paneli üzerinden sevk ve idare edilmektedir.
(All appointment processes within the system are managed and routed through the admin panel, which requires authorized access.)



<img width="820" height="522" alt="YönetimPaneli" src="https://github.com/user-attachments/assets/90c79a24-16c9-4860-b1bb-bd0ed0f034b0" />

Veritabanı, kullanıcı formu ile tam entegre ve dinamik bir yapıda çalışmaktadır. Müşterilerin randevu alabilmesi için öncelikle yetkili 
kullanıcının "Mesai Saatlerini Yönet" sayfasına erişmesi, ilgili parametreleri belirledikten sonra "Mesai Saatlerini Oluştur" adımıyla 
işlemi tamamlaması gerekmektedir. Sistem, girilen zaman aralığına göre otomatik olarak 30'ar dakikalık dinamik randevu slotları tanımlamaktadır.

(The database operates dynamically in full integration with the user form. For a customer to book an appointment, 
the authorized user must first navigate to the "Manage Working Hours" page, select the relevant parameters, 
and click "Create Working Hours". Based on the defined time interval, the system automatically generates dynamic 30-minute appointment slots.)

<img width="693" height="862" alt="MesaiSaat" src="https://github.com/user-attachments/assets/e2cbce83-2c39-4d78-803b-7d89ef0da651" />


<img width="937" height="721" alt="AnaSayfa" src="https://github.com/user-attachments/assets/574708c3-756f-4b61-adcc-d8fac3c0b920" />

Mesai saatleri tanımlandıktan sonra Ana Sayfa üzerinden "Randevu Al" sekmesine geçiş yapılarak kullanıcı bilgileri sisteme girilmektedir.

(Once the working hours are defined, users navigate to the "Book an Appointment" page via the Home Page to enter their information into the system.)


<img width="757" height="761" alt="önce" src="https://github.com/user-attachments/assets/d6c26da8-8a57-4cbe-a233-ef87c6506af2" />

<img width="682" height="933" alt="sonra" src="https://github.com/user-attachments/assets/f943c5d6-51cb-4633-abeb-156c07aa82b0" />

Hizmet seçimi aşamasında sistem; hizmet-rol eşleşmesini kontrol ederek uygun randevu saatine sahip personeli ve işlem detaylarını dinamik olarak listeler.
Randevu süresi standart olarak 30 dakikalık slotlar halinde hesaplanmakta olup,2 hizmet seçilmesi durumunda sistem otomatik olarak birbirini takip eden bir 
sonraki zaman slotunu da randevu süresine dahil ederek kaydı onaylar.

(During the service selection phase, the system cross-references the service-role matching to dynamically list available staff and details. 
A single service slot is standardized at 30 minutes; when two services are selected, the system automatically incorporates the consecutive 
time slot into the booking and confirms the reservation.)

<img width="707" height="896" alt="sorgulama" src="https://github.com/user-attachments/assets/fbe50250-fe9e-4096-b097-469ce7974557" />

Kullanıcılar dilerlerse Ana Sayfa üzerinden "Randevu Sorgula" sayfasına erişerek, kayıtlı telefon numaraları ile mevcut randevu 
detaylarını ve durumlarını kolayca sorgulayabilmektedir.

(If desired, users can navigate to the "Query Appointment" page via the Home Page to easily check their existing appointment 
details and status using their registered phone number.)


<img width="766" height="459" alt="RL" src="https://github.com/user-attachments/assets/893e5fde-8c10-465a-b66e-74615a0522c9" />
<img width="787" height="757" alt="RİP" src="https://github.com/user-attachments/assets/540ca6a1-125d-469e-865a-fe8e336a28ab" />


Ek olarak yönetim paneli bünyesindeki "Randevu Listesi" sayfası üzerinden tüm aktif randevular görüntülenebilmektedir. 
İptal işlemleri için ise "Randevu İptal" sayfasına geçiş yapılarak ilgili personel filtrelenmekte, randevu detayları 
incelendikten sonra iptal işlemi güvenli bir şekilde gerçekleştirilebilmektedir.

(Additionally, all active appointments can be viewed via the "Appointment List" page within the admin panel. 
For cancellation operations, users can navigate to the "Cancel Appointment" page, filter by the relevant staff member, 
review the booking details, and safely perform the cancellation.)

