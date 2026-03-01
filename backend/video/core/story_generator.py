"""
Story Generator - No Streamlit
Generate video scripts from niche/topic
"""
import logging
import json
from typing import Dict, Any, Optional
import random

logger = logging.getLogger(__name__)

class StoryGenerator:
    """Generate video scripts without Streamlit"""
    
    def __init__(self):
        self.templates = {
            'educational': {
                'hook': [
                    "Tahukah kamu bahwa {topic} itu penting?",
                    "Tips penting tentang {topic} yang wajib kamu tahu!",
                    "Inilah rahasia {topic} yang jarang diketahui"
                ],
                'body': [
                    "Pertama, pahami dasar-dasar {topic}. {fact1}",
                    "Kedua, praktikkan secara konsisten. {fact2}",
                    "Ketiga, evaluasi progressmu. {fact3}"
                ],
                'cta': [
                    "Yuk praktikkan sekarang!",
                    "Bagikan ke temanmu yang butuh info ini",
                    "Follow untuk tips {topic} lainnya"
                ]
            },
            'promotional': {
                'hook': [
                    "Promo spesial {product} hanya hari ini!",
                    "Jangan lewatkan kesempatan memiliki {product}",
                    "Yang kamu cari selama ini ada di sini!"
                ],
                'body': [
                    "{product} memiliki keunggulan: {feature1}",
                    "Cocok untuk kamu yang membutuhkan {feature2}",
                    "Dapatkan sekarang dengan harga spesial!"
                ],
                'cta': [
                    "Klik link di bio untuk order!",
                    "Hubungi kami sekarang sebelum kehabisan",
                    "Diskon 20% untuk 10 pembeli pertama!"
                ]
            },
            'engaging': {
                'hook': [
                    "Kamu pernah mengalami {problem}?",
                    "Ini dia solusi untuk {problem}!",
                    "Cara mudah mengatasi {problem}"
                ],
                'body': [
                    "Langkah pertama sangat mudah: {step1}",
                    "Selanjutnya, lakukan {step2}",
                    "Terakhir, pastikan {step3}"
                ],
                'cta': [
                    "Coba sekarang dan rasakan bedanya!",
                    "Share pengalamanmu di kolom komentar",
                    "Save video ini untuk panduan nanti"
                ]
            }
        }
        
        self.facts_pool = {
            'bisnis': [
                "80% kesuksesan bisnis datang dari konsistensi",
                "Modal terbesar adalah pengetahuan, bukan uang",
                "Pelanggan setia lebih berharga dari pelanggan baru",
                "Inovasi adalah kunci bertahan di persaingan"
            ],
            'teknologi': [
                "Teknologi berkembang sangat cepat setiap tahunnya",
                "AI akan mengubah cara kita bekerja",
                "Digitalisasi mempermudah semua aspek kehidupan",
                "Keamanan data menjadi prioritas utama"
            ],
            'kesehatan': [
                "Olahraga teratur meningkatkan produktivitas",
                "Tidur cukup penting untuk kesehatan otak",
                "Minum air putih minimal 8 gelas sehari",
                "Makanan bergizi seimbang untuk daya tahan tubuh"
            ]
        }
    
    async def generate_script(self, niche: str, style: str = 'educational', 
                            duration: int = 30) -> Dict[str, Any]:
        """Generate video script based on niche and style"""
        
        if style not in self.templates:
            style = 'educational'
            
        template = self.templates[style]
        
        # Get facts based on niche
        facts = self._get_facts(niche, 3)
        
        # Generate hook
        hook_template = random.choice(template['hook'])
        hook = hook_template.format(topic=niche, product=niche, problem=niche)
        
        # Generate body
        body_parts = []
        for i, body_template in enumerate(template['body']):
            if i < len(facts):
                fact = facts[i]
            else:
                fact = f"tips {niche} yang terbukti efektif"
                
            body = body_template.format(
                topic=niche, 
                product=niche,
                fact1=fact, fact2=fact, fact3=fact,
                feature1=fact, feature2=fact,
                step1=fact, step2=fact, step3=fact
            )
            body_parts.append(body)
        
        body = ' '.join(body_parts)
        
        # Generate CTA
        cta_template = random.choice(template['cta'])
        cta = cta_template.format(product=niche, topic=niche)
        
        # Combine full script
        full_script = f"{hook}\n\n{body}\n\n{cta}"
        
        # Estimate reading time (approx 3 words per second)
        word_count = len(full_script.split())
        estimated_duration = word_count / 3
        
        return {
            'hook': hook,
            'body': body,
            'cta': cta,
            'full_script': full_script,
            'style': style,
            'niche': niche,
            'estimated_duration': round(estimated_duration, 1),
            'word_count': word_count
        }
    
    def _get_facts(self, niche: str, count: int = 3) -> list:
        """Get facts related to niche"""
        niche_lower = niche.lower()
        
        # Find matching category
        category = 'bisnis'  # default
        for key in self.facts_pool:
            if key in niche_lower:
                category = key
                break
                
        facts = self.facts_pool.get(category, self.facts_pool['bisnis'])
        
        # Return random facts
        if len(facts) >= count:
            return random.sample(facts, count)
        else:
            return facts * (count // len(facts) + 1)[:count]
    
    async def generate_from_prompt(self, prompt: str) -> Dict[str, Any]:
        """Generate script from user prompt"""
        # Simple parsing - bisa di-upgrade pakai AI nanti
        words = prompt.lower().split()
        
        # Try to detect niche
        niche = "produk"  # default
        if len(words) > 3:
            niche = ' '.join(words[-3:])
        
        # Detect style
        style = 'educational'
        if any(word in prompt for word in ['jual', 'promo', 'diskon', 'murah']):
            style = 'promotional'
        elif any(word in prompt for word in ['tips', 'cara', 'tutorial']):
            style = 'educational'
        else:
            style = 'engaging'
        
        return await self.generate_script(niche, style)


story_generator = StoryGenerator()
