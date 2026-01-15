import React, { useState } from 'react';
import {
  Truck,
  Clock,
  MapPin,
  ClipboardList,
  Package,
  QrCode,
  Trash2,
  CheckCircle,
  Fuel,
  BarChart3,
  Timer,
  FlaskConical,
  FileText,
  Shield,
  Blocks,
  Globe,
  Rocket,
  ChevronRight,
  Sparkles
} from 'lucide-react';

// Feature data
const features = [
  {
    id: 1,
    icon: Truck,
    title: "Gerçek Zamanlı Araç Takibi",
    capability: "Atölye ve garajlara giren araçların anlık durumunun dijital ikizi",
    value: "Bekleme süreleri azalır, darboğazlar görünür hale gelir",
    color: "from-blue-500 to-blue-600",
    bgColor: "bg-blue-50",
    iconColor: "text-blue-600"
  },
  {
    id: 2,
    icon: Clock,
    title: "Araç Yaşam Döngüsü Yönetimi",
    capability: "Araçların girişten çıkışa tüm bakım-onarım sürecinin izlenmesi",
    value: "Plansız iş emirleri ve tekrar eden arızalar düşer",
    color: "from-emerald-500 to-emerald-600",
    bgColor: "bg-emerald-50",
    iconColor: "text-emerald-600"
  },
  {
    id: 3,
    icon: MapPin,
    title: "Akıllı Atölye Haritası",
    capability: "24 atölye ve posta yapısının dijital ortamda modellenmesi",
    value: "Fiziksel karmaşa dijitalde sadeleşir",
    color: "from-violet-500 to-violet-600",
    bgColor: "bg-violet-50",
    iconColor: "text-violet-600"
  },
  {
    id: 4,
    icon: ClipboardList,
    title: "İş Emri Dijital İkizi",
    capability: "Her iş emrinin zaman, maliyet ve kaynak bazlı izlenmesi",
    value: "Gerçek maliyetler netleşir",
    color: "from-orange-500 to-orange-600",
    bgColor: "bg-orange-50",
    iconColor: "text-orange-600"
  },
  {
    id: 5,
    icon: Package,
    title: "Stok & Envanter Dijital İkizi",
    capability: "Yedek parça, sarf malzeme ve stok hareketlerinin canlı takibi",
    value: "Fazla stok ve kritik eksiklerin önüne geçilir",
    color: "from-cyan-500 to-cyan-600",
    bgColor: "bg-cyan-50",
    iconColor: "text-cyan-600"
  },
  {
    id: 6,
    icon: QrCode,
    title: "Barkod & QR Entegrasyonu",
    capability: "Parça–araç–iş emri ilişkisinin barkodla kurulması",
    value: "Manuel hata oranı düşer",
    color: "from-pink-500 to-pink-600",
    bgColor: "bg-pink-50",
    iconColor: "text-pink-600"
  },
  {
    id: 7,
    icon: Trash2,
    title: "Hurda Karar Mekanizması",
    capability: "Hurda tespit sürecinin dijital kayıt ve komisyon yapısı",
    value: "Şeffaf ve denetlenebilir karar alma",
    color: "from-red-500 to-red-600",
    bgColor: "bg-red-50",
    iconColor: "text-red-600"
  },
  {
    id: 8,
    icon: CheckCircle,
    title: "Kalite Kontrol Dijital Kayıtları",
    capability: "Yapılan işlemlerin kalite standartlarına göre izlenmesi",
    value: "Standart dışı işler erken yakalanır",
    color: "from-teal-500 to-teal-600",
    bgColor: "bg-teal-50",
    iconColor: "text-teal-600"
  },
  {
    id: 9,
    icon: Fuel,
    title: "Akaryakıt Dijital İkizi",
    capability: "Araç bazlı yakıt tüketiminin analiz edilmesi",
    value: "Yıllık yakıt maliyetlerinde ciddi tasarruf",
    color: "from-amber-500 to-amber-600",
    bgColor: "bg-amber-50",
    iconColor: "text-amber-600"
  },
  {
    id: 10,
    icon: BarChart3,
    title: "Garaj & Lokasyon Bazlı Analiz",
    capability: "Tatlıcak, Yazır, Meram, Alakova vb. lokasyon karşılaştırmaları",
    value: "Veriye dayalı yönetim",
    color: "from-indigo-500 to-indigo-600",
    bgColor: "bg-indigo-50",
    iconColor: "text-indigo-600"
  },
  {
    id: 11,
    icon: Timer,
    title: "Zaman & Performans Analitiği",
    capability: "Atölye, posta ve personel bazlı süre analizleri",
    value: "İş gücü verimliliği artar",
    color: "from-lime-500 to-lime-600",
    bgColor: "bg-lime-50",
    iconColor: "text-lime-600"
  },
  {
    id: 12,
    icon: FlaskConical,
    title: "Senaryo & Simülasyon",
    capability: '"Eğer bu araç şu atölyeye girseydi ne olurdu?" simülasyonları',
    value: "Stratejik karar desteği",
    color: "from-purple-500 to-purple-600",
    bgColor: "bg-purple-50",
    iconColor: "text-purple-600"
  },
  {
    id: 13,
    icon: FileText,
    title: "Raporlama & Görselleştirme",
    capability: "PDF, Excel ve yönetici panelleri",
    value: "Yöneticiye net, sade bilgi",
    color: "from-sky-500 to-sky-600",
    bgColor: "bg-sky-50",
    iconColor: "text-sky-600"
  },
  {
    id: 14,
    icon: Shield,
    title: "Yetkilendirme & Güvenlik",
    capability: "Rol bazlı erişim, kayıt ve loglama",
    value: "Kurumsal güvenlik",
    color: "from-slate-500 to-slate-600",
    bgColor: "bg-slate-50",
    iconColor: "text-slate-600"
  },
  {
    id: 15,
    icon: Blocks,
    title: "Modüler Mimari",
    capability: "İhtiyaca göre açılıp kapanabilen modüller",
    value: "Ölçeklenebilir yapı",
    color: "from-fuchsia-500 to-fuchsia-600",
    bgColor: "bg-fuchsia-50",
    iconColor: "text-fuchsia-600"
  },
  {
    id: 16,
    icon: Globe,
    title: "Platform Bağımsız Yapı",
    capability: "Belirli bir firmaya veya yazılıma bağımlı olmadan çalışır",
    value: "Kurum kontrolü elinde tutar",
    color: "from-rose-500 to-rose-600",
    bgColor: "bg-rose-50",
    iconColor: "text-rose-600"
  },
  {
    id: 17,
    icon: Rocket,
    title: "Dijital Dönüşüm Uyumu",
    capability: "TOM Dijital Dönüşüm Yol Haritası ile birebir uyum",
    value: "Sürdürülebilir dönüşüm",
    color: "from-gradient-500 to-blue-600",
    bgColor: "bg-gradient-to-r from-blue-50 to-purple-50",
    iconColor: "text-blue-600"
  }
];

// Feature Card Component
const FeatureCard = ({ feature, index }: { feature: typeof features[0]; index: number }) => {
  const [isHovered, setIsHovered] = useState(false);
  const Icon = feature.icon;

  return (
    <div
      className={`
        group relative overflow-hidden rounded-2xl bg-white p-6
        border border-gray-100 shadow-sm
        transition-all duration-500 ease-out
        hover:shadow-2xl hover:shadow-${feature.iconColor}/10
        hover:-translate-y-2 hover:border-transparent
        cursor-pointer
      `}
      style={{
        animationDelay: `${index * 50}ms`,
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Gradient overlay on hover */}
      <div
        className={`
          absolute inset-0 bg-gradient-to-br ${feature.color} opacity-0
          group-hover:opacity-5 transition-opacity duration-500
        `}
      />

      {/* Floating particles effect */}
      <div className="absolute top-0 right-0 w-32 h-32 opacity-0 group-hover:opacity-100 transition-opacity duration-700">
        <div className={`absolute top-4 right-4 w-2 h-2 rounded-full ${feature.bgColor} animate-ping`} />
        <div className={`absolute top-8 right-8 w-1.5 h-1.5 rounded-full ${feature.bgColor} animate-ping`} style={{ animationDelay: '0.2s' }} />
        <div className={`absolute top-6 right-12 w-1 h-1 rounded-full ${feature.bgColor} animate-ping`} style={{ animationDelay: '0.4s' }} />
      </div>

      {/* Icon */}
      <div className={`
        relative inline-flex items-center justify-center w-14 h-14 rounded-xl
        ${feature.bgColor} ${feature.iconColor}
        transition-all duration-500
        group-hover:scale-110 group-hover:rotate-3
        mb-4
      `}>
        <Icon size={28} strokeWidth={1.5} />

        {/* Glow effect */}
        <div className={`
          absolute inset-0 rounded-xl bg-gradient-to-br ${feature.color}
          opacity-0 group-hover:opacity-20 blur-xl transition-opacity duration-500
        `} />
      </div>

      {/* Title */}
      <h3 className="text-lg font-bold text-gray-900 mb-3 group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-gray-900 group-hover:to-gray-600 transition-all duration-300">
        {feature.title}
      </h3>

      {/* Capability */}
      <p className="text-sm text-gray-600 mb-4 leading-relaxed">
        {feature.capability}
      </p>

      {/* Value - appears on hover */}
      <div className={`
        flex items-start gap-2 p-3 rounded-xl
        ${feature.bgColor}
        transform transition-all duration-500
        ${isHovered ? 'opacity-100 translate-y-0' : 'opacity-70 translate-y-1'}
      `}>
        <Sparkles size={16} className={`${feature.iconColor} flex-shrink-0 mt-0.5`} />
        <p className={`text-sm font-medium ${feature.iconColor}`}>
          {feature.value}
        </p>
      </div>

      {/* Arrow indicator */}
      <div className={`
        absolute bottom-4 right-4 transform transition-all duration-300
        ${isHovered ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-2'}
      `}>
        <ChevronRight size={20} className={feature.iconColor} />
      </div>
    </div>
  );
};

// Stats Component
const Stats = () => {
  const stats = [
    { value: "17", label: "Dijital İkiz Modülü" },
    { value: "24", label: "Atölye Entegrasyonu" },
    { value: "7/24", label: "Gerçek Zamanlı İzleme" },
    { value: "%100", label: "Yerli Çözüm" },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-16">
      {stats.map((stat, index) => (
        <div
          key={index}
          className="text-center p-6 rounded-2xl bg-gradient-to-br from-white to-gray-50 border border-gray-100 shadow-sm hover:shadow-lg transition-shadow duration-300"
        >
          <div className="text-4xl font-black bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
            {stat.value}
          </div>
          <div className="text-sm text-gray-600 font-medium">
            {stat.label}
          </div>
        </div>
      ))}
    </div>
  );
};

// Main Component
export const TOMFeatures = () => {
  return (
    <section className="relative py-24 px-4 overflow-hidden bg-gradient-to-b from-gray-50 via-white to-gray-50">
      {/* Background decorations */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-100 rounded-full blur-3xl opacity-30" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-100 rounded-full blur-3xl opacity-30" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gradient-to-r from-blue-50 to-purple-50 rounded-full blur-3xl opacity-50" />
      </div>

      <div className="relative max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-blue-100 to-purple-100 text-blue-700 text-sm font-semibold mb-6">
            <Sparkles size={16} />
            <span>Dijital Dönüşümün Kalbi</span>
          </div>

          {/* Title */}
          <h2 className="text-4xl md:text-5xl font-black text-gray-900 mb-6">
            TOM Dijital İkiz
            <span className="block mt-2 bg-gradient-to-r from-blue-600 via-purple-600 to-blue-600 bg-clip-text text-transparent">
              Platform Yetkinlikleri
            </span>
          </h2>

          {/* Description */}
          <p className="max-w-3xl mx-auto text-lg text-gray-600 leading-relaxed">
            Araç, atölye, stok ve bakım süreçlerini sadece izleyen değil;{' '}
            <strong className="text-gray-900">anlayan, analiz eden ve yönetime karar desteği sunan</strong>{' '}
            akıllı bir yönetim altyapısı.
          </p>
        </div>

        {/* Stats */}
        <Stats />

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <FeatureCard key={feature.id} feature={feature} index={index} />
          ))}
        </div>

        {/* CTA Section */}
        <div className="mt-20 text-center">
          <div className="inline-flex flex-col sm:flex-row items-center gap-4">
            <button className="group relative px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold rounded-2xl shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/40 transition-all duration-300 hover:-translate-y-1">
              <span className="relative z-10 flex items-center gap-2">
                Demo Talep Et
                <ChevronRight size={20} className="group-hover:translate-x-1 transition-transform" />
              </span>
            </button>
            <button className="px-8 py-4 text-gray-700 font-bold rounded-2xl border-2 border-gray-200 hover:border-gray-300 hover:bg-gray-50 transition-all duration-300">
              Teknik Dokümanlar
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default TOMFeatures;
